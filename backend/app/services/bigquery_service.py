from typing import Dict, Any, List
from google.cloud import bigquery
from datetime import datetime
from elasticsearch.dsl import AsyncSearch
import asyncio
from app.core.config import get_settings
from app.core.logger import setup_logger
from app.services.elasticsearch_client import es_client
from app.core.google_cloud import GoogleCloudClients

settings = get_settings()
logger = setup_logger(__name__)


class BigQueryService:
    """
    Google BigQuery service for analytics and ML predictions
    Syncs outcome data from Elasticsearch and runs predictive models
    """

    def __init__(self):
        self.client = GoogleCloudClients.bigquery()
        self.dataset_id = "rescue_analytics"
        self.outcomes_table_id = "outcomes_history"
        self.predictions_table_id = "predictions_log"
        self.table_ref = f"{settings.gcp_project_id}.{self.dataset_id}.{self.outcomes_table_id}"
        self.predictions_table_ref = (
            f"{settings.gcp_project_id}.{self.dataset_id}.{self.predictions_table_id}"
        )

    async def sync_outcomes_to_bigquery(self) -> Dict[str, Any]:
        """
        Sync all outcomes from Elasticsearch to BigQuery using AsyncSearch
        Run this as a nightly batch job
        """
        try:
            search = AsyncSearch(using=es_client.client, index=settings.outcomes_index)
            rows_to_insert = []

            async for hit in search.scan():
                if hit.outcome == "success":
                    rows_to_insert.append(
                        {
                            "outcome_id": hit.meta.id,
                            "dog_id": hit.dog_id,
                            "outcome": "success",
                            "adopter_experience_level": hit.adopter_experience_level
                            or "intermediate",
                            "dog_difficulty_level": hit.dog_difficulty_level or "moderate",
                            "match_score_at_adoption": hit.match_score_at_adoption or 0.0,
                            "outcome_successful": True,
                            "satisfaction_score": hit.adopter_satisfaction_score,
                            "days_until_return": None,
                            "synced_at": datetime.now().isoformat(),
                        }
                    )
                elif hit.outcome == "returned":
                    rows_to_insert.append(
                        {
                            "outcome_id": hit.meta.id,
                            "dog_id": hit.dog_id,
                            "outcome": "returned",
                            "adopter_experience_level": hit.adopter_experience_level
                            or "intermediate",
                            "dog_difficulty_level": hit.dog_difficulty_level or "moderate",
                            "match_score_at_adoption": hit.match_score_at_adoption or 0.0,
                            "outcome_successful": False,
                            "satisfaction_score": None,
                            "days_until_return": hit.days_until_return,
                            "synced_at": datetime.now().isoformat(),
                        }
                    )

            if not rows_to_insert:
                return {"synced_count": 0, "message": "No outcomes to sync"}

            errors = await asyncio.to_thread(
                self.client.insert_rows_json, self.table_ref, rows_to_insert
            )

            if errors:
                logger.error(f"Errors inserting rows to BigQuery: {errors}")
                raise Exception(f"BigQuery insert errors: {errors}")

            logger.info(f"Successfully synced {len(rows_to_insert)} outcomes to BigQuery")

            return {
                "synced_count": len(rows_to_insert),
                "table": self.table_ref,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error syncing to BigQuery: {e}")
            raise

    async def query_success_rates(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query success rates by various dimensions safely using parameterized queries.
        """
        try:
            query_params = []
            query = f"""
            SELECT
                adopter_experience_level, dog_difficulty_level, COUNT(*) as total_adoptions,
                SUM(CASE WHEN outcome_successful THEN 1 ELSE 0 END) as successful_adoptions,
                ROUND(AVG(CASE WHEN outcome_successful THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate,
                ROUND(AVG(match_score_at_adoption), 2) as avg_match_score
            FROM `{self.table_ref}` WHERE 1=1
            """

            if filters:
                if exp_level := filters.get("adopter_experience_level"):
                    query += " AND adopter_experience_level = @exp_level"
                    query_params.append(
                        bigquery.ScalarQueryParameter("exp_level", "STRING", exp_level)
                    )
                if dog_diff := filters.get("dog_difficulty_level"):
                    query += " AND dog_difficulty_level = @dog_diff"
                    query_params.append(
                        bigquery.ScalarQueryParameter("dog_diff", "STRING", dog_diff)
                    )

            query += " GROUP BY adopter_experience_level, dog_difficulty_level ORDER BY success_rate DESC"

            job_config = bigquery.QueryJobConfig(query_parameters=query_params)

            # FIXED: Run the blocking query call in a separate thread
            query_job = await asyncio.to_thread(self.client.query, query, job_config=job_config)
            results = await asyncio.to_thread(query_job.result)

            stats = [dict(row) for row in results]  # More concise conversion
            logger.info(f"Retrieved success rate stats: {len(stats)} rows")
            return {"stats": stats, "query_timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Error querying success rates: {e}")
            raise

    async def predict_outcome_ml(
        self, adopter_experience: str, dog_difficulty: str, match_score: float
    ) -> Dict[str, Any]:
        """
        Use BigQuery ML model to predict adoption outcome safely.
        """
        try:
            query = f"""
            SELECT
                predicted_outcome_successful,
                predicted_outcome_successful_probs[OFFSET(1)].prob as confidence
            FROM
                ML.PREDICT(MODEL `{settings.gcp_project_id}.{self.dataset_id}.adoption_success_predictor`,
                    (
                        SELECT
                            @exp_level as adopter_experience_level,
                            @dog_diff as dog_difficulty_level,
                            @match_score as match_score_at_adoption
                    )
                )
            """
            query_params = [
                bigquery.ScalarQueryParameter("exp_level", "STRING", adopter_experience),
                bigquery.ScalarQueryParameter("dog_diff", "STRING", dog_difficulty),
                bigquery.ScalarQueryParameter("match_score", "FLOAT64", match_score),
            ]
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)

            query_job = await asyncio.to_thread(self.client.query, query, job_config=job_config)
            results = await asyncio.to_thread(query_job.result)

            for row in results:
                predicted_success = row["predicted_outcome_successful"]
                confidence = row["confidence"]
                result = {
                    "predicted_outcome": "success" if predicted_success else "returned",
                    "confidence": round(confidence, 4),
                    "adopter_experience": adopter_experience,
                    "dog_difficulty": dog_difficulty,
                    "match_score": match_score,
                    "recommendation": self._generate_ml_recommendation(
                        predicted_success, confidence
                    ),
                }
                await self._log_prediction(result)
                logger.info(
                    f"ML Prediction: {result['predicted_outcome']} (confidence: {confidence})"
                )
                return result

            raise Exception("No prediction result returned from BigQuery ML model")

        except Exception as e:
            logger.error(f"Error running ML prediction: {e}")
            raise

    async def _log_prediction(self, prediction: Dict[str, Any]) -> None:
        """Log ML prediction to BigQuery for tracking"""
        try:
            row = {
                "prediction_id": str(datetime.now().timestamp()),
                "predicted_outcome": prediction["predicted_outcome"],
                "confidence": prediction["confidence"],
                "adopter_experience_level": prediction["adopter_experience"],
                "dog_difficulty_level": prediction["dog_difficulty"],
                "match_score": prediction["match_score"],
                "created_at": datetime.now().isoformat(),
            }

            errors = await asyncio.to_thread(
                self.client.insert_rows_json, self.predictions_table_ref, [row]
            )
            if errors:
                logger.warning(f"Error logging prediction: {errors}")
        except Exception as e:
            logger.warning(f"Non-critical error logging prediction: {e}")

    def _generate_ml_recommendation(self, predicted_success: bool, confidence: float) -> str:
        """Generate recommendation based on ML prediction"""

        if predicted_success and confidence > 0.85:
            return "Strong Match - Proceed with adoption (ML confidence: high)"
        elif predicted_success and confidence > 0.70:
            return "Good Match - Proceed with adoption (ML confidence: moderate)"
        elif predicted_success:
            return "Possible Match - Schedule meet-and-greet (ML confidence: low)"
        elif not predicted_success and confidence > 0.85:
            return "High Risk - Not recommended (ML predicts failure with high confidence)"
        else:
            return "Uncertain - Consider trial foster period (ML confidence: low)"


# Singleton instance
bigquery_service = BigQueryService()
