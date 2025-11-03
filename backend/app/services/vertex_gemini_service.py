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
        creds, proj = google_auth_default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        email = getattr(creds, "service_account_email", "(no-email)")
        logger.info(
            f"🔎 ADC identity for Vertex: {email} (project seen by ADC: {proj})"
        )

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
                    response = await self._generate_in_region_async(
                        prompt, "us-central1"
                    )
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
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )

            analysis = json.loads(response_text)
            analysis["text_length"] = len(text.split())
            logger.info(
                f"Sentiment analysis complete: {analysis['sentiment']['interpretation']}"
            )
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
        commitment_score = min(
            100, 50 + (word_count // 10) + (pos_count * 10) - (neg_count * 15)
        )
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
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )

            extracted = json.loads(response_text)
            result = {
                "medical_events": extracted.get("medical_events", []),
                "past_conditions": extracted.get("past_conditions", []),
                "active_treatments": extracted.get("active_treatments", []),
                "severity_score": max(0, min(10, extracted.get("severity_score", 0))),
                "adoption_readiness": extracted.get("adoption_readiness", "ready"),
                "medical_summary": extracted.get("medical_summary", ""),
            }
            if result["adoption_readiness"] not in {
                "ready",
                "needs_treatment",
                "long_term_care",
            }:
                result["adoption_readiness"] = "ready"
            logger.info(
                f"Extracted medical data for {dog_name}: {result['adoption_readiness']}"
            )
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
        self, query: str, search_results: Dict[str, Any], search_type: str = "adopters"
    ) -> str:
        """
        Format Elasticsearch search results into natural language using Gemini.
        Also generates individual match reasons for each result.

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
                # Use translated motivation if available (for multilingual support)
                motivation_text = source.get(
                    "translated_motivation", source.get("motivation", "")
                )[:300]  # Increased from 200 to 300 for better context
                language_info = (
                    f" [Original: {source.get('language_name', 'English')}]"
                    if source.get("original_language", "en") != "en"
                    else ""
                )

                matches_summary.append(
                    {
                        "rank": i,
                        "name": source.get("applicant_name", "Unknown") + language_info,
                        "score": round(score, 3),
                        "location": f"{source.get('city', '')}, {source.get('state', '')}".strip(
                            ", "
                        ),
                        "housing": source.get("housing_type", ""),
                        "motivation": motivation_text,  # Translated if non-English
                        "experience": source.get("experience_level", ""),
                        "employment": source.get("employment_status", ""),
                        "has_yard": source.get("has_yard", False),
                        "yard_size": source.get("yard_size", ""),
                        "other_pets": source.get("other_pets_description", ""),
                    }
                )
            else:
                matches_summary.append(
                    {
                        "rank": i,
                        "name": source.get("name", "Unknown"),
                        "score": round(score, 3),
                        "breed": source.get("breed", ""),
                        "age": source.get("age", ""),
                        "personality": source.get("personality_traits", "")[:200],
                    }
                )

        # Generate individual match reasons for each result
        reasons_prompt = f"""You are an expert adoption coordinator. Analyze why each adopter is a GOOD match for the search query.

User query: "{query}"

Top matches from Elasticsearch semantic search:
{json.dumps(matches_summary, indent=2)}

IMPORTANT: These adopters were ALREADY matched by our semantic search algorithm. Your job is to explain WHY they are good matches.

For EACH match, write a positive, concise 1-2 sentence explanation of WHY they are a good match for this query. Focus on:
- What specific factors from their profile align with the query requirements
- Their relevant experience, housing situation, motivation, or lifestyle strengths
- What makes them well-suited for this specific request

Return ONLY valid JSON (no markdown fences):
{{
  "match_reasons": [
    {{
      "rank": 1,
      "name": "adopter name",
      "reason": "Positive explanation of why they match (1-2 sentences)"
    }},
    ...
  ]
}}

RULES:
- These are PRE-FILTERED matches - focus on POSITIVE reasons why they fit
- Reference concrete details from their profile (housing, experience, motivation, employment)
- Keep each reason to 1-2 sentences
- Be specific and constructive
- Do NOT say things like "profile is empty" or "doesn't meet criteria" - if they're in the results, they DO match
- Focus on what makes them SUITABLE, not unsuitable
"""

        try:
            # Generate match reasons
            reasons_response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=reasons_prompt,
            )
            reasons_text = (reasons_response.text or "").strip()

            # Clean markdown fences
            if reasons_text.startswith("```"):
                lines = reasons_text.split("\n")
                reasons_text = "\n".join(lines[1:-1]).strip()
            reasons_text = reasons_text.replace("```json", "").replace("```", "").strip()

            # Parse match reasons
            reasons_data = json.loads(reasons_text)
            match_reasons = reasons_data.get("match_reasons", [])

            # Add reasons back to the original hits
            for hit in hits:
                source = hit.get("_source", {})
                applicant_name = source.get("applicant_name", "")

                # Find the matching reason
                for reason_entry in match_reasons:
                    if reason_entry.get("name", "").lower() in applicant_name.lower() or \
                       applicant_name.lower() in reason_entry.get("name", "").lower():
                        hit["match_reason"] = reason_entry.get("reason", "Good match based on profile similarity")
                        break

                # Fallback if no reason found
                if "match_reason" not in hit:
                    hit["match_reason"] = "Matches your search criteria based on their profile and motivation"

            logger.info(f"Generated match reasons for {len(match_reasons)} adopters")

        except Exception as e:
            logger.error(f"Error generating match reasons: {e}")
            # Fallback: add generic reasons
            for hit in hits:
                if "match_reason" not in hit:
                    hit["match_reason"] = "Strong match based on their application profile and experience"

        # Generate overall summary
        prompt = f"""You are a helpful rescue coordinator AI assistant. A user searched for: "{query}"

I found {len(hits)} matching {search_type} using Elasticsearch semantic search with multilingual support. Here are the top {len(matches_summary)} matches:

{json.dumps(matches_summary, indent=2)}

Note: Applications marked with [Original: Language] were submitted in that language and automatically translated for you.

Write a friendly, conversational response (2-3 sentences) that:
1. Confirms how many matches were found
2. Highlights what makes the top matches relevant to the query (e.g., "experienced adopters with yards" or "work-from-home applicants")
3. If any matches are from non-English applications, briefly mention the multilingual capability
4. Encourages the user to review the detailed match cards below, where EACH card includes a specific explanation of why that adopter is a good fit

IMPORTANT: Each match card below will have its own detailed "Why this match?" explanation, so you don't need to explain individual adopters. Focus on the overall findings.

Be warm, confident, and helpful. Don't say things like "unable to provide details" - the details ARE provided in each match card.
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
    # TRANSLATION
    # ========================================
    async def translate_text(
        self,
        text: str,
        target_language: str = "English",
        source_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Translate text using Gemini's multilingual capabilities.

        Args:
            text: The text to translate
            target_language: Target language name (e.g., "English", "Spanish", "Korean", "Chinese")
            source_language: Source language (if None, will auto-detect)

        Returns:
            Dictionary with translated_text, source_language, target_language
        """
        source_lang_prompt = (
            f"from {source_language}"
            if source_language
            else "(detect the source language)"
        )

        prompt = f"""You are a professional translator specializing in animal welfare and adoption documentation.

Translate the following text {source_lang_prompt} to {target_language}.

Text to translate:
{text}

Return ONLY valid JSON (no markdown fences):
{{
  "translated_text": "the translated text here",
  "source_language": "detected or provided source language",
  "target_language": "{target_language}",
  "confidence": 0.0-1.0
}}

RULES:
- Preserve all technical terms, medical conditions, and proper nouns appropriately
- Maintain the tone and meaning of the original text
- For animal welfare context: keep professional and compassionate tone
- If text is already in target language, return it as-is with confidence 1.0
"""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            response_text = (response.text or "").strip()

            # Clean markdown fences
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]).strip()
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )

            result = json.loads(response_text)
            logger.info(
                f"Translation complete: {result.get('source_language', 'unknown')} -> {target_language}"
            )
            return result

        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {
                "translated_text": text,
                "source_language": source_language or "unknown",
                "target_language": target_language,
                "confidence": 0.0,
                "error": str(e),
            }

    # ========================================
    # BATCH TRANSLATION FOR RAG
    # ========================================
    async def batch_translate_to_english(
        self,
        items: list[Dict[str, Any]],
        text_field: str = "text",
        language_field: str = "language",
    ) -> list[Dict[str, Any]]:
        """
        Batch translate multiple documents to English for RAG pipeline.
        Only translates non-English documents; preserves English documents as-is.

        Args:
            items: List of documents with text and language fields
            text_field: Field name containing the text to translate
            language_field: Field name containing the language code

        Returns:
            List of documents with translated text in 'translated_text' field
        """
        try:
            # Separate English and non-English items
            english_items = []
            non_english_items = []

            for item in items:
                lang = item.get(language_field, "en")
                if lang == "en" or not lang:
                    # Keep English items as-is
                    item["translated_text"] = item.get(text_field, "")
                    item["translation_needed"] = False
                    english_items.append(item)
                else:
                    item["translation_needed"] = True
                    non_english_items.append(item)

            if not non_english_items:
                logger.info("All items are in English, no translation needed")
                return items

            logger.info(
                f"Translating {len(non_english_items)} items to English (keeping {len(english_items)} English items)"
            )

            # Batch translation prompt
            batch_texts = []
            for idx, item in enumerate(non_english_items):
                text = item.get(text_field, "")
                lang = item.get(language_field, "unknown")
                batch_texts.append(f"[ITEM_{idx}] ({lang}):\n{text}\n")

            prompt = f"""Translate the following documents to English. Each document is marked with [ITEM_N].
Return the translations in the same order, using the same [ITEM_N] markers.

Documents:
{chr(10).join(batch_texts)}

RULES:
- Preserve the meaning and context accurately
- Keep proper nouns (names, places) unchanged
- Maintain the same formatting and structure
- Return ONLY the translated text for each item with its [ITEM_N] marker
- Do not add explanations or comments

Format:
[ITEM_0]
<translated text>

[ITEM_1]
<translated text>
"""

            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )

            response_text = (response.text or "").strip()

            # Parse the batch response
            import re

            item_pattern = r"\[ITEM_(\d+)\]\s*\n(.*?)(?=\[ITEM_|\Z)"
            matches = re.findall(item_pattern, response_text, re.DOTALL)

            # Map translations back to items
            for match in matches:
                idx = int(match[0])
                translated = match[1].strip()
                if idx < len(non_english_items):
                    non_english_items[idx]["translated_text"] = translated

            # Fallback: if parsing failed, translate one-by-one
            for item in non_english_items:
                if "translated_text" not in item:
                    logger.warning(
                        f"Batch translation failed for item, falling back to individual translation"
                    )
                    text = item.get(text_field, "")
                    lang = item.get(language_field, "unknown")
                    individual_result = await self.translate_text(
                        text, target_language="English", source_language=lang
                    )
                    item["translated_text"] = individual_result.get(
                        "translated_text", text
                    )

            # Combine and return
            all_items = english_items + non_english_items
            logger.info(
                f"Batch translation complete: {len(non_english_items)} items translated"
            )
            return all_items

        except Exception as e:
            logger.error(f"Error in batch translation: {e}")
            # Fallback: mark all as untranslated
            for item in items:
                if "translated_text" not in item:
                    item["translated_text"] = item.get(text_field, "")
            return items

    # ========================================
    # APPLICATION SUMMARY FORMATTING
    # ========================================
    async def format_application_summary(self, application_text: str) -> str:
        """
        Extract structured information from an adoption application and format it
        in a clean, ChatGPT-style summary format.

        Args:
            application_text: The raw adoption application text

        Returns:
            Formatted markdown summary of the application
        """
        prompt = f"""You are an expert adoption coordinator. Analyze this adoption application and create a comprehensive, well-structured summary.

Application Text:
{application_text}

Create a professional summary in markdown format with the following structure:

## Applicant Summary: [Extract Applicant Name]

**Status:** Pending
**Submitted:** [Today's date in format "Month DD, YYYY, at HH:MM AM/PM"]
**Email:** [Extract email if present, otherwise use "Not provided"]

## 📋 Applicant Overview

[Write a comprehensive 2-3 sentence overview of the applicant, summarizing their motivation, living situation, experience, and what makes them a good fit for adopting a rescue animal.]

## 🏡 Living Situation

- **Residence Type:** [Extract: House/Apartment/Townhouse/Condo/Other]
- **Yard:** [Yes with size if mentioned, or No]
- **Other Pets:** [Yes - list types, or None]
- **Household Members:** [Number of people, ages if mentioned]
- **Home Ownership:** [Own/Rent/Other]

## 💼 Work & Lifestyle

- **Employment Status:** [Work from home/Office worker/Remote/Retired/etc.]
- **Daily Schedule:** [Brief description of their typical day and time available for a dog]
- **Activity Level:** [Active/Moderate/Low - based on their description]

## 🐕 Experience & Preferences

- **Dog Experience:** [Describe their previous experience with dogs]
- **Training Experience:** [Any mention of training knowledge]
- **Preferred Dog Type:** [Size, age, temperament preferences if mentioned]
- **Special Accommodations:** [Any mention of ability to handle special needs, medical issues, behavioral challenges]

## ⭐ Motivation & Commitment

[Quote or summarize the most compelling parts of their motivation. Highlight commitment indicators like "long-term", "forever home", "family member", etc.]

## ❗ Important Considerations

[List any important points that require follow-up, potential concerns, or standout positive factors. If everything looks good, note "No concerns identified - strong application"]

RULES:
- Extract information accurately from the text
- If information is not provided, write "Not specified" rather than making assumptions
- Keep the tone professional but warm
- Use emojis only in section headers (as shown above)
- If the applicant name is not found, use "Applicant"
- Format all sections consistently
- Focus on facts from the application, not speculation
- Highlight both strengths and any areas needing clarification"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            formatted_summary = (response.text or "").strip()
            logger.info("Generated formatted application summary")
            return formatted_summary
        except Exception as e:
            logger.error(f"Error formatting application summary: {e}")
            # Fallback to basic format
            return f"""## Applicant Summary

**Status:** Pending

## 📋 Application Text

{application_text[:500]}...

*Note: Auto-formatting unavailable. Please review the full text above.*"""

    # ========================================
    # GENERAL TEXT GENERATION
    # ========================================
    async def generate_response(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
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

    async def generate_applicant_details(
        self, query: str, applicant_data: Dict[str, Any]
    ) -> str:
        """
        Generate detailed information about a specific applicant based on their full data.
        Uses the same ChatGPT-style format as format_application_summary.

        Args:
            query: User's question about the applicant
            applicant_data: Full applicant data from Elasticsearch

        Returns:
            Natural language response with applicant details in structured format
        """
        prompt = f"""You are an expert adoption coordinator. A user is asking about a specific applicant from your database.

User question: "{query}"

Applicant data from database:
{json.dumps(applicant_data, indent=2)}

Create a professional summary in markdown format with the following structure:

# Applicant Summary: {applicant_data.get('applicant_name', 'Applicant')}

**Status:** {applicant_data.get('status', 'Pending')}
**Submitted:** {applicant_data.get('submitted_at', 'Date not available')}
**Email:** {applicant_data.get('email', 'Not provided')}

## Applicant Overview

[Write a comprehensive 2-3 sentence overview of the applicant, summarizing their motivation, living situation, experience, and what makes them a good fit for adopting a rescue animal.]

## Living Situation

- **Residence Type:** {applicant_data.get('housing_type', 'Not specified')}
- **Yard:** [Extract from has_yard field: Yes/No, include yard_size if available]
- **Other Pets:** [Extract from has_other_pets and other_pets_description]
- **Household Members:** [Extract from family_members or household_size]
- **Home Ownership:** [Extract from housing_ownership or infer]

## Work & Lifestyle

- **Employment Status:** {applicant_data.get('employment_status', 'Not specified')}
- **Daily Schedule:** [Describe their schedule and availability based on employment and other fields]
- **Activity Level:** [Infer from lifestyle, preferences, or work situation]

## Experience & Preferences

- **Dog Experience:** {applicant_data.get('experience_level', 'Not specified')}
- **Training Experience:** [Extract from previous_dog or training-related fields]
- **Preferred Dog Type:** [Extract from preferences if available]
- **Special Accommodations:** [Extract from behavioral preferences or special needs mentions]

## Motivation & Commitment

{applicant_data.get('motivation', 'Not provided')[:500]}

[Add analysis: Highlight commitment indicators like "long-term", "forever home", "family member" if present in the motivation text]

## Important Considerations

[Based on all the data, list:
1. Key strengths (2-3 points)
2. Any areas needing follow-up or clarification
3. Overall assessment: "Strong candidate" / "Recommended for interview" / "Needs additional review"]

RULES:
- Extract information accurately from the provided data
- If a field is missing or null, write "Not specified"
- Keep the tone professional but warm
- Use emojis only in section headers (as shown above)
- Format all sections consistently
- Highlight both strengths and any areas needing clarification
- If the user's question was specific, ensure you address it in your response"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            result = (response.text or "").strip()
            logger.info(f"Generated applicant details for query: {query}")
            return result
        except Exception as e:
            logger.error(f"Error generating applicant details: {e}")
            # Fallback: create a simple formatted response
            name = applicant_data.get("applicant_name", "Unknown")
            location = f"{applicant_data.get('city', '')}, {applicant_data.get('state', '')}".strip(
                ", "
            )
            housing = applicant_data.get("housing_type", "Not specified")
            experience = applicant_data.get("experience_level", "Not specified")
            motivation = applicant_data.get("motivation", "Not provided")[:300]
            email = applicant_data.get("email", "Not provided")
            submitted = applicant_data.get("submitted_at", "Date not available")

            return f"""# Applicant Summary: {name}

**Status:** Pending
**Submitted:** {submitted}
**Email:** {email}

## Applicant Overview

{name} has submitted an application to adopt a rescue dog. They are located in {location} and live in a {housing}.

## Living Situation

- **Residence Type:** {housing}
- **Location:** {location}
- **Experience Level:** {experience}

## Motivation & Commitment

{motivation}...

*Note: Full database details available. This is a simplified view due to processing limitations.*"""

    async def detect_intent(self, message: str) -> Dict[str, Any]:
        try:
            prompt = f"""Analyze this user message and determine the intent and extract any structured filters.

User message: "{message}"

Respond with ONLY valid JSON (no markdown fences):
{{
  "type": "find_adopters" | "analyze_application" | "general",
  "limit": number|null,
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
- limit: extract the number of results requested (e.g., "top 3", "best 5", "find 10"); null if not specified (defaults to 5)
- has_yard: true if query mentions "yard", "garden", "outdoor space", "large property"; false if "no yard", "apartment"; null otherwise
- yard_size_min: extract minimum square meters if mentioned (convert: small=50, medium=150, large=300); null otherwise
- experience_levels: extract if query mentions "experienced", "first-time", "professional", "novice", etc.; null otherwise
- housing_types: extract if query specifies house type; null otherwise
- has_other_pets: true if "multi-pet", "other pets", "other dogs/cats"; false if "no other pets"; null otherwise
- behavioral_keywords: extract keywords related to dog behavior/personality that adopter should handle (anxious, aggressive, shy, energetic, etc.)

Examples:
- "Find top 3 adopters for Rocky" -> {{"type": "find_adopters", "limit": 3, "filters": {{}}}}
- "Find experienced adopters with large yards" -> {{"type": "find_adopters", "limit": null, "filters": {{"experience_levels": ["Experienced", "Professional (Vet/Trainer)"], "yard_size_min": 300}}}}
- "Find adopters good with anxious dogs" -> {{"type": "find_adopters", "limit": null, "filters": {{"behavioral_keywords": ["anxious"]}}}}
- "Show me best 5 matches" -> {{"type": "find_adopters", "limit": 5, "filters": {{}}}}
- "Analyze this application" -> {{"type": "analyze_application", "limit": null, "filters": {{}}}}
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
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )

            # Parse JSON response
            result = json.loads(response_text)

            # Validate and set defaults
            if "type" not in result:
                result["type"] = "general"
            if "filters" not in result:
                result["filters"] = {}

            logger.info(
                f"Intent detected: {result['type']}, filters: {result['filters']}"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in detect_intent: {e}")
            # Fallback to simple keyword detection
            message_lower = message.lower()
            if any(
                word in message_lower
                for word in [
                    "find",
                    "search",
                    "show me",
                    "get me",
                    "adopters",
                    "applicants",
                ]
            ):
                return {"type": "find_adopters", "filters": {}}
            elif any(
                word in message_lower
                for word in ["analyze", "review", "evaluate", "application"]
            ):
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
        temp_client = genai.Client(
            vertexai=True, project=self.project_id, location=region
        )
        return await temp_client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )


# Singleton instance
vertex_gemini_service = VertexGeminiService()
