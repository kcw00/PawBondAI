from elasticsearch import Elasticsearch
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class ElasticsearchClient:
    def __init__(self):
        self.client = Elasticsearch(
            settings.elastic_endpoint, api_key=settings.elastic_api_key
        )
        logger.info("Elasticsearch client initialized")

    def create_index(self, index_name: str, mappings: dict):
        """Create an index with mappings"""
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name, body=mappings)
            logger.info(f"Created index: {index_name}")
        else:
            logger.info(f"Index {index_name} already exists")

    def index_document(self, index_name: str, document: dict, doc_id: str = None):
        """Index a single document"""
        return self.client.index(index=index_name, document=document, id=doc_id)

    def search(self, index_name: str, query: dict):
        """Search documents"""
        return self.client.search(index=index_name, body=query)

    def get_document(self, index_name: str, doc_id: str):
        """Get a document by ID"""
        return self.client.get(index=index_name, id=doc_id)

    def update_document(self, index_name: str, doc_id: str, document: dict):
        """Update a document"""
        return self.client.update(index=index_name, id=doc_id, body={"doc": document})

    def delete_document(self, index_name: str, doc_id: str):
        """Delete a document"""
        return self.client.delete(index=index_name, id=doc_id)


es_client = ElasticsearchClient()
