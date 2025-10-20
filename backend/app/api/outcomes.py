from fastapi import APIRouter, HTTPException, Path, Query, Body
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.schemas import OutcomeCreate, OutcomeResponse, OutcomeStatsResponse
from app.models.es_documents import RescueAdoptionOutcome
from app.services.elasticsearch_client import es_client
from app.core.logger import setup_logger
from elasticsearch.dsl import AsyncSearch, Q

router = APIRouter()
logger = setup_logger(__name__)


# 1. Create a new outcome
# ~~~~~worked! testing done by with postman.
@router.post("", response_model=OutcomeResponse)
async def create_outcome(outcome: OutcomeCreate = Body(...)):
    """
    Create a new adoption outcome record
    Stores both successes and failures for ML learning
    """
    try:
        outcome_id = str(uuid.uuid4())

        # Create AsyncDocument instance
        doc = RescueAdoptionOutcome(meta={"id": outcome_id})
        doc.outcome_id = outcome_id
        doc.dog_id = outcome.dog_id
        doc.application_id = outcome.application_id
        doc.outcome = outcome.outcome
        doc.outcome_reason = outcome.outcome_reason
        doc.success_factors = outcome.success_factors or ""
        doc.failure_factors = outcome.failure_factors or ""
        doc.adoption_date = outcome.adoption_date or datetime.now()
        doc.return_date = outcome.return_date
        doc.adopter_satisfaction_score = outcome.adopter_satisfaction_score
        doc.dog_difficulty_level = outcome.dog_difficulty_level
        doc.adopter_experience_level = outcome.adopter_experience_level
        doc.match_score_at_adoption = outcome.match_score
        doc.created_by = outcome.created_by

        # Calculate days until return if applicable
        if outcome.return_date and outcome.adoption_date:
            doc.days_until_return = (outcome.return_date - outcome.adoption_date).days

        # Save to Elasticsearch using DSL
        await doc.save(using=es_client.client)

        logger.info(
            f"Created outcome {outcome_id} for dog {outcome.dog_id}, result: {outcome.outcome}"
        )

        return OutcomeResponse(
            outcome_id=outcome_id,
            dog_id=outcome.dog_id,
            application_id=outcome.application_id,
            outcome=outcome.outcome,
            outcome_reason=outcome.outcome_reason,
            success_factors=outcome.success_factors,
            failure_factors=outcome.failure_factors,
            adoption_date=doc.adoption_date.isoformat() if doc.adoption_date else None,
            return_date=doc.return_date.isoformat() if doc.return_date else None,
            days_until_return=doc.days_until_return,
            adopter_satisfaction_score=outcome.adopter_satisfaction_score,
            dog_difficulty_level=outcome.dog_difficulty_level,
            adopter_experience_level=outcome.adopter_experience_level,
            match_score_at_adoption=outcome.match_score,
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            created_by=outcome.created_by,
        )

    except Exception as e:
        logger.error(f"Error creating outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating outcome: {str(e)}")


# 2. Get all outcomes for a specific dog
# ~~~~worked! testing done by with postman.
@router.get("/dog/{dog_id}")
async def get_dog_outcomes(dog_id: str = Path(...)):
    """
    Get all outcomes for a specific dog using AsyncSearch
    Shows adoption history including returns
    """
    try:
        # Use AsyncSearch with filter
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
        s = s.filter("term", dog_id=dog_id)
        s = s.sort("-adoption_date")

        response = await s.execute()

        outcomes = []
        for hit in response:
            # Dates from ES are already strings, no need for isoformat()
            adoption_date = hit.adoption_date if hasattr(hit, "adoption_date") else None
            return_date = hit.return_date if hasattr(hit, "return_date") else None

            outcomes.append(
                {
                    "outcome_id": hit.meta.id,
                    "outcome": hit.outcome,
                    "adoption_date": adoption_date,
                    "return_date": return_date,
                    "days_until_return": (
                        hit.days_until_return if hasattr(hit, "days_until_return") else None
                    ),
                }
            )

        return {
            "dog_id": dog_id,
            "total_outcomes": len(outcomes),
            "outcomes": outcomes,
        }

    except Exception as e:
        logger.error(f"Error getting dog outcomes: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting outcomes: {str(e)}")


# 4. Get aggregate statistics
# ~~~~worked! testing done by with postman.
@router.get("/stats", response_model=OutcomeStatsResponse)
async def get_outcome_stats():
    """
    Get aggregate statistics on all outcomes using AsyncSearch
    """
    try:
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")

        # Total count
        total_count = await s.count()

        # Success count
        success_s = s.filter("term", outcome="success")
        success_count = await success_s.count()

        # Return count
        return_s = s.filter("term", outcome="returned")
        return_count = await return_s.count()

        # Calculate success rate
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        return OutcomeStatsResponse(
            total_outcomes=total_count,
            successful_adoptions=success_count,
            returned_adoptions=return_count,
            success_rate=round(success_rate, 2),
        )

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# 5. Get successful outcomes
# ~~~~worked! testing done by with postman.
@router.get("/successful")
async def get_successful_outcomes(
    limit: int = Query(10, ge=1, le=100),
    min_satisfaction: int = Query(7, ge=1, le=10),
):
    """
    Get successful outcomes for pattern learning using AsyncSearch
    """
    try:
        # Use AsyncSearch with filters
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
        s = s.filter("term", outcome="success")

        if min_satisfaction:
            s = s.filter("range", adopter_satisfaction_score={"gte": min_satisfaction})

        s = s.sort("-adopter_satisfaction_score", "-adoption_date")
        s = s[0:limit]

        response = await s.execute()

        outcomes = []
        for hit in response:
            outcomes.append(
                {
                    "outcome_id": hit.meta.id,
                    "dog_id": hit.dog_id,
                    "success_factors": hit.success_factors,
                    "adopter_experience_level": hit.adopter_experience_level,
                    "dog_difficulty_level": hit.dog_difficulty_level,
                    "match_score": hit.match_score_at_adoption,
                    "satisfaction_score": hit.adopter_satisfaction_score,
                }
            )

        return {
            "count": len(outcomes),
            "outcomes": outcomes,
        }

    except Exception as e:
        logger.error(f"Error getting successful outcomes: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 6. Get failed outcomes
# ~~~~worked! testing done by with postman.
@router.get("/failed")
async def get_failed_outcomes(limit: int = Query(10, ge=1, le=100)):
    """
    Get failed/returned outcomes for pattern learning using AsyncSearch
    """
    try:
        # Use AsyncSearch with filter
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
        s = s.filter("term", outcome="returned")
        s = s.sort("days_until_return")  # Fastest returns first
        s = s[0:limit]

        response = await s.execute()

        outcomes = []
        for hit in response:
            outcomes.append(
                {
                    "outcome_id": hit.meta.id,
                    "dog_id": hit.dog_id,
                    "failure_factors": hit.failure_factors,
                    "outcome_reason": hit.outcome_reason,
                    "adopter_experience_level": hit.adopter_experience_level,
                    "dog_difficulty_level": hit.dog_difficulty_level,
                    "days_until_return": hit.days_until_return,
                }
            )

        return {
            "count": len(outcomes),
            "outcomes": outcomes,
        }

    except Exception as e:
        logger.error(f"Error getting failed outcomes: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 7. Semantic search for similar outcomes
# ~~~~worked! testing done by with postman.
@router.post("/search")
async def search_similar_outcomes(
    query: str = Body(..., embed=True),
    outcome_type: str = Body("success", embed=True),
    limit: int = Body(5, embed=True),
):
    """
    Semantic search for similar outcomes using ES inference endpoint
    Used for prediction and pattern matching

    Args:
        query: Text describing the adoption scenario
        outcome_type: "success" or "failed"
        limit: Number of results to return
    """
    try:
        # Determine which field to search based on outcome type
        if outcome_type == "success":
            search_field = "success_factors"
            filter_outcome = "success"
        else:
            search_field = "failure_factors"
            filter_outcome = "returned"

        # Use AsyncSearch with semantic query (uses ES inference endpoint)
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
        s = s.query("semantic", field=search_field, query=query)
        s = s.filter("term", outcome=filter_outcome)
        s = s[0:limit]

        response = await s.execute()

        outcomes = []
        for hit in response:
            outcomes.append(
                {
                    "outcome_id": hit.meta.id,
                    "score": hit.meta.score,
                    "dog_id": hit.dog_id,
                    "factors": getattr(hit, search_field, ""),
                    "experience_level": hit.adopter_experience_level,
                    "difficulty_level": hit.dog_difficulty_level,
                }
            )

        return {
            "query": query,
            "outcome_type": outcome_type,
            "count": len(outcomes),
            "similar_outcomes": outcomes,
        }

    except Exception as e:
        logger.error(f"Error searching outcomes: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 8. List all outcomes with pagination
#   ~~~~worked! testing done by with postman.
@router.get("", response_model=List[OutcomeResponse])
async def list_outcomes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    outcome_filter: Optional[str] = Query(None, description="Filter by outcome type"),
):
    """List all outcomes with pagination using AsyncSearch"""
    try:
        s = AsyncSearch(using=es_client.client, index="rescue-adoption-outcomes")
        s = s.query("match_all")

        # Add filter if specified
        if outcome_filter:
            s = s.filter("term", outcome=outcome_filter)

        # Sort and paginate
        s = s.sort("-created_at")
        s = s[offset : offset + limit]

        response = await s.execute()

        outcomes = []
        for hit in response:
            # Dates from ES are already strings, no need for isoformat()
            outcomes.append(
                OutcomeResponse(
                    outcome_id=hit.meta.id,
                    dog_id=hit.dog_id,
                    application_id=hit.application_id,
                    outcome=hit.outcome,
                    outcome_reason=hit.outcome_reason,
                    success_factors=hit.success_factors,
                    failure_factors=hit.failure_factors,
                    adoption_date=hit.adoption_date if hasattr(hit, "adoption_date") else None,
                    return_date=hit.return_date if hasattr(hit, "return_date") else None,
                    days_until_return=(
                        hit.days_until_return if hasattr(hit, "days_until_return") else None
                    ),
                    adopter_satisfaction_score=(
                        hit.adopter_satisfaction_score
                        if hasattr(hit, "adopter_satisfaction_score")
                        else None
                    ),
                    dog_difficulty_level=(
                        hit.dog_difficulty_level if hasattr(hit, "dog_difficulty_level") else None
                    ),
                    adopter_experience_level=(
                        hit.adopter_experience_level
                        if hasattr(hit, "adopter_experience_level")
                        else None
                    ),
                    match_score_at_adoption=(
                        hit.match_score_at_adoption
                        if hasattr(hit, "match_score_at_adoption")
                        else None
                    ),
                    created_at=hit.created_at if hasattr(hit, "created_at") else None,
                    created_by=hit.created_by if hasattr(hit, "created_by") else None,
                )
            )

        return outcomes

    except Exception as e:
        logger.error(f"Error listing outcomes: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing outcomes: {str(e)}")


# 9. Get an outcome by ID
# ~~~~worked! testing done by with postman.
# IMPORTANT: This route must be LAST because /{outcome_id} will match any GET request
@router.get("/{outcome_id}", response_model=OutcomeResponse)
async def get_outcome(outcome_id: str = Path(...)):
    """Get a specific outcome by ID using Elasticsearch DSL"""
    try:
        # Use AsyncDocument.get()
        doc = await RescueAdoptionOutcome.get(id=outcome_id, using=es_client.client)

        return OutcomeResponse(
            outcome_id=outcome_id,
            dog_id=doc.dog_id,
            application_id=doc.application_id,
            outcome=doc.outcome,
            outcome_reason=doc.outcome_reason,
            success_factors=doc.success_factors,
            failure_factors=doc.failure_factors,
            adoption_date=doc.adoption_date.isoformat() if doc.adoption_date else None,
            return_date=doc.return_date.isoformat() if doc.return_date else None,
            days_until_return=doc.days_until_return,
            adopter_satisfaction_score=doc.adopter_satisfaction_score,
            dog_difficulty_level=doc.dog_difficulty_level,
            adopter_experience_level=doc.adopter_experience_level,
            match_score_at_adoption=doc.match_score_at_adoption,
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            created_by=doc.created_by,
        )

    except Exception as e:
        logger.error(f"Error getting outcome: {e}")
        raise HTTPException(status_code=404, detail=f"Outcome not found: {str(e)}")
