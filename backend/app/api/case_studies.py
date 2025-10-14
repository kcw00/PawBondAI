from fastapi import APIRouter, HTTPException, Path, Query
from typing import List
from datetime import datetime
import uuid

from app.models.schemas import CaseStudyResponse, CaseStudyCreate, SearchRequest
from app.services.elasticsearch_client import es_client
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


# 1. Create a case study
# ~~~~worked! testing done by with postman.
@router.post("", response_model=CaseStudyResponse)
async def create_case_study(case: CaseStudyCreate):
    """Create a new case study"""
    case_id = str(uuid.uuid4())
    case_dict = case.model_dump()
    case_dict.update(
        {
            "id": case_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    )

    try:
        result = await es_client.index_document(
            index_name=settings.case_studies_index, document=case_dict, id=case_id
        )
        logger.info(f"Case study created and indexed with ID: {case_id}")
        logger.debug(f"Indexing result: {result}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating case study: {str(e)}")
    return CaseStudyResponse(**case_dict)


# 2. Get a case study by ID
# ~~~~worked! testing done by with postman.
@router.get("/{case_id}", response_model=CaseStudyResponse)
async def get_case_study(case_id: str):
    """Get a specific case study by ID"""

    try:
        result = await es_client.get_document(index_name=settings.case_studies_index, id=case_id)
        case_data = result["_source"]

        # Ensure id field exists
        if "id" not in case_data:
            case_data["id"] = result["_id"]

        return CaseStudyResponse(**case_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Case study not found: {str(e)}")


# 3. List all case studies
# ~~~~worked! testing done by with postman.
@router.get("", response_model=List[CaseStudyResponse])
async def list_case_studies(limit: int = 10):
    """List all case studies"""
    query = {
        "query": {"match_all": {}},
        "size": limit,
    }

    try:
        result = await es_client.search(index_name=settings.case_studies_index, body=query)

        cases = []
        for hit in result["hits"]["hits"]:
            case_data = hit["_source"]
            # Ensure id field exists
            if "id" not in case_data:
                case_data["id"] = hit["_id"]
            cases.append(CaseStudyResponse(**case_data))

        return cases
    except Exception as e:
        logger.error(f"Error listing case studies: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing case studies: {str(e)}")


# 4. Search case studies
# testing needed
@router.post("/search", response_model=List[CaseStudyResponse])
async def search_similar_cases(search_req: SearchRequest):
    """Search similar case studies"""
    query = {
        "query": {
            "multi_match": {
                "query": search_req.query,
                "fields": ["title", "diagnosis", "presenting_complaint", "tags"],
            }
        },
        "size": search_req.limit,
    }

    try:
        result = await es_client.search(index_name=settings.case_studies_index, body=query)

        cases = []
        for hit in result["hits"]["hits"]:
            case_data = hit["_source"]
            # Ensure id field exists
            if "id" not in case_data:
                case_data["id"] = hit["_id"]
            cases.append(CaseStudyResponse(**case_data))

        return cases
    except Exception as e:
        logger.error(f"Error searching case studies: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching case studies: {str(e)}")
