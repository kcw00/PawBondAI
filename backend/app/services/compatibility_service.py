from typing import List, Dict, Any, Optional
from app.models.es_documents import Application, Dog
from app.services.elasticsearch_client import es_client
from app.core.logger import setup_logger
from elasticsearch.dsl import AsyncSearch
import math

logger = setup_logger(__name__)


class CompatibilityService:
    """Service for calculating compatibility scores between applications and dogs"""

    def __init__(self):
        self.weights = {
            "experience": 0.25,
            "housing": 0.20,
            "lifestyle": 0.15,
            "household": 0.15,
            "motivation": 0.25,
        }

    async def calculate_compatibility(
        self, application_id: str, dog_id: str
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive compatibility score between an application and a dog

        Returns dict with:
        - overall_score: 0-100
        - dimension_scores: breakdown by each dimension
        - recommendation: approve/review/reject
        - concerns: list of potential issues
        """
        try:
            # Fetch application and dog documents
            app_doc = await Application.get(id=application_id, using=es_client.client)
            dog_doc = await Dog.get(id=dog_id, using=es_client.client)

            # Calculate scores for each dimension
            experience_score = self._score_experience(app_doc, dog_doc)
            housing_score = self._score_housing(app_doc, dog_doc)
            lifestyle_score = self._score_lifestyle(app_doc, dog_doc)
            household_score = self._score_household(app_doc, dog_doc)
            motivation_score = await self._score_motivation(app_doc, dog_doc)

            # Calculate weighted overall score
            overall_score = (
                experience_score * self.weights["experience"]
                + housing_score * self.weights["housing"]
                + lifestyle_score * self.weights["lifestyle"]
                + household_score * self.weights["household"]
                + motivation_score * self.weights["motivation"]
            )

            # Generate recommendation and concerns
            recommendation, concerns = self._generate_recommendation(
                overall_score,
                {
                    "experience": experience_score,
                    "housing": housing_score,
                    "lifestyle": lifestyle_score,
                    "household": household_score,
                    "motivation": motivation_score,
                },
                app_doc,
                dog_doc,
            )

            return {
                "overall_score": round(overall_score, 2),
                "dimension_scores": {
                    "experience": round(experience_score, 2),
                    "housing": round(housing_score, 2),
                    "lifestyle": round(lifestyle_score, 2),
                    "household": round(household_score, 2),
                    "motivation": round(motivation_score, 2),
                },
                "recommendation": recommendation,
                "concerns": concerns,
                "application_id": application_id,
                "dog_id": dog_id,
            }

        except Exception as e:
            logger.error(f"Error calculating compatibility: {e}")
            raise

    def _score_experience(self, app: Application, dog: Dog) -> float:
        """
        Score pet experience match (0-100)

        Factors:
        - Current/past pet ownership
        - Volunteer experience
        - Surrender history
        - New pet introduction plan quality
        """
        score = 50  # Base score

        # Pet ownership experience
        if app.pet_experience.has_current_or_past_pets:
            score += 20
            # Check for detailed history
            if app.pet_experience.pet_history_details:
                score += 10

        # Volunteer experience bonus
        if app.pet_experience.volunteer_experience_details:
            score += 15

        # Surrender history concern
        if app.pet_experience.ever_surrendered_pet:
            if app.pet_experience.surrender_reason:
                # Has explanation - less concerning
                score -= 10
            else:
                # No explanation - more concerning
                score -= 20

        # New pet introduction plan
        if app.pet_experience.new_pet_introduction_plan:
            plan_length = len(app.pet_experience.new_pet_introduction_plan)
            if plan_length > 200:  # Detailed plan
                score += 15
            elif plan_length > 50:  # Basic plan
                score += 5

        return min(100, max(0, score))

    def _score_housing(self, app: Application, dog: Dog) -> float:
        """
        Score housing compatibility (0-100)

        Factors:
        - Housing type and size
        - Yard/balcony availability
        - Landlord permission (if renting)
        - Space adequacy for dog size
        """
        score = 70  # Base score

        # Space requirements by dog weight
        if dog.weight_kg and app.housing_info.size_sqm:
            if dog.weight_kg > 30:  # Large dog
                if app.housing_info.size_sqm >= 100:  # ~1000 sqft
                    score += 15
                elif app.housing_info.size_sqm < 70:  # ~750 sqft
                    score -= 20
            elif dog.weight_kg > 15:  # Medium dog
                if app.housing_info.size_sqm >= 70:
                    score += 10

        # Yard/balcony for active dogs
        behavioral_text = (dog.behavioral_notes or "").lower()
        high_energy = any(
            word in behavioral_text for word in ["active", "energetic", "playful", "high energy"]
        )

        if high_energy:
            if app.housing_info.has_yard_or_balcony:
                score += 15
            else:
                score -= 15

        # Landlord permission (critical for renters)
        if app.housing_info.ownership_status in ["Leased", "Rented"]:
            if app.housing_info.landlord_permission_granted == "Yes":
                score += 10
            elif app.housing_info.landlord_permission_granted == "No":
                score -= 40  # Major red flag
            else:  # Not_Applicable or missing
                score -= 25

        # Housing type suitability
        if app.housing_info.type in ["Detached House", "Townhouse"]:
            score += 5
        elif app.housing_info.type == "Apartment" and dog.weight_kg and dog.weight_kg > 35:
            score -= 10  # Large dog in apartment

        return min(100, max(0, score))

    def _score_lifestyle(self, app: Application, dog: Dog) -> float:
        """
        Score lifestyle compatibility (0-100)

        Factors:
        - Application type (foster vs adopt)
        - KARA donor status
        - Long-term commitment indicators
        """
        score = 70  # Base score

        # Application type
        if app.application_meta.type == "Adoption":
            score += 20  # Long-term commitment
        elif app.application_meta.type == "Foster":
            score += 10  # Still valuable

        # KARA donor bonus (shows commitment)
        if app.application_meta.is_kara_donor:
            score += 15

        # Marital stability (optional field)
        if app.applicant_info.marital_status in ["Married", "Partnered"]:
            score += 5  # Stable household

        return min(100, max(0, score))

    def _score_household(self, app: Application, dog: Dog) -> float:
        """
        Score household compatibility (0-100)

        Factors:
        - Household agreement
        - Allergies
        - Household size vs dog temperament
        """
        score = 70  # Base score

        # All members agreement (critical)
        if app.household_info.all_members_agree:
            agreement_text = app.household_info.all_members_agree.lower()
            if "yes" in agreement_text or "agree" in agreement_text:
                score += 20
            elif "no" in agreement_text or "disagree" in agreement_text:
                score -= 40

        # Allergies
        if app.household_info.has_allergies:
            if app.household_info.allergy_details:
                # Has details - manageable
                score -= 10
            else:
                # No details - concerning
                score -= 20

        # Household size
        if app.household_info.household_size:
            if app.household_info.household_size == 1:
                # Single person - needs good support plan
                if app.applicant_info.emergency_contact_phone:
                    score += 5
            elif app.household_info.household_size >= 2:
                # Multiple people - more support
                score += 10

        # Members description quality
        if app.household_info.members_description:
            if len(app.household_info.members_description) > 100:
                score += 10  # Detailed description

        return min(100, max(0, score))

    async def _score_motivation(self, app: Application, dog: Dog) -> float:
        """
        Score motivation alignment using Elasticsearch semantic search (0-100)

        Uses ES inference endpoint (google_vertex_ai_embedding) for semantic similarity
        """
        try:
            # Build dog profile text for semantic comparison
            dog_profile_text = f"""
            Dog: {dog.name}
            Breed: {dog.breed}
            Age: {dog.age}
            Weight: {dog.weight_kg}kg
            Behavioral Notes: {dog.behavioral_notes or 'N/A'}
            Medical History: {dog.medical_history or 'N/A'}
            """

            # Use Elasticsearch semantic search with inference endpoint
            # This automatically generates embeddings using google_vertex_ai_embedding
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "semantic": {
                                    "field": "application_summary",
                                    "query": dog_profile_text.strip()
                                }
                            }
                        ],
                        "filter": [
                            {
                                "term": {
                                    "_id": app.meta.id
                                }
                            }
                        ]
                    }
                },
                "_source": False
            }

            response = await es_client.client.search(
                index="applications",
                body=search_body
            )

            # Extract the similarity score from Elasticsearch
            if response["hits"]["hits"]:
                # ES semantic search returns a relevance score
                # Higher score = better semantic match
                es_score = response["hits"]["hits"][0]["_score"]

                # Normalize ES score to 0-100 range
                # ES semantic search typically returns values 0-2
                # Convert to percentage: (score / 2) * 100
                normalized_score = min(100, max(0, (es_score / 2) * 100))

                return normalized_score
            else:
                return 50.0  # Neutral score if no match

        except Exception as e:
            logger.error(f"Error scoring motivation with semantic search: {e}")
            # Return neutral score on error
            return 50.0

    def _generate_recommendation(
        self,
        overall_score: float,
        dimension_scores: Dict[str, float],
        app: Application,
        dog: Dog,
    ) -> tuple[str, List[str]]:
        """
        Generate recommendation and identify concerns

        Returns:
        - recommendation: "approve", "review", or "reject"
        - concerns: list of concern strings
        """
        concerns = []

        # Check individual dimensions for red flags
        if dimension_scores["experience"] < 40:
            concerns.append("Limited pet ownership experience")

        if dimension_scores["housing"] < 50:
            concerns.append("Housing may not be suitable")
            if app.housing_info.ownership_status in ["Leased", "Rented"]:
                if app.housing_info.landlord_permission_granted != "Yes":
                    concerns.append("CRITICAL: No landlord permission")

        if dimension_scores["household"] < 50:
            concerns.append("Household compatibility concerns")
            if app.household_info.has_allergies:
                concerns.append("Household member has allergies")

        if dimension_scores["lifestyle"] < 50:
            concerns.append("Lifestyle may not align with pet needs")

        if dimension_scores["motivation"] < 50:
            concerns.append("Application essays don't strongly align with this dog's profile")

        # Check for surrender history
        if app.pet_experience.ever_surrendered_pet:
            if not app.pet_experience.surrender_reason:
                concerns.append("Previous pet surrender without explanation")

        # Generate recommendation based on overall score and concerns
        critical_concerns = any("CRITICAL" in c for c in concerns)

        if critical_concerns or overall_score < 50:
            recommendation = "reject"
        elif overall_score >= 80 and len(concerns) <= 1:
            recommendation = "approve"
        else:
            recommendation = "review"

        return recommendation, concerns

    async def rank_applications_for_dog(
        self, dog_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank all pending/under_review applications for a specific dog

        Returns list of applications with compatibility scores, sorted by overall_score
        """
        try:
            # Get all pending or under_review applications
            s = AsyncSearch(using=es_client.client, index="applications")
            s = s.query("match_all")
            s = s.filter(
                "terms", **{"application_meta.status": ["Pending", "Under_Review"]}
            )
            s = s[0:100]  # Get up to 100 applications

            response = await s.execute()

            # Calculate compatibility for each application
            ranked_applications = []
            for hit in response:
                app_data = hit.to_dict()
                app_id = hit.meta.id

                try:
                    compatibility = await self.calculate_compatibility(
                        app_id, dog_id
                    )

                    ranked_applications.append(
                        {
                            "application": {**app_data, "id": app_id},
                            "compatibility": compatibility,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error scoring application {app_id}: {e}"
                    )
                    continue

            # Sort by overall score descending
            ranked_applications.sort(
                key=lambda x: x["compatibility"]["overall_score"], reverse=True
            )

            # Return top N
            return ranked_applications[:limit]

        except Exception as e:
            logger.error(f"Error ranking applications: {e}")
            raise


compatibility_service = CompatibilityService()
