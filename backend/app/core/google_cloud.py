import os
from pathlib import Path
from google.cloud import language_v1, documentai_v1, bigquery, storage
from google.oauth2 import service_account
from app.core.config import get_settings

settings = get_settings()

# Resolve base directory for keys
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Service Account Credentials
DOCUMENT_PROCESSOR_CREDENTIALS = service_account.Credentials.from_service_account_file(
    str(BASE_DIR / settings.DOCUMENT_PROCESSOR_SA_KEY)
)

ANALYTICS_ML_CREDENTIALS = service_account.Credentials.from_service_account_file(
    str(BASE_DIR / settings.ANALYTICS_ML_SA_KEY)
)

LANGUAGE_SERVICES_CREDENTIALS = service_account.Credentials.from_service_account_file(
    str(BASE_DIR / settings.LANGUAGE_SERVICES_SA_KEY)
)


def init_google_cloud():
    """Initialize non-GenAI Google Cloud clients (noop for GenAI)."""
    # Keep for symmetry/logging if you want:
    print("✅ Google Cloud services configured (GenAI uses google.genai Client)")


# Client instances
class GoogleCloudClients:
    """Lazy-loaded Google Cloud clients"""

    _language_client = None
    _document_ai_client = None
    _bigquery_client = None
    _storage_client = None

    @classmethod
    def language(cls) -> language_v1.LanguageServiceClient:
        if cls._language_client is None:
            cls._language_client = language_v1.LanguageServiceClient(
                credentials=LANGUAGE_SERVICES_CREDENTIALS
            )
        return cls._language_client

    @classmethod
    def document_ai(cls) -> documentai_v1.DocumentProcessorServiceClient:
        if cls._document_ai_client is None:
            cls._document_ai_client = documentai_v1.DocumentProcessorServiceClient(
                credentials=DOCUMENT_PROCESSOR_CREDENTIALS
            )
        return cls._document_ai_client

    @classmethod
    def bigquery(cls) -> bigquery.Client:
        if cls._bigquery_client is None:
            cls._bigquery_client = bigquery.Client(
                project=settings.gcp_project_id,
                credentials=ANALYTICS_ML_CREDENTIALS,
                location=settings.gcp_region,
            )
        return cls._bigquery_client

    @classmethod
    def storage(cls) -> storage.Client:
        if cls._storage_client is None:
            cls._storage_client = storage.Client(
                project=settings.gcp_project_id,
                credentials=DOCUMENT_PROCESSOR_CREDENTIALS,  # Storage used for document processing
            )
        return cls._storage_client
