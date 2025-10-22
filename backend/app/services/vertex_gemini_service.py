# app/services/vertex_ai_service.py
from __future__ import annotations
from typing import Dict, Any, Optional
import json
import anyio

from google.auth import default as google_auth_default
from google.api_core import exceptions as gapi_exceptions

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class VertexGeminiService:
    """
    Unified Gemini service using Google Gen AI SDK in Vertex mode.
    - Text generation, analysis
    - Sentiment + entities
    - Medical data extraction
    """

    def __init__(self):
        # Log ADC identity so we know which SA needs roles
        creds, proj = google_auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        email = getattr(creds, "service_account_email", "(no-email)")
        logger.info(f"🔎 ADC identity for Vertex: {email} (project seen by ADC: {proj})")

        self.location = settings.vertex_ai_location
        self.project_id = settings.gcp_project_id
        self.model_id = settings.gemini_model

        # Gen AI client in Vertex mode (Python: google.genai)
        # See examples: init Client with vertexai=True, project, location.
        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
            # The Gen AI SDK uses ADC by default; creds can be injected via env/ADC.
        )

        logger.info(
            "✅ Google Gen AI client initialized "
            f"(vertex_mode, project={self.project_id}, location={self.location}, model={self.model_id})"
        )

    # ========================================
    # SENTIMENT & ENTITY ANALYSIS
    # ========================================
    async def analyze_sentiment_and_entities(self, text: str) -> Dict[str, Any]:
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
- sentiment.score: positive = 0.25..1.0, neutral = -0.25..0.25, negative = -1.0..-0.25
- sentiment.magnitude: emotional intensity (0.0 = none, 1.0 = moderate, 2.0+ = strong)
- entities: extract max 10 most salient
- themes: match keywords (previous dog, long-term, patient, active, work from home, family, training)
- commitment_score: high word count, positive sentiment, commitment phrases = higher score
- positive_indicators: count phrases like "long-term", "forever", "commitment", "dedicated", "patient"
- red_flags: count phrases like "easy", "cute", "instagram", "temporary", "try it out"
Return ONLY JSON (no markdown fences).
"""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            if self._is_region_not_found(e) and self.location != "us-central1":
                logger.warning("Retrying Gemini call in us-central1")
                try:
                    response = await self._generate_in_region_async(prompt, "us-central1")
                except Exception as e2:
                    logger.error(f"Retry in us-central1 failed: {e2}")
                    return self._fallback_sentiment_analysis(text)
            else:
                return self._fallback_sentiment_analysis(text)

        try:
            response_text = (response.text or "").strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]).strip()
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            analysis = json.loads(response_text)
            analysis["text_length"] = len(text.split())
            logger.info(f"Sentiment analysis complete: {analysis['sentiment']['interpretation']}")
            return analysis
        except Exception as e:
            logger.error(f"JSON parsing error in sentiment analysis: {e}")
            return self._fallback_sentiment_analysis(text)

    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        word_count = len(text.split())
        positive_words = [
            "love",
            "excited",
            "patient",
            "committed",
            "dedicated",
            "forever",
            "happy",
        ]
        negative_words = ["temporary", "easy", "instagram", "cute only"]
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        score = (pos_count - neg_count) / max(word_count, 1)
        score = max(-1.0, min(1.0, score))
        commitment_score = min(100, 50 + (word_count // 10) + (pos_count * 10) - (neg_count * 15))
        return {
            "sentiment": {
                "score": score,
                "magnitude": pos_count + neg_count,
                "interpretation": "Positive" if score > 0 else "Neutral/Mixed",
            },
            "entities": [],
            "themes": [],
            "commitment_assessment": {
                "commitment_score": commitment_score,
                "commitment_level": "Moderate" if commitment_score >= 50 else "Low",
                "word_count": word_count,
                "positive_indicators": pos_count,
                "red_flags": neg_count,
            },
            "text_length": word_count,
            "recommendation": "Proceed with Caution - Manual review required",
        }

    # ========================================
    # MEDICAL DATA EXTRACTION
    # ========================================
    async def extract_medical_data(
        self, medical_history_text: str, dog_name: str = "Unknown"
    ) -> Dict[str, Any]:
        prompt = f"""You are a veterinary data extraction expert. Analyze this medical history and extract structured data.

Dog Name: {dog_name}
Medical History:
{medical_history_text}

Return ONLY valid JSON (no markdown fences):
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
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            response_text = (response.text or "").strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]).strip()
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            extracted = json.loads(response_text)
            result = {
                "medical_events": extracted.get("medical_events", []),
                "past_conditions": extracted.get("past_conditions", []),
                "active_treatments": extracted.get("active_treatments", []),
                "severity_score": max(0, min(10, extracted.get("severity_score", 0))),
                "adoption_readiness": extracted.get("adoption_readiness", "ready"),
                "medical_summary": extracted.get("medical_summary", ""),
            }
            if result["adoption_readiness"] not in {"ready", "needs_treatment", "long_term_care"}:
                result["adoption_readiness"] = "ready"
            logger.info(f"Extracted medical data for {dog_name}: {result['adoption_readiness']}")
            return result
        except Exception as e:
            logger.error(f"Error extracting medical data: {e}")
            return self._fallback_medical_extraction(medical_history_text)

    def _fallback_medical_extraction(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        severity_keywords = {"critical": 10, "severe": 8, "moderate": 5, "minor": 2}
        severity_score = 0
        for k, v in severity_keywords.items():
            if k in text_lower:
                severity_score = max(severity_score, v)
        if any(w in text_lower for w in ["chronic", "permanent", "special needs"]):
            readiness = "long_term_care"
        elif any(w in text_lower for w in ["treatment", "medication", "recovering"]):
            readiness = "needs_treatment"
        else:
            readiness = "ready"
        return {
            "medical_events": [],
            "past_conditions": [],
            "active_treatments": [],
            "severity_score": severity_score,
            "adoption_readiness": readiness,
            "medical_summary": "Manual review required",
        }

    # ========================================
    # GENERAL TEXT GENERATION
    # ========================================
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        try:
            full_prompt = f"Context: {context}\n\n{prompt}" if context else prompt
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
            )
            return (response.text or "").strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, I'm having trouble processing your request right now."

    async def detect_intent(self, message: str) -> Dict[str, Any]:
        try:
            prompt = f"""Analyze this user message and determine the intent.

User message: "{message}"

Respond with JSON only:
{{
  "type": "find_adopters" | "analyze_application" | "general",
  "filters": {{}}
}}
"""
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            txt = (response.text or "").lower()
            if "find_adopters" in txt:
                return {"type": "find_adopters", "filters": {}}
            if "analyze_application" in txt or "analyze" in txt:
                return {"type": "analyze_application", "filters": {}}
            return {"type": "general", "filters": {}}
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return {"type": "general", "filters": {}}

    # ---------- helpers ----------
    def _is_region_not_found(self, e: Exception) -> bool:
        msg = str(e).lower()
        return (
            "not found" in msg
            and "publisher model" in msg
            or isinstance(e, gapi_exceptions.NotFound)
        )

    async def _generate_in_region_async(self, prompt: str, region: str):
        # Create a *temporary* client bound to a different region for retry
        temp_client = genai.Client(vertexai=True, project=self.project_id, location=region)
        return await temp_client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )


# Singleton instance
vertex_gemini_service = VertexGeminiService()
