"""Direct HTTP Elasticsearch client - bypasses Python client timeout issues"""

import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class ElasticsearchHTTPClient:
    """Direct HTTP client for Elasticsearch using requests library"""

    def __init__(self):
        # Keep the full endpoint URL including port
        self.base_url = settings.elastic_endpoint.rstrip("/")
        self.headers = {
            "Authorization": f"ApiKey {settings.elastic_api_key}",
            "Content-Type": "application/json",
        }
        logger.info(f"HTTP ES Client initialized: {self.base_url}")

    async def index_document(
        self, index_name: str, document: Dict[str, Any], doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Index a document using httpx async"""
        # Convert datetime objects to ISO format strings
        prepared_doc = json.loads(json.dumps(document, default=str))

        # Build URL
        if doc_id:
            url = f"{self.base_url}/{index_name}/_doc/{doc_id}"
        else:
            url = f"{self.base_url}/{index_name}/_doc"

        logger.info(f"POST {url}")

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.post(url, headers=self.headers, json=prepared_doc)
                response.raise_for_status()
                response_data = response.json()
                logger.info(f"✅ Document indexed: {response_data.get('_id')}")
                return response_data

        except httpx.TimeoutException as e:
            logger.error(f"Request timed out: {e}")
            raise Exception(f"Request to Elasticsearch timed out: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"HTTP error from Elasticsearch: {e}")
        except Exception as e:
            logger.error(f"Request failed: {type(e).__name__}: {e}")
            raise Exception(f"Failed to index document: {str(e)}")

    async def get_document(self, index_name: str, doc_id: str) -> Dict[str, Any]:
        """Get a document by ID"""
        url = f"{self.base_url}/{index_name}/_doc/{doc_id}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def search(self, index_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Search documents"""
        url = f"{self.base_url}/{index_name}/_search"

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.post(url, headers=self.headers, json=query)
            response.raise_for_status()
            return response.json()

    async def update_document(
        self, index_name: str, doc_id: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a document"""
        url = f"{self.base_url}/{index_name}/_update/{doc_id}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.post(url, headers=self.headers, json={"doc": document})
            response.raise_for_status()
            return response.json()

    async def delete_document(self, index_name: str, doc_id: str) -> Dict[str, Any]:
        """Delete a document"""
        url = f"{self.base_url}/{index_name}/_doc/{doc_id}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()


# Create singleton instance
es_http_client = ElasticsearchHTTPClient()
