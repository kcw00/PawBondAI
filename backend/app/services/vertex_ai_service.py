from google import genai
from google.genai import types
from app.core.config import get_settings
from typing import List, Dict, Any
import base64


class VertexAIService:
    def __init__(self):
        settings = get_settings()
        # Initialize Google GenAI client with Vertex AI
        self.client = genai.Client(
            vertexai=True,
            project=settings.gcp_project_id,
            location=settings.vertex_ai_location
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for semantic search"""
        response = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """Analyze dog photo with Gemini Vision"""
        # Convert bytes to base64 for inline data
        import base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        full_prompt = f"""You are a veterinary assistant analyzing a dog photo.

{prompt}

Provide detailed observations about:
1. Visible health indicators
2. Breed characteristics (if identifiable)
3. Approximate age
4. Any visible conditions or concerns
5. Body condition score

Be specific but note that this is preliminary analysis only."""

        response = self.client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[
                full_prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg"
                )
            ]
        )
        return response.text


vertex_ai_service = VertexAIService()
