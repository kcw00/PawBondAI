from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.core.config import get_elasticsearch_client

router = APIRouter()
es_client = get_elasticsearch_client()


@router.get("/health")
def health_check():
    try:
        # Use info() instead of cluster.health() for Elasticsearch Serverless compatibility
        info = es_client.info()

        return {
            "status": "success",
            "message": "Connected to Elasticsearch",
            "elasticsearch_version": info.get("version", {}).get("number", "unknown"),
            "cluster_name": info.get("cluster_name", "unknown"),
        }
    except Exception as e:
        status_code = getattr(e, "status_code", 500)

        raise HTTPException(
            status_code=status_code,
            detail=f"Error connecting to Elasticsearch: {str(e)}",
        )
