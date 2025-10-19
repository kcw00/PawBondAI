from typing import Dict, Any, List
from google.cloud import language_v1
from google.api_core.exceptions import GoogleAPICallError
from app.core.logger import setup_logger

logger = setup_logger(__name__)


class SentimentService:
    """
    Google Cloud Natural Language API service
    Analyzes sentiment and extracts entities from application text
    """

    def __init__(self):
        try:
            self.client = language_v1.LanguageServiceClient()
            logger.info("✅ Google Cloud Language client initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing Google Cloud Language client: {e}")
            raise

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (motivation essays, follow-up notes, etc.)

        Returns:
            sentiment_score: -1.0 (negative) to 1.0 (positive)
            magnitude: How emotional the text is (0.0 to infinity)
        """
        try:
            document = language_v1.Document(
                content=text, type_=language_v1.Document.Type.PLAIN_TEXT
            )

            sentiment = self.client.analyze_sentiment(
                request={"document": document}
            ).document_sentiment

            result = {
                "score": sentiment.score,  # -1.0 to 1.0
                "magnitude": sentiment.magnitude,  # 0.0+
                "interpretation": self._interpret_sentiment(sentiment.score, sentiment.magnitude),
            }

            logger.info(
                f"Sentiment analysis complete: score={result['score']}, magnitude={result['magnitude']}"
            )

            return result
        except GoogleAPICallError as e:
            logger.error(f"Google API call error during sentiment analysis: {e}")
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract key entities (people, pets, locations, concepts) from text

        Useful for finding patterns like:
        - "patient", "calm" → personality traits
        - "work from home" → lifestyle factors
        - "previous rescue dog" → experience indicators
        """
        try:
            document = language_v1.Document(
                content=text, type_=language_v1.Document.Type.PLAIN_TEXT
            )

            response = self.client.analyze_entities(request={"document": document})

            entities = []
            for entity in response.entities:
                entities.append(
                    {
                        "name": entity.name,
                        "type": language_v1.Entity.Type(entity.type_).name,
                        "salience": entity.salience,  # Importance (0.0 to 1.0)
                        "mentions": [
                            mention.text.content for mention in entity.mentions[:3]
                        ],  # First 3 mentions
                    }
                )

            # Sort by salience (most important first)
            entities.sort(key=lambda x: x["salience"], reverse=True)

            logger.info(f"Extracted {len(entities)} entities from text")

            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            raise

    def analyze_application_motivation(self, motivation_text: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of adopter motivation essay

        Combines sentiment + entity extraction to determine:
        - Is the adopter genuinely committed?
        - What are their key motivations?
        - Any red flags?
        """
        try:
            # Run both analyses
            sentiment = self.analyze_sentiment(motivation_text)
            entities = self.extract_entities(motivation_text)

            # Extract key themes
            key_themes = self._extract_themes(entities)

            # Determine commitment level
            commitment_assessment = self._assess_commitment(sentiment, entities, motivation_text)

            return {
                "sentiment": sentiment,
                "key_entities": entities[:10],  # Top 10
                "key_themes": key_themes,
                "commitment_assessment": commitment_assessment,
                "text_length": len(motivation_text.split()),
                "recommendation": self._generate_recommendation(sentiment, commitment_assessment),
            }

        except Exception as e:
            logger.error(f"Error analyzing application motivation: {e}")
            raise

    def _interpret_sentiment(self, score: float, magnitude: float) -> str:
        """
        Human-readable sentiment interpretation

        Score: -1.0 to 1.0
        Magnitude: 0.0+ (emotional intensity)
        """
        if score >= 0.5 and magnitude >= 1.0:
            return "Highly Positive & Enthusiastic"
        elif score >= 0.25:
            return "Positive"
        elif score >= -0.25:
            return "Neutral/Mixed"
        elif score >= -0.5:
            return "Negative"
        else:
            return "Very Negative"

    def _extract_themes(self, entities: List[Dict[str, Any]]) -> List[str]:
        """
        Extract common adoption themes from entities

        Looks for indicators like:
        - Experience: "previous dog", "rescue experience"
        - Commitment: "long-term", "lifetime", "forever home"
        - Lifestyle: "work from home", "active", "patient"
        """
        themes = []

        # Combine all entity names and mentions
        all_text = " ".join(
            [
                entity["name"].lower() + " " + " ".join(entity["mentions"]).lower()
                for entity in entities
            ]
        )

        # Theme keywords
        theme_keywords = {
            "experienced_adopter": ["previous", "experience", "rescue", "foster", "volunteer"],
            "long_term_commitment": ["long-term", "lifetime", "forever", "permanent", "commitment"],
            "patient_personality": ["patient", "calm", "understanding", "gentle"],
            "active_lifestyle": ["active", "exercise", "walks", "hiking", "running"],
            "work_from_home": ["work from home", "remote", "home office", "flexible schedule"],
            "family_oriented": ["family", "children", "kids", "household"],
            "training_focus": ["training", "obedience", "behavioral", "learn"],
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)

        return themes

    def _assess_commitment(
        self, sentiment: Dict[str, Any], entities: List[Dict[str, Any]], text: str
    ) -> Dict[str, Any]:
        score = 50
        if sentiment["score"] > 0.5:
            score += 20
        elif sentiment["score"] > 0.25:
            score += 10
        if sentiment["magnitude"] > 2.0:
            score += 10
        word_count = len(text.split())
        if word_count > 200:
            score += 15
        elif word_count > 100:
            score += 10
        commitment_phrases = [
            "long-term",
            "lifetime",
            "forever",
            "commitment",
            "dedicated",
            "patient",
            "work through",
            "behavioral training",
        ]
        phrase_count = sum(1 for phrase in commitment_phrases if phrase in text.lower())
        score += min(phrase_count * 5, 20)
        red_flags = ["easy", "cute", "instagram", "temporary", "try it out"]
        flag_count = sum(1 for flag in red_flags if flag in text.lower())
        score -= flag_count * 10
        score = max(0, min(100, score))
        if score >= 80:
            level = "Very High"
        elif score >= 65:
            level = "High"
        elif score >= 50:
            level = "Moderate"
        elif score >= 35:
            level = "Low"
        else:
            level = "Very Low"
        return {
            "commitment_score": score,
            "commitment_level": level,
            "word_count": word_count,
            "positive_indicators": phrase_count,
            "red_flags": flag_count,
        }

    def _generate_recommendation(
        self, sentiment: Dict[str, Any], commitment: Dict[str, Any]
    ) -> str:
        if commitment["commitment_score"] >= 75 and sentiment["score"] > 0.5:
            return "Highly Recommended - Strong commitment signals and positive sentiment"
        elif commitment["commitment_score"] >= 60:
            return "Recommended - Good indicators of serious intent"
        elif commitment["commitment_score"] >= 45:
            return "Proceed with Caution - Schedule interview to assess further"
        else:
            return "Not Recommended - Low commitment signals, consider other applicants first"


# Singleton instance for the application to use
sentiment_service_instance = SentimentService()


def get_sentiment_service():
    return sentiment_service_instance
