from typing import Dict, Any, List, Optional
from app.services.elasticsearch_service import es_service
from app.core.config import get_settings

settings = get_settings()


class MatchingService:
    """
    Core matching logic using Elasticsearch
    Learns from both successes AND failures
    """

    async def analyze_application(self, application_text: str) -> Dict[str, Any]:
        """
        Analyze application and find patterns
        """
        # Find similar past adopters (successes)
        similar_successes = await es_service.semantic_search(
            index=settings.outcomes_index,
            query=application_text,
            semantic_field="success_factors",
            filters=[{"outcome": "success"}],
            size=10,
        )

        # Find similar failures
        similar_failures = await es_service.semantic_search(
            index=settings.outcomes_index,
            query=application_text,
            semantic_field="failure_factors",
            filters=[{"outcome": "returned"}],
            size=10,
        )

        # Extract patterns
        patterns = await self._extract_patterns(similar_successes["hits"], similar_failures["hits"])

        # Find matching dogs
        matching_dogs = await self._find_matching_dogs(application_text, patterns)

        # Calculate prediction
        prediction = self._calculate_prediction(similar_successes["hits"], similar_failures["hits"])

        return {
            "similar_successful_adopters": similar_successes["hits"][:3],
            "similar_failed_adopters": similar_failures["hits"][:3],
            "patterns": patterns,
            "recommended_dogs": matching_dogs,
            "prediction": prediction,
        }

    async def find_adopters(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Find matching adopters using hybrid search with structured filters"""
        # Use semantic search on motivation field only
        # Other fields (other_pets_description, family_members) are likely semantic_text too
        # So we'll rely on semantic search + filters for now
        return await es_service.hybrid_search(
            index=settings.applications_index,
            query=query,
            semantic_field="motivation",
            text_fields=[],  # Empty - no regular text fields to search
            filters=filters,
            size=20,
        )

    async def find_dogs_for_adopter(
        self, adopter_text: str, filters: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Find matching dogs for an adopter"""
        if filters is None:
            filters = []
        filters.append({"status": "available"})

        return await es_service.hybrid_search(
            index=settings.dogs_index,
            query=adopter_text,
            semantic_field="personality_traits",
            text_fields=["behavioral_notes", "medical_needs"],
            filters=filters,
            size=10,
        )

    async def predict_outcome(self, dog_id: str, application_id: str) -> Dict[str, Any]:
        """
        Predict outcome for a potential match
        Uses both success and failure patterns
        """
        # Get dog and application data
        dog = await es_service.get_document(settings.dogs_index, dog_id)
        application = await es_service.get_document(settings.applications_index, application_id)

        # Build search query
        search_text = (
            f"{dog['personality_traits']} {dog['behavioral_notes']} " f"{application['motivation']}"
        )

        # Find similar successful outcomes
        success_results = await es_service.semantic_search(
            index=settings.outcomes_index,
            query=search_text,
            semantic_field="success_factors",
            filters=[{"outcome": "success"}],
            size=10,
        )

        # Find similar failed outcomes
        failure_results = await es_service.semantic_search(
            index=settings.outcomes_index,
            query=search_text,
            semantic_field="failure_factors",
            filters=[{"outcome": "returned"}],
            size=10,
        )

        # Calculate prediction
        prediction = self._calculate_prediction(success_results["hits"], failure_results["hits"])

        return {
            "predicted_outcome": prediction["outcome"],
            "confidence": prediction["confidence"],
            "success_patterns": success_results["hits"][:3],
            "failure_risks": failure_results["hits"][:3],
            "recommendation": prediction["recommendation"],
        }

    async def _extract_patterns(
        self, successes: List[Dict], failures: List[Dict]
    ) -> Dict[str, Any]:
        """Extract patterns from outcomes"""
        # Get aggregations
        experience_agg = await es_service.aggregations(
            index=settings.outcomes_index,
            field="adopter_experience_level",
            filters=[{"outcome": "success"}],
        )

        patterns = {
            "works_from_home_count": 0,
            "previous_experience_count": 0,
            "patient_personality_count": 0,
            "total_successes": len(successes),
            "total_failures": len(failures),
            "experience_distribution": experience_agg,
        }

        # Analyze text patterns
        for success in successes:
            text = success["data"].get("success_factors", "").lower()
            if "work from home" in text or "remote" in text:
                patterns["works_from_home_count"] += 1
            if "previous" in text or "experience" in text:
                patterns["previous_experience_count"] += 1
            if "patient" in text or "calm" in text:
                patterns["patient_personality_count"] += 1

        # Calculate percentages
        if patterns["total_successes"] > 0:
            patterns["works_from_home_percent"] = round(
                (patterns["works_from_home_count"] / patterns["total_successes"]) * 100
            )
            patterns["previous_experience_percent"] = round(
                (patterns["previous_experience_count"] / patterns["total_successes"]) * 100
            )

        return patterns

    async def _find_matching_dogs(self, adopter_text: str, patterns: Dict[str, Any]) -> List[Dict]:
        """Find dogs that match adopter profile"""
        # Enhance query based on patterns
        query = adopter_text

        if patterns.get("works_from_home_percent", 0) > 70:
            query += " separation anxiety needs companionship"
        if patterns.get("previous_experience_percent", 0) > 70:
            query += " challenging behavioral needs"

        result = await es_service.semantic_search(
            index=settings.dogs_index,
            query=query,
            semantic_field="personality_traits",
            filters=[{"status": "available"}],
            size=5,
        )

        return result["hits"]

    def _calculate_prediction(self, successes: List[Dict], failures: List[Dict]) -> Dict[str, Any]:
        """Calculate outcome prediction"""
        total = len(successes) + len(failures)

        if total == 0:
            return {
                "outcome": "uncertain",
                "confidence": 0,
                "recommendation": "Insufficient historical data. Recommend trial foster period.",
            }

        success_ratio = len(successes) / total

        if success_ratio > 0.7:
            outcome = "success"
            confidence = min(int(success_ratio * 100), 95)
            recommendation = "Strong match - proceed with adoption"
        elif success_ratio > 0.5:
            outcome = "success"
            confidence = int(success_ratio * 100)
            recommendation = "Good match - schedule meet-and-greet"
        elif success_ratio < 0.3:
            outcome = "high_risk"
            confidence = int((1 - success_ratio) * 100)
            recommendation = "Caution: High risk of return. Review failure patterns carefully."
        else:
            outcome = "uncertain"
            confidence = 50
            recommendation = "Mixed signals. Recommend extended trial period."

        return {
            "outcome": outcome,
            "confidence": confidence,
            "success_count": len(successes),
            "failure_count": len(failures),
            "recommendation": recommendation,
        }


# Singleton
matching_service = MatchingService()
