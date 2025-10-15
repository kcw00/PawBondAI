import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Elasticsearch
    ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT")
    ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_REGION = os.getenv("GCP_REGION")

    # Vertex AI
    VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION")

    # Index names
    DOGS_INDEX = "dogs"
    VET_KNOWLEDGE_INDEX = "veterinary_knowledge"
    CASE_STUDIES_INDEX = "case_studies"


# Create the settings instance
settings = Settings()
