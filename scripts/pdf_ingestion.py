import base64
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
# Elastic Cloud settings
ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
INDEX_NAME = "veterinary_knowledge"
PIPELINE_NAME = "pdf_pipeline"
# Test connection first
try:
    headers = {
        "Authorization": f"ApiKey {ELASTIC_API_KEY}",
        "Content-Type": "application/json",
    }
    test_response = requests.get(ELASTIC_ENDPOINT, headers=headers, verify=True)
    print(f"✅ Connection test: {test_response.status_code}")
    if test_response.status_code == 401:
        print(" ❌ Authentication failed. Please check your API key.")
        import sys

        sys.exit(1)
except Exception as e:
    print(f" ❌ Connection test failed: {str(e)}")
    import sys

    sys.exit(1)


# Function to estimate token count
def estimate_tokens(text):
    # More accurate token estimation
    # Roughly 4 chars per token for English text, but this varies
    return len(text) // 4


# Function to clean content
def clean_content(text):
    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    return text


# Function to split text into chunks of approximately equal size
def chunk_text(text, max_tokens=10000):  # Reduced from 15000 to 10000
    # Clean the text first
    text = clean_content(text)

    # Rough approximation: 1 token ≈ 4 characters for English text
    max_chars = max_tokens * 4
    # Split into paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the limit, start a new chunk
        if len(current_chunk) + len(paragraph) > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    # Check if any chunks are still too large and split them further if needed
    final_chunks = []
    for chunk in chunks:
        if estimate_tokens(chunk) > 19000:  # Safe limit below 20000
            # If still too large, split by sentences
            sentences = re.split(r"(?<=[.!?])\s+", chunk)
            sub_chunk = ""
            for sentence in sentences:
                if estimate_tokens(sub_chunk + sentence) > 19000 and sub_chunk:
                    final_chunks.append(sub_chunk)
                    sub_chunk = sentence
                else:
                    if sub_chunk:
                        sub_chunk += " " + sentence
                    else:
                        sub_chunk = sentence
            if sub_chunk:
                final_chunks.append(sub_chunk)
        else:
            final_chunks.append(chunk)
    return final_chunks


# Directory containing PDF files
pdf_directory = "../data/vet_pdfs"
# Process each PDF file
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        file_path = os.path.join(pdf_directory, filename)
        try:
            # Read as binary and encode to base64
            with open(file_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                # Check if it's a valid PDF
                if not pdf_bytes.startswith(b"%PDF"):
                    print(
                        f" ⚠️ Warning: {filename} doesn't appear to be a valid PDF. Skipping."
                    )
                    continue
                encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            # Use the simulate endpoint to extract content
            simulate_body = {
                "pipeline": {
                    "description": "Extract content from PDFs",
                    "processors": [
                        {
                            "attachment": {
                                "field": "data",
                                "target_field": "attachment",
                                "indexed_chars": -1,
                                "remove_binary": True,
                                "properties": [
                                    "content",
                                    "title",
                                    "content_type",
                                    "language",
                                    "author",
                                    "date",
                                ],
                            }
                        }
                    ],
                },
                "docs": [{"_source": {"filename": filename, "data": encoded_pdf}}],
            }
            print(f"Extracting content from {filename}...")
            simulate_response = requests.post(
                f"{ELASTIC_ENDPOINT}/_ingest/pipeline/_simulate",
                headers=headers,
                data=json.dumps(simulate_body),
                verify=True,
            )
            if simulate_response.status_code == 200:
                # Check if there was an error in the simulation
                if "error" in simulate_response.json()["docs"][0]:
                    print(
                        f"Error extracting content from {filename}: {simulate_response.json()['docs'][0]['error']}"
                    )
                    continue
                # Get the extracted content
                processed_doc = simulate_response.json()["docs"][0]["doc"]["_source"]
                title = processed_doc.get("attachment", {}).get("title", filename)
                content = processed_doc.get("attachment", {}).get("content", "")
                # Chunk the content
                content_chunks = chunk_text(content)
                total_chunks = len(content_chunks)
                print(f"Processing {filename}: {total_chunks} chunks")
                # Index each chunk to the main index
                for i, chunk in enumerate(content_chunks):
                    # Verify token count before sending
                    estimated_tokens = estimate_tokens(chunk)
                    if estimated_tokens > 19000:
                        print(
                            f"  ⚠️ Warning: Chunk {i+1} has estimated {estimated_tokens} tokens, which may exceed limits"
                        )
                        continue

                    chunk_document = {
                        "filename": filename,
                        "chunk_number": i + 1,
                        "total_chunks": total_chunks,
                        "attachment": {"title": title, "content_chunk": chunk},
                        "source": "medical_article",
                        "upload_date": datetime.now().isoformat(),
                        "metadata": {
                            "ingestion_type": "batch",
                            "category": "veterinary_medicine",
                        },
                    }
                    try:
                        # Index the chunk
                        chunk_response = requests.post(
                            f"{ELASTIC_ENDPOINT}/{INDEX_NAME}/_doc",
                            headers=headers,
                            data=json.dumps(chunk_document),
                            verify=True,
                        )
                        print(
                            f"  Chunk {i+1}/{total_chunks}: Status {chunk_response.status_code}"
                        )
                        if chunk_response.status_code >= 400:
                            print(f"  Error details: {chunk_response.text}")
                    except Exception as e:
                        print(f"  ❌ Exception while indexing chunk {i+1}: {str(e)}")
            else:
                print(
                    f" ❌ Failed to simulate pipeline for {filename}: {simulate_response.status_code}"
                )
                print(simulate_response.text)
        except Exception as e:
            print(f" ❌ Error processing {filename}: {str(e)}")
            print(f" ❌ Unexpected error: {str(e)}")
