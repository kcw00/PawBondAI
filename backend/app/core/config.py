from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    app_name: str = "RescueAI"
    debug: bool = False

    # Elasticsearch
    elastic_endpoint: str
    elastic_api_key: str

    # Google Cloud
    gcp_project_id: str
    gcp_region: str = "us-west1"
    vertex_ai_location: str = "us-west1"

    # Index names
    dogs_index: str = "dogs"
    vet_knowledge_index: str = "veterinary_knowledge"
    case_studies_index: str = "case_studies"

    # Optional: Google Cloud Storage
    gcs_bucket_name: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
