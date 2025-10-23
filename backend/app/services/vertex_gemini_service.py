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
    # SEARCH RESULT FORMATTING
    # ========================================
    async def format_search_results(
        self,
        query: str,
        search_results: Dict[str, Any],
        search_type: str = "adopters"
    ) -> str:
        """
        Format Elasticsearch search results into natural language using Gemini.

        Args:
            query: The original user query
            search_results: Raw Elasticsearch results with hits array
            search_type: Type of search ("adopters" or "dogs")

        Returns:
            Natural language formatted response
        """
        hits = search_results.get("hits", [])

        if not hits:
            if search_type == "adopters":
                return "I couldn't find any matching adopters for your search. Try broadening your criteria or being more specific about what you're looking for."
            else:
                return "I couldn't find any matching dogs. Try adjusting your search criteria."

        # Prepare data for Gemini
        matches_summary = []
        for i, hit in enumerate(hits[:5], 1):  # Top 5 for context
            source = hit.get("_source", {})
            score = hit.get("_score", 0)

            if search_type == "adopters":
                matches_summary.append({
                    "rank": i,
                    "name": source.get("applicant_name", "Unknown"),
                    "score": round(score, 3),
                    "location": f"{source.get('city', '')}, {source.get('state', '')}".strip(", "),
                    "housing": source.get("housing_type", ""),
                    "motivation": source.get("motivation", "")[:200],  # First 200 chars
                    "experience": source.get("experience_level", ""),
                    "employment": source.get("employment_status", ""),
                })
            else:
                matches_summary.append({
                    "rank": i,
                    "name": source.get("name", "Unknown"),
                    "score": round(score, 3),
                    "breed": source.get("breed", ""),
                    "age": source.get("age", ""),
                    "personality": source.get("personality_traits", "")[:200],
                })

        prompt = f"""You are a helpful rescue coordinator AI assistant. A user searched for: "{query}"

I found {len(hits)} matching {search_type} using Elasticsearch semantic search. Here are the top {len(matches_summary)} matches:

{json.dumps(matches_summary, indent=2)}

Write a friendly, conversational response (2-3 sentences) that:
1. Confirms how many matches were found
2. Highlights what makes the top matches relevant to the query
3. Encourages the user to review the detailed match cards

Be warm and helpful. Don't repeat the technical data - that will be shown in cards below your message.
Don't use markdown formatting. Keep it natural and conversational.
"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            formatted_response = (response.text or "").strip()
            logger.info(f"Formatted search results with Gemini for query: {query}")
            return formatted_response
        except Exception as e:
            logger.error(f"Error formatting search results with Gemini: {e}")
            # Fallback to simple message
            if search_type == "adopters":
                return f"Found {len(hits)} matching adopters based on your search. Check out the top matches below!"
            else:
                return f"Found {len(hits)} matching dogs. Take a look at these great matches!"

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
            prompt = f"""Analyze this user message and determine the intent and extract any structured filters.

User message: "{message}"

Respond with ONLY valid JSON (no markdown fences):
{{
  "type": "find_adopters" | "analyze_application" | "general",
  "filters": {{
    "has_yard": true|false|null,
    "yard_size_min": number|null,
    "experience_levels": ["First-time owner", "Some experience", "Experienced", "Professional (Vet/Trainer)"]|null,
    "housing_types": ["House", "Apartment", "Townhouse", "Condo"]|null,
    "has_other_pets": true|false|null,
    "behavioral_keywords": ["anxious", "calm", "energetic", "shy", "friendly"]|null
  }}
}}

RULES:
- type: "find_adopters" if searching for adopters/applicants, "analyze_application" if analyzing specific application text, "general" otherwise
- has_yard: true if query mentions "yard", "garden", "outdoor space", "large property"; false if "no yard", "apartment"; null otherwise
- yard_size_min: extract minimum square meters if mentioned (convert: small=50, medium=150, large=300); null otherwise
- experience_levels: extract if query mentions "experienced", "first-time", "professional", "novice", etc.; null otherwise
- housing_types: extract if query specifies house type; null otherwise
- has_other_pets: true if "multi-pet", "other pets", "other dogs/cats"; false if "no other pets"; null otherwise
- behavioral_keywords: extract keywords related to dog behavior/personality that adopter should handle (anxious, aggressive, shy, energetic, etc.)

Examples:
- "Find experienced adopters with large yards" -> {{"type": "find_adopters", "filters": {{"experience_levels": ["Experienced", "Professional (Vet/Trainer)"], "yard_size_min": 300}}}}
- "Find adopters good with anxious dogs" -> {{"type": "find_adopters", "filters": {{"behavioral_keywords": ["anxious"]}}}}
- "Analyze this application" -> {{"type": "analyze_application", "filters": {{}}}}
"""
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            response_text = (response.text or "").strip()

            # Clean markdown fences if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]).strip()
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Parse JSON response
            result = json.loads(response_text)

            # Validate and set defaults
            if "type" not in result:
                result["type"] = "general"
            if "filters" not in result:
                result["filters"] = {}

            logger.info(f"Intent detected: {result['type']}, filters: {result['filters']}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in detect_intent: {e}")
            # Fallback to simple keyword detection
            message_lower = message.lower()
            if any(word in message_lower for word in ["find", "search", "show me", "get me", "adopters", "applicants"]):
                return {"type": "find_adopters", "filters": {}}
            elif any(word in message_lower for word in ["analyze", "review", "evaluate", "application"]):
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
