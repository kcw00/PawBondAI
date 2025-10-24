from typing import Dict, Any, List
from app.services.vertex_gemini_service import vertex_gemini_service
from app.core.logger import setup_logger

logger = setup_logger(__name__)


class MedicalExtractionService:
    """
    AI-powered medical history extraction service

    Automatically extracts structured medical data from free-text medical histories.
    Used for both single dog entry and bulk CSV uploads.

    Now uses Vertex AI Gemini (production-grade)
    """

    def __init__(self):
        self.service = vertex_gemini_service

    async def extract_medical_data(
        self, medical_history_text: str, dog_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Extract structured medical data from free-text medical history

        Delegates to vertex_gemini_service

        Args:
            medical_history_text: Natural language medical history
            dog_name: Name of the dog (for context)

        Returns:
            Dictionary containing medical_events, past_conditions, active_treatments, etc.
        """
        return await self.service.extract_medical_data(medical_history_text, dog_name)


    async def batch_extract(self, dogs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract medical data for multiple dogs (bulk upload)

        Args:
            dogs_data: List of dicts with keys: name, breed, age, medical_history

        Returns:
            List of dicts with original data + extracted medical fields
        """
        results = []

        for i, dog_data in enumerate(dogs_data):
            try:
                name = dog_data.get("name", f"Dog-{i+1}")
                medical_history = dog_data.get("medical_history", "")

                if not medical_history or medical_history.strip() == "":
                    # No medical history - set healthy defaults
                    extracted = {
                        "medical_events": [],
                        "past_conditions": [],
                        "active_treatments": [],
                        "severity_score": 0,
                        "adoption_readiness": "ready",
                        "medical_summary": "No medical history provided",
                    }
                else:
                    # Extract medical data
                    extracted = await self.extract_medical_data(medical_history, name)

                # Merge with original data
                result = {**dog_data, **extracted}
                results.append(result)

                logger.info(
                    f"Batch extraction {i+1}/{len(dogs_data)}: {name} - {extracted['adoption_readiness']}"
                )

            except Exception as e:
                logger.error(f"Error in batch extraction for dog {i+1}: {e}")
                # Add original data with fallback (handled by service)
                fallback = await self.service.extract_medical_data(
                    dog_data.get("medical_history", ""), name
                )
                result = {**dog_data, **fallback}
                results.append(result)

        logger.info(f"Completed batch extraction for {len(results)} dogs")
        return results

    def calculate_current_conditions(self, medical_events: List[Dict[str, Any]]) -> List[str]:
        """
        Calculate current/active conditions from medical events

        Args:
            medical_events: List of medical event dicts

        Returns:
            List of current condition names
        """
        current = []
        for event in medical_events:
            if event.get("outcome") in ["ongoing", "worsened"]:
                condition = event.get("condition")
                if condition and condition not in current:
                    current.append(condition)
        return current


# Singleton instance
medical_extraction_service = MedicalExtractionService()
