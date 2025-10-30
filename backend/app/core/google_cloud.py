from google.cloud import language_v1, documentai_v1, bigquery, storage
from app.core.config import get_settings

settings = get_settings()

# Use Application Default Credentials (ADC) for Cloud Run
# ADC automatically uses the service account attached to the Cloud Run service
# No need to load credentials from files


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
            # Uses Application Default Credentials
            cls._language_client = language_v1.LanguageServiceClient()
        return cls._language_client

    @classmethod
    def document_ai(cls) -> documentai_v1.DocumentProcessorServiceClient:
        if cls._document_ai_client is None:
            # Uses Application Default Credentials
            cls._document_ai_client = documentai_v1.DocumentProcessorServiceClient()
        return cls._document_ai_client

    @classmethod
    def bigquery(cls) -> bigquery.Client:
        if cls._bigquery_client is None:
            # Uses Application Default Credentials
            cls._bigquery_client = bigquery.Client(
                project=settings.gcp_project_id,
                location=settings.gcp_region,
            )
        return cls._bigquery_client

    @classmethod
    def storage(cls) -> storage.Client:
        if cls._storage_client is None:
            # Uses Application Default Credentials
            cls._storage_client = storage.Client(
                project=settings.gcp_project_id,
            )
        return cls._storage_client
