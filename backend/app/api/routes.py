from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.core.config import get_elasticsearch_client

router = APIRouter()
es_client = get_elasticsearch_client()


@router.get("/health")
async def health_check():
    try:
        health = await es_client.cluster.health()

        return {
            "status": "success",
            "message": "Connected to Elasticsearch",
            "cluster_status": health["status"],
            "number_of_nodes": health["number_of_nodes"],
            "active_shards": health["active_shards"],
        }
    except Exception as e:
        status_code = getattr(e, "status_code", 500)

        raise HTTPException(
            status_code=status_code,
            detail=f"Error connecting to Elasticsearch: {str(e)}",
        )
