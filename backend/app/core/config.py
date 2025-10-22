from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional
from elasticsearch import Elasticsearch

# Get the backend directory (parent of parent of this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # API Settings
    app_name: str = "PawBondAI"
    debug: bool = False

    # Elasticsearch
    elastic_cloud_id: str
    elastic_endpoint: str
    elastic_api_key: str
    elastic_verify_certs: bool = True
    elastic_ca_certs: Optional[str] = None
    elastic_timeout: int = 60  # seconds

    # Google Cloud
    gcp_project_id: str
    gcp_region: str = "us-west1"
    vertex_ai_location: str = "us-west1"
    doc_ai_processor_id: str

    # Service account credentials
    DOCUMENT_PROCESSOR_SA_KEY: str = "keys/document-processor-sa-key.json"
    ANALYTICS_ML_SA_KEY: str = "keys/analytics-ml-sa-key.json"
    LANGUAGE_SERVICES_SA_KEY: str = "keys/language-services-sa-key.json"

    # Index names
    dogs_index: str = "dogs"
    vet_knowledge_index: str = "veterinary_knowledge"
    case_studies_index: str = "case_studies"
    applications_index: str = "applications"
    outcomes_index: str = "rescue-adoption-outcomes"

    # Optional: Google Cloud Storage
    gcs_bucket_name: str = ""

    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = False
        env_file_encoding = "utf-8"

    # Method to create es client
    def get_elasticsearch_client(self) -> Elasticsearch:
        """Create and return an Elasticsearch client using the settings."""
        # For serverless projects, you can use either cloud_id or endpoint
        if self.elastic_cloud_id:
            # Using cloud_id (Connection alias)
            return Elasticsearch(cloud_id=self.elastic_cloud_id, api_key=self.elastic_api_key)
        else:
            # Using direct endpoint
            return Elasticsearch(hosts=[self.elastic_endpoint], api_key=self.elastic_api_key)


@lru_cache()
def get_settings():
    return Settings()


# Create a singleton es client
@lru_cache()
def get_elasticsearch_client() -> Elasticsearch:
    settings = get_settings()
    return settings.get_elasticsearch_client()
