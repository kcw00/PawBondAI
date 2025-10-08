from fastapi import APIRouter
from typing import List
from datetime import datetime
import uuid

from app.models.schemas import CaseStudy, CaseStudyCreate, SearchRequest
from app.services.elasticsearch_client import es_client
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/search", response_model=List[CaseStudy])
async def search_similar_cases(search_req: SearchRequest):
    """Search similar case studies"""
    query = {
        "query": {
            "multi_match": {
                "query": search_req.query,
                "fields": ["title", "description", "diagnosis", "symptoms"],
            }
        },
        "size": search_req.limit,
    }

    result = es_client.search(index_name=settings.case_studies_index, query=query)

    cases = [CaseStudy(**hit["_source"]) for hit in result["hits"]["hits"]]
    return cases


@router.post("", response_model=CaseStudy)
async def create_case_study(case: CaseStudyCreate):
    """Create a new case study"""
    case_id = str(uuid.uuid4())
    case_dict = case.model_dump()
    case_dict.update({"id": case_id, "created_at": datetime.now()})

    es_client.index_document(
        index_name=settings.case_studies_index, document=case_dict, doc_id=case_id
    )

    return CaseStudy(**case_dict)


@router.get("/{case_id}", response_model=CaseStudy)
async def get_case_study(case_id: str):
    """Get a specific case study by ID"""
    from fastapi import HTTPException

    try:
        result = es_client.get_document(
            index_name=settings.case_studies_index, doc_id=case_id
        )
        return CaseStudy(**result["_source"])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Case study not found: {str(e)}")


@router.get("", response_model=List[CaseStudy])
async def list_case_studies(limit: int = 10):
    """List all case studies"""
    query = {
        "query": {"match_all": {}},
        "size": limit,
        "sort": [{"created_at": {"order": "desc"}}],
    }

    result = es_client.search(index_name=settings.case_studies_index, query=query)

    cases = [CaseStudy(**hit["_source"]) for hit in result["hits"]["hits"]]
    return cases
