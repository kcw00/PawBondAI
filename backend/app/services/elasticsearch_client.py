from elasticsearch import AsyncElasticsearch
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class AsyncElasticsearchClient:
    def __init__(self):
        # Create async client
        if settings.elastic_cloud_id:
            self.client = AsyncElasticsearch(
                cloud_id=settings.elastic_cloud_id,
                api_key=settings.elastic_api_key,
                request_timeout=30,
            )
        else:
            self.client = AsyncElasticsearch(
                hosts=[settings.elastic_endpoint],
                api_key=settings.elastic_api_key,
                request_timeout=30,
            )

        logger.info("Async Elasticsearch client initialized")

    async def ping(self):
        """Test connection"""
        try:
            if await self.client.ping():
                logger.info("✅ Successfully connected to Elasticsearch")
                info = await self.client.info()
                logger.info(f"   Cluster: {info['cluster_name']}")
                return True
            else:
                logger.warning("⚠️ Elasticsearch ping failed")
                return False
        except Exception as e:
            logger.error(f"❌ Elasticsearch connection error: {e}")
            return False

    async def count(self, index_name: str):
        """Get document count for an index"""
        return await self.client.count(index=index_name)

    async def create_index(self, index_name: str, body: dict):
        """Create an index with mappings"""
        exists = await self.client.indices.exists(index=index_name)
        if not exists:
            await self.client.indices.create(index=index_name, body=body)
            logger.info(f"Created index: {index_name}")
        else:
            logger.info(f"Index {index_name} already exists")

    async def index_document(self, index_name: str, document: dict, id: str = None):
        """Index a single document (compatible with DSL Document.save())"""
        return await self.client.index(index=index_name, document=document, id=id)

    async def close(self):
        """Close the async client connection"""
        await self.client.close()

    async def search(self, index_name: str, body: dict):
        """Search documents"""
        return await self.client.search(index=index_name, body=body)

    async def get_document(self, index_name: str, id: str):
        """Get a document by ID"""
        return await self.client.get(index=index_name, id=id)

    async def update_document(self, index_name: str, id: str, document: dict):
        """Update a document"""
        return await self.client.update(index=index_name, id=id, body={"doc": document})

    async def delete_document(self, index_name: str, id: str):
        """Delete a document"""
        return await self.client.delete(index=index_name, id=id)


# Lazy-loaded singleton instance
_es_client = None

def get_es_client() -> AsyncElasticsearchClient:
    """Get or create the Elasticsearch client singleton."""
    global _es_client
    if _es_client is None:
        _es_client = AsyncElasticsearchClient()
    return _es_client

# For backward compatibility, maintain the existing import pattern
# but defer initialization until first use
class _ESClientProxy:
    """Proxy that defers Elasticsearch client initialization until first use."""
    def __getattr__(self, name):
        return getattr(get_es_client(), name)

es_client = _ESClientProxy()
