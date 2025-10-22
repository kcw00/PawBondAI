from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import Optional
from elasticsearch.dsl import AsyncSearch
from app.models.schemas import MotivationRequest, AnalysisResponse, PredictionRequest
from app.services.elasticsearch_service import ElasticsearchService, get_elasticsearch_service
from app.services.vertex_gemini_service import vertex_gemini_service
from app.services.bigquery_service import bigquery_service
from app.services.elasticsearch_client import es_client
from app.core.logger import setup_logger
from app.core.config import get_settings

router = APIRouter()
logger = setup_logger(__name__)
settings = get_settings()


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
            s = AsyncSearch(using=es_client.client, index=settings.outcomes_index)
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

            # Fallback: Use semantic pattern matching from historical outcomes
            query_text = f"{prediction.adopter_experience} adopter with {prediction.dog_difficulty} dog, match score {prediction.match_score}"

            # Find similar successful outcomes using semantic search
            success_search = AsyncSearch(using=es_client.client, index=settings.outcomes_index)
            success_search = success_search.query(
                "semantic", field="success_factors", query=query_text
            )
            success_search = success_search.filter("term", outcome="success")
            success_search = success_search[0:10]
            success_response = await success_search.execute()

            # Find similar failed outcomes using semantic search
            failed_search = AsyncSearch(using=es_client.client, index=settings.outcomes_index)
            failed_search = failed_search.query(
                "semantic", field="failure_factors", query=query_text
            )
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
                "source": "Elasticsearch Semantic Pattern Matching",
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
async def analyze_sentiment(request: MotivationRequest):
    """
    Analyze sentiment of application text using Vertex AI Gemini

    Replaces Google Cloud Natural Language API with Gemini (consolidated AI service)

    Demo: "Sentiment: Positive (score: 0.8)"
    """
    try:
        analysis_result = await vertex_gemini_service.analyze_sentiment_and_entities(
            text=request.motivation_text
        )

        # Transform to match expected response format
        return {
            "sentiment": analysis_result["sentiment"],
            "key_entities": analysis_result["entities"][:10],  # Top 10
            "key_themes": analysis_result["themes"],
            "commitment_assessment": analysis_result["commitment_assessment"],
            "text_length": analysis_result["text_length"],
            "recommendation": analysis_result["recommendation"],
        }

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/dashboard")
async def get_dashboard_analytics(
    es_service: ElasticsearchService = Depends(get_elasticsearch_service),
):
    """
    Comprehensive analytics for demo dashboard using Elasticsearch DSL

    Returns:
    - Overall success rate
    - Success by experience level
    - Success by dog difficulty
    - Key insights
    """
    try:
        dashboard = await es_service.get_realtime_analytics_from_es()
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
