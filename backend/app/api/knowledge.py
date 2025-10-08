from fastapi import APIRouter
from typing import List

from app.models.schemas import SearchRequest, SearchResult
from app.services.elasticsearch_client import es_client
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/search", response_model=List[SearchResult])
async def search_veterinary_knowledge(search_req: SearchRequest):
    """Search veterinary knowledge base (articles, research, documentation)"""
    query = {
        "query": {
            "multi_match": {"query": search_req.query, "fields": ["title^2", "content"]}
        },
        "size": search_req.limit,
    }

    result = es_client.search(index_name=settings.vet_knowledge_index, query=query)

    search_results = []
    for hit in result["hits"]["hits"]:
        search_results.append(
            SearchResult(
                id=hit["_id"],
                title=hit["_source"].get("title", ""),
                content=hit["_source"].get("content", ""),
                score=hit["_score"],
                source=hit["_source"].get("source"),
            )
        )

    return search_results
