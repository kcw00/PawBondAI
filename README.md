# PawBondAI

AI-powered platform connecting rescue dogs with adopters and providing veterinary decision support for animal rescue organizations.

## 🎯 Problem & Solution

**The Challenge:** Animal rescue organizations struggle with:
- Matching the right dogs with the right adopters beyond basic filters
- Accessing veterinary expertise for medical decisions
- Learning from each other's experiences across different rescues

**Our Solution:** A RAG (Retrieval-Augmented Generation) system built on Elasticsearch that provides:
- **Semantic search** for intelligent dog-adopter matching based on behavioral and medical profiles
- **Veterinary knowledge base** with PDF document ingestion and chunked retrieval
- **Case study sharing network** with geo-based discovery for rescue collaboration

## 🔍 Key Technical Features

### 1. Semantic Search with Google Vertex AI Embeddings
- `semantic_text` fields for nuanced matching beyond keyword search
- Combined profile vectors for holistic dog-adopter compatibility
- Medical history and behavioral analysis through embeddings

### 2. Intelligent PDF Processing Pipeline
- Custom ingest pipeline for veterinary documents
- Automatic chunking for optimal retrieval
- Metadata preservation for source tracking

### 3. Geo-Aware Case Study Network
- `geo_point` indexing for finding nearby rescue organizations
- Visibility controls (private/network/public)
- Cross-rescue collaboration features

## 📊 Elasticsearch Architecture

### Three Core Indices

#### 1. **dogs** - Rescue Dog Profiles
Semantic search on medical history, behavioral notes, and combined profiles for intelligent matching.

<details>
<summary>View full schema</summary>

```json
PUT dogs
{
  "mappings": {
    "properties": {
      "dog_id": {"type": "keyword"},
      "name": {"type": "text"},
      "breed": {"type": "keyword"},
      "age": {"type": "integer"},
      "age_display": {"type": "keyword"},
      "weight_kg": {"type": "float"},
      "sex": {"type": "keyword"},
      "reproductive_status": {
        "properties": {
          "sterilized": {"type": "boolean"},
          "procedure": {"type": "keyword"},
          "date": {"type": "date"},
          "location": {"type": "text"}
        }
      },
      "rescue_date": {"type": "date"},
      "medical_history": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "current_conditions": {"type": "text"},
      "medications": {"type": "text"},
      "vaccinations": {
        "type": "nested",
        "properties": {
          "vaccine_name": {"type": "keyword"},
          "date_administered": {"type": "date"}
        }
      },
      "behavioral_notes": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "combined_profile": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "adoption_status": {"type": "keyword"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}
```
</details>

#### 2. **veterinary_knowledge** - RAG Knowledge Base
PDF documents chunked and embedded for precise veterinary information retrieval.

<details>
<summary>View full schema</summary>

```json
PUT veterinary_knowledge
{
  "mappings": {
    "properties": {
      "attachment": {
        "properties": {
          "title": {"type": "text"},
          "content_chunk": {
            "type": "semantic_text",
            "inference_id": "google_vertex_ai_embedding"
          }
        }
      },
      "filename": {"type": "keyword"},
      "chunk_number": {"type": "integer"},
      "total_chunks": {"type": "integer"},
      "source": {"type": "keyword"},
      "upload_date": {"type": "date"},
      "processed_date": {"type": "date"},
      "metadata": {
        "type": "object",
        "dynamic": true
      }
    }
  }
}
```
</details>

#### 3. **case_studies** - Rescue Network Knowledge Sharing
Real medical cases with semantic search, geo-discovery, and privacy controls.

<details>
<summary>View full schema</summary>

```json
PUT case_studies
{
  "mappings": {
    "properties": {
      "case_id": {"type": "keyword"},
      "title": {"type": "text"},
      "rescue_organization": {"type": "keyword"},
      "organization_contact": {"type": "keyword"},
      "date_published": {"type": "date"},
      "visibility": {"type": "keyword"},
      "is_shareable": {"type": "boolean"},
      "geographic_location": {"type": "geo_point"},
      "country": {"type": "keyword"},
      "region": {"type": "keyword"},
      "patient_species": {"type": "keyword"},
      "patient_breed": {"type": "keyword"},
      "patient_age_years": {"type": "integer"},
      "patient_age_months": {"type": "integer"},
      "patient_age_category": {"type": "keyword"},
      "patient_sex": {"type": "keyword"},
      "patient_weight_kg": {"type": "float"},
      "patient_weight_category": {"type": "keyword"},
      "is_juvenile": {"type": "boolean"},
      "is_geriatric": {"type": "boolean"},
      "presenting_complaint": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "clinical_history": {"type": "text"},
      "physical_examination": {"type": "text"},
      "diagnostic_tests": {"type": "text"},
      "diagnosis": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "treatment_plan": {"type": "text"},
      "outcome": {"type": "text"},
      "follow_up": {"type": "text"},
      "combined_case_text": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "learning_points": {"type": "text"},
      "tags": {"type": "keyword"},
      "disease_category": {"type": "keyword"},
      "urgency_level": {"type": "keyword"},
      "references": {"type": "text"},
      "estimated_cost": {"type": "float"},
      "cost_breakdown": {"type": "text"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}
```
</details>

## 🚀 Data Ingestion Pipeline

### PDF Document Processing
Veterinary documents are processed through a custom ingest pipeline:

<details>
<summary>View ingest pipeline configuration</summary>

```json
PUT _ingest/pipeline/pdf_pipeline
{
  "description": "Extract content from PDFs",
  "processors": [
    {
      "attachment": {
        "field": "data",
        "target_field": "attachment",
        "indexed_chars": -1,
        "properties": ["content", "title", "content_type", "language", "author", "date"]
      }
    },
    {
      "set": {
        "field": "processed_date",
        "value": "{{_ingest.timestamp}}"
      }
    },
    {
      "remove": {
        "field": "data"
      }
    }
  ]
}
```
</details>

### Bulk Data Upload
```bash
# Dog profiles and case studies
POST /dogs/_bulk
POST /case_studies/_bulk

# Veterinary PDFs (using custom ingestion script)
python scripts/pdf_ingestion.py
```

## 🛠️ Tech Stack
- **Elasticsearch** - Core search & analytics engine
- **Google Vertex AI** - Embedding generation
- **Python** - Data ingestion scripts
- **Kibana** - Index management