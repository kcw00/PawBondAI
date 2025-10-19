from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from elasticsearch.dsl import AsyncSearch
from app.models.schemas import MotivationRequest, AnalysisResponse
from app.services.bigquery_service import bigquery_service
from app.services.sentiment_service import SentimentService, get_sentiment_service
from app.services.elasticsearch_client import es_client
from app.core.logger import setup_logger
from google.api_core.exceptions import GoogleAPICallError

router = APIRouter()
logger = setup_logger(__name__)


# Request/Response Schemas
class PredictionRequest(BaseModel):
    adopter_experience: str  # "beginner", "intermediate", "expert"
    dog_difficulty: str  # "easy", "moderate", "challenging"
    match_score: float  # 0.0 to 1.0


# Analytics Endpoints


@router.get("/success-rates")
async def get_success_rates(
    adopter_experience: Optional[str] = Query(
        None, description="Filter by adopter experience level"
    ),
    dog_difficulty: Optional[str] = Query(None, description="Filter by dog difficulty level"),
):
    """
    Get success rates by various dimensions using Elasticsearch DSL

    For demo: Show "Work-from-home adopters: 89% success"
    """
    try:
        filters = {}
        if adopter_experience:
            filters["adopter_experience_level"] = adopter_experience
        if dog_difficulty:
            filters["dog_difficulty_level"] = dog_difficulty

        # Get from BigQuery (if setup) or fallback to Elasticsearch
        try:
            result = await bigquery_service.query_success_rates(filters)
            result["source"] = "BigQuery"
        except Exception as bq_error:
            logger.warning(f"BigQuery not available, using Elasticsearch: {bq_error}")

            # Fallback: Use Elasticsearch AsyncSearch
            s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
            total_count = await s.count()

            success_s = s.filter("term", outcome="success")
            success_count = await success_s.count()

            success_rate = (success_count / total_count * 100) if total_count > 0 else 0

            result = {
                "stats": [
                    {
                        "total_adoptions": total_count,
                        "successful_adoptions": success_count,
                        "success_rate": round(success_rate, 2),
                    }
                ],
                "source": "Elasticsearch",
            }

        return result

    except Exception as e:
        logger.error(f"Error getting success rates: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/predict")
async def predict_adoption_outcome(prediction: PredictionRequest = Body(...)):
    """
    ML prediction for adoption outcome using Elasticsearch DSL

    Demo: "Predicted: SUCCESS - 92% confidence"
    """
    try:
        # Try BigQuery ML prediction
        try:
            result = await bigquery_service.predict_outcome_ml(
                adopter_experience=prediction.adopter_experience,
                dog_difficulty=prediction.dog_difficulty,
                match_score=prediction.match_score,
            )
            result["source"] = "BigQuery ML"

        except Exception as bq_error:
            logger.warning(f"BigQuery ML not available, using pattern matching: {bq_error}")

            # Fallback: Use pattern matching from historical outcomes with AsyncSearch
            query_text = f"{prediction.adopter_experience} adopter with {prediction.dog_difficulty} dog, match score {prediction.match_score}"

            # Find similar successful outcomes using AsyncSearch
            success_search = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
            success_search = success_search.query("match", success_factors=query_text)
            success_search = success_search.filter("term", outcome="success")
            success_search = success_search[0:10]
            success_response = await success_search.execute()

            # Find similar failed outcomes using AsyncSearch
            failed_search = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
            failed_search = failed_search.query("match", failure_factors=query_text)
            failed_search = failed_search.filter("term", outcome="returned")
            failed_search = failed_search[0:10]
            failed_response = await failed_search.execute()

            # Calculate prediction based on similarity scores
            success_scores = [hit.meta.score for hit in success_response]
            failed_scores = [hit.meta.score for hit in failed_response]

            total_score = sum(success_scores) + sum(failed_scores)
            success_ratio = sum(success_scores) / total_score if total_score > 0 else 0.5

            predicted_outcome = "success" if success_ratio > 0.5 else "returned"
            confidence = success_ratio if predicted_outcome == "success" else (1 - success_ratio)

            result = {
                "predicted_outcome": predicted_outcome,
                "confidence": round(confidence, 4),
                "adopter_experience": prediction.adopter_experience,
                "dog_difficulty": prediction.dog_difficulty,
                "match_score": prediction.match_score,
                "similar_successful_cases": len(success_response),
                "similar_failed_cases": len(failed_response),
                "source": "Elasticsearch Pattern Matching",
                "recommendation": f"{'Proceed with adoption' if predicted_outcome == 'success' else 'High risk - recommend trial foster'}",
            }

        logger.info(
            f"Prediction: {result['predicted_outcome']} (confidence: {result['confidence']})"
        )
        return result

    except Exception as e:
        logger.error(f"Error predicting outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/sentiment", response_model=AnalysisResponse)
def analyze_sentiment(
    request: MotivationRequest, service: SentimentService = Depends(get_sentiment_service)
):
    """
    Analyze sentiment of application text using Google Natural Language API

    Demo: "Sentiment: Positive (score: 0.8)"
    """
    try:
        analysis_result = service.analyze_application_motivation(
            motivation_text=request.motivation_text
        )

        return analysis_result
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=503, detail=f"Error communicating with Google Cloud NLP API: {e.message}"
        )

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/dashboard")
async def get_dashboard_analytics():
    """
    Comprehensive analytics for demo dashboard using Elasticsearch DSL

    Returns:
    - Overall success rate
    - Success by experience level
    - Success by dog difficulty
    - Key insights
    """
    try:
        # Get overall stats from Elasticsearch using AsyncSearch
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
        # Define aggregations
        s.aggs.bucket("outcomes", "terms", field="outcome")
        s.aggs.bucket("experience_breakdown", "terms", field="adopter_experience_level").bucket(
            "outcomes", "terms", field="outcome"
        )

        # Execute the search (we don't even need the hits, just the aggregations)
        response = await s.execute()

        # --- Process Aggregation Results ---
        aggs = response.aggregations

        total_count = aggs.outcomes.doc_count
        outcome_counts = {b.key: b.doc_count for b in aggs.outcomes.buckets}
        success_count = outcome_counts.get("success", 0)
        return_count = outcome_counts.get("returned", 0)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        # Process experience breakdown
        experience_breakdown = {}
        for bucket in aggs.experience_breakdown.buckets:
            level = bucket.key
            level_total = bucket.doc_count
            level_success = next(
                (b.doc_count for b in bucket.outcomes.buckets if b.key == "success"), 0
            )
            rate = (level_success / level_total * 100) if level_total > 0 else 0
            experience_breakdown[level] = {
                "total": level_total,
                "successful": level_success,
                "success_rate": round(rate, 2),
            }

        # Key insights (can be derived from aggregated data)
        insights = [
            f"Overall success rate: {round(success_rate, 2)}%",
            f"Total adoptions tracked: {total_count}",
        ]
        if "expert" in experience_breakdown and experience_breakdown["expert"]["success_rate"] > 80:
            insights.append("Expert adopters have highest success rate")

        dashboard = {
            "overall_stats": {
                "total_outcomes": total_count,
                "successful_adoptions": success_count,
                "returned_adoptions": return_count,
                "success_rate": round(success_rate, 2),
            },
            "experience_breakdown": experience_breakdown,
            "key_insights": insights,
            "data_source": "Elasticsearch (Aggregations)",
        }
        return dashboard

    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/sync-bigquery")
async def trigger_bigquery_sync():
    """
    Manually trigger BigQuery sync (normally runs nightly)

    For demo: Show data flowing from ES → BigQuery
    """
    try:
        result = await bigquery_service.sync_outcomes_to_bigquery()

        logger.info(f"BigQuery sync completed: {result['synced_count']} records")

        return {
            "success": True,
            "message": f"Synced {result['synced_count']} outcomes to BigQuery",
            "details": result,
        }

    except Exception as e:
        logger.error(f"Error syncing to BigQuery: {e}")
        # Non-critical error - BigQuery might not be set up yet
        return {
            "success": False,
            "message": "BigQuery sync not available (setup required)",
            "error": str(e),
        }
