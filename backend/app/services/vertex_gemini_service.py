from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
from PIL import Image
import io
import json
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class VertexGeminiService:
    """
    Unified Vertex AI Gemini service for all AI operations

    Capabilities:
    - Text generation (chat, analysis, recommendations)
    - Sentiment analysis & entity extraction
    - Medical data extraction
    - Vision analysis (dog photos)

    Uses Vertex AI (production-grade) instead of Google AI API (developer)
    """

    def __init__(self):
        # Initialize Vertex AI client
        self.client = genai.Client(
            vertexai=True,
            project=settings.gcp_project_id,
            location=settings.vertex_ai_location
        )

        # Models
        self.text_model = "gemini-1.5-flash"
        self.vision_model = "gemini-1.5-flash"

        logger.info("✅ Vertex AI Gemini client initialized")

    # ========================================
    # SENTIMENT & ENTITY ANALYSIS
    # ========================================

    async def analyze_sentiment_and_entities(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment and extract entities using Gemini

        Replaces Google Cloud Natural Language API with Gemini

        Returns:
            sentiment: score (-1 to 1), magnitude, interpretation
            entities: key entities with salience
            themes: extracted adoption themes
            commitment_assessment: commitment level analysis
        """
        try:
            prompt = f"""You are an expert at analyzing adoption application essays.

Analyze this adoption application motivation text:

{text}

Extract the following in JSON format:

{{
    "sentiment": {{
        "score": -1.0 to 1.0,
        "magnitude": 0.0+,
        "interpretation": "Highly Positive & Enthusiastic|Positive|Neutral/Mixed|Negative|Very Negative"
    }},
    "entities": [
        {{
            "name": "entity name",
            "type": "PERSON|LOCATION|ORGANIZATION|EVENT|WORK_OF_ART|CONSUMER_GOOD|OTHER",
            "salience": 0.0 to 1.0,
            "mentions": ["mention1", "mention2"]
        }}
    ],
    "themes": [
        "experienced_adopter|long_term_commitment|patient_personality|active_lifestyle|work_from_home|family_oriented|training_focus"
    ],
    "commitment_assessment": {{
        "commitment_score": 0-100,
        "commitment_level": "Very High|High|Moderate|Low|Very Low",
        "word_count": number,
        "positive_indicators": number,
        "red_flags": number
    }},
    "recommendation": "Highly Recommended|Recommended|Proceed with Caution|Not Recommended"
}}

RULES:
- sentiment.score: positive = 0.25 to 1.0, neutral = -0.25 to 0.25, negative = -1.0 to -0.25
- sentiment.magnitude: emotional intensity (0.0 = none, 1.0 = moderate, 2.0+ = strong)
- entities: extract max 10 most salient
- themes: match keywords (previous dog, long-term, patient, active, work from home, family, training)
- commitment_score: high word count, positive sentiment, commitment phrases = higher score
- positive_indicators: count phrases like "long-term", "forever", "commitment", "dedicated", "patient"
- red_flags: count phrases like "easy", "cute", "instagram", "temporary", "try it out"
"""

            response = self.client.models.generate_content(
                model=self.text_model,
                contents=prompt
            )

            # Parse JSON response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            analysis = json.loads(response_text)

            # Add original text length
            analysis["text_length"] = len(text.split())

            logger.info(f"Sentiment analysis complete: {analysis['sentiment']['interpretation']}")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in sentiment analysis: {e}")
            # Fallback to basic analysis
            return self._fallback_sentiment_analysis(text)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._fallback_sentiment_analysis(text)

    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword matching"""
        text_lower = text.lower()
        word_count = len(text.split())

        # Simple sentiment scoring
        positive_words = ["love", "excited", "patient", "committed", "dedicated", "forever", "happy"]
        negative_words = ["temporary", "easy", "instagram", "cute only"]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        score = (pos_count - neg_count) / max(len(text.split()), 1)
        score = max(-1.0, min(1.0, score))

        commitment_score = min(100, 50 + (word_count // 10) + (pos_count * 10) - (neg_count * 15))

        return {
            "sentiment": {
                "score": score,
                "magnitude": pos_count + neg_count,
                "interpretation": "Positive" if score > 0 else "Neutral/Mixed"
            },
            "entities": [],
            "themes": [],
            "commitment_assessment": {
                "commitment_score": commitment_score,
                "commitment_level": "Moderate" if commitment_score >= 50 else "Low",
                "word_count": word_count,
                "positive_indicators": pos_count,
                "red_flags": neg_count
            },
            "text_length": word_count,
            "recommendation": "Proceed with Caution - Manual review required"
        }

    # ========================================
    # MEDICAL DATA EXTRACTION
    # ========================================

    async def extract_medical_data(self, medical_history_text: str, dog_name: str = "Unknown") -> Dict[str, Any]:
        """
        Extract structured medical data from free-text medical history

        Args:
            medical_history_text: Natural language medical history
            dog_name: Name of the dog (for context)

        Returns:
            medical_events, past_conditions, active_treatments, severity_score, adoption_readiness
        """
        try:
            prompt = f"""You are a veterinary data extraction expert. Analyze this medical history and extract structured data.

Dog Name: {dog_name}
Medical History:
{medical_history_text}

Extract and return ONLY valid JSON (no markdown, no code blocks):

{{
    "medical_events": [
        {{
            "date": "YYYY-MM-DD or null if unknown",
            "event_type": "vaccination|surgery|diagnosis|treatment|checkup|injury|other",
            "condition": "specific condition name",
            "treatment": "treatment given or null",
            "severity": "mild|moderate|severe",
            "outcome": "resolved|ongoing|improved|worsened",
            "description": "brief description",
            "location": "body part/area affected or null"
        }}
    ],
    "past_conditions": ["condition1", "condition2"],
    "active_treatments": ["treatment1", "treatment2"],
    "severity_score": 0-10,
    "adoption_readiness": "ready|needs_treatment|long_term_care",
    "medical_summary": "one sentence summary"
}}

RULES:
- Extract ALL medical events chronologically
- past_conditions: only RESOLVED conditions
- active_treatments: only CURRENT/ONGOING treatments
- severity_score: 0=healthy, 5=moderate issues, 10=critical
- adoption_readiness: ready (healthy/minor resolved), needs_treatment (active treatment), long_term_care (chronic)
"""

            response = self.client.models.generate_content(
                model=self.text_model,
                contents=prompt
            )

            response_text = response.text.strip()

            # Remove markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            extracted_data = json.loads(response_text)

            # Validate and set defaults
            result = {
                "medical_events": extracted_data.get("medical_events", []),
                "past_conditions": extracted_data.get("past_conditions", []),
                "active_treatments": extracted_data.get("active_treatments", []),
                "severity_score": min(max(extracted_data.get("severity_score", 0), 0), 10),
                "adoption_readiness": extracted_data.get("adoption_readiness", "ready"),
                "medical_summary": extracted_data.get("medical_summary", "")
            }

            # Validate adoption_readiness
            if result["adoption_readiness"] not in ["ready", "needs_treatment", "long_term_care"]:
                result["adoption_readiness"] = "ready"

            logger.info(f"Extracted medical data for {dog_name}: {result['adoption_readiness']}")
            return result

        except Exception as e:
            logger.error(f"Error extracting medical data: {e}")
            return self._fallback_medical_extraction(medical_history_text)

    def _fallback_medical_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback medical extraction using keywords"""
        text_lower = text.lower()

        severity_keywords = {"critical": 10, "severe": 8, "moderate": 5, "minor": 2}
        severity_score = 0
        for keyword, score in severity_keywords.items():
            if keyword in text_lower:
                severity_score = max(severity_score, score)

        if any(word in text_lower for word in ["chronic", "permanent", "special needs"]):
            adoption_readiness = "long_term_care"
        elif any(word in text_lower for word in ["treatment", "medication", "recovering"]):
            adoption_readiness = "needs_treatment"
        else:
            adoption_readiness = "ready"

        return {
            "medical_events": [],
            "past_conditions": [],
            "active_treatments": [],
            "severity_score": severity_score,
            "adoption_readiness": adoption_readiness,
            "medical_summary": "Manual review required"
        }

    # ========================================
    # VISION ANALYSIS
    # ========================================

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """
        Analyze dog photo using Gemini Vision

        Args:
            image_bytes: Image data as bytes
            prompt: Analysis prompt/instructions

        Returns:
            Analysis text from Gemini Vision
        """
        try:
            # Build full prompt
            full_prompt = f"""You are a veterinary assistant analyzing a dog photo.

{prompt}

Provide detailed observations about:
1. Visible health indicators
2. Breed characteristics (if identifiable)
3. Approximate age
4. Any visible conditions or concerns
5. Body condition score

Be specific but note that this is preliminary analysis only."""

            # Generate content with vision model
            response = self.client.models.generate_content(
                model=self.vision_model,
                contents=[
                    full_prompt,
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    )
                ]
            )

            return response.text

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"

    # ========================================
    # GENERAL TEXT GENERATION
    # ========================================

    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate conversational response using Gemini

        Args:
            prompt: User's message or prompt
            context: Optional context

        Returns:
            Generated text response
        """
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\n{prompt}"

            response = self.client.models.generate_content(
                model=self.text_model,
                contents=full_prompt
            )

            return response.text

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, I'm having trouble processing your request right now."

    async def detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect user intent from message"""
        try:
            prompt = f"""Analyze this user message and determine the intent.

User message: "{message}"

Respond with JSON only:
{{
    "type": "find_adopters" | "analyze_application" | "general",
    "filters": {{}}
}}
"""

            response = self.client.models.generate_content(
                model=self.text_model,
                contents=prompt
            )

            # Simple parsing
            if "find_adopters" in response.text.lower():
                return {"type": "find_adopters", "filters": {}}
            elif "analyze" in response.text.lower():
                return {"type": "analyze_application", "filters": {}}
            else:
                return {"type": "general", "filters": {}}

        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return {"type": "general", "filters": {}}


# Singleton instance
vertex_gemini_service = VertexGeminiService()
