from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.services.elasticsearch_client import es_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Elasticsearch connection
        es_client.client.ping()
        return {
            "status": "healthy",
            "elasticsearch": "connected",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
