from app.core.config import get_settings
from app.services.elasticsearch_client import es_client
from app.models.es_documents import KnowledgeArticle, CaseStudy, Dog
from elasticsearch.dsl import AsyncSearch, Q
from typing import List, Dict, Any, Optional
import logging, datetime

logger = logging.getLogger(__name__)


class ElasticsearchService:
    def __init__(self):
        self.client = es_client.client
        self.settings = get_settings()

    async def hybrid_search_knowledge(
        self, query: str, size: int = 5, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search on knowledge base using ES inference endpoint
        Note: ES handles embeddings automatically via semantic_text fields
        """
        # Build semantic search using AsyncSearch
        s = AsyncSearch(using=self.client, index=self.settings.vet_knowledge_index)

        # Use semantic query (ES inference endpoint generates embeddings automatically)
        s = s.query("semantic", field="content_chunk", query=query)

        # Add language filter if specified
        if language:
            s = s.filter("term", language=language)

        s = s[0:size]

        # Execute the search
        response = await s.execute()

        return [
            {**hit.to_dict(), "relevance_score": hit.meta.score, "article_id": hit.meta.id}
            for hit in response
        ]

    async def vector_search_cases(self, symptoms: List[str], size: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for similar cases using ES inference endpoint
        Note: ES handles embeddings automatically via semantic_text fields
        """
        query_text = " ".join(symptoms)

        # Build semantic search using AsyncSearch
        s = AsyncSearch(using=self.client, index=self.settings.case_studies_index)
        s = s.query("semantic", field="presenting_complaint", query=query_text)
        s = s[0:size]

        response = await s.execute()

        return [hit.to_dict() for hit in response]

    async def get_dog_profile(self, dog_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve dog profile using DSL"""
        try:
            # Use DSL Document.get()
            dog = await Dog.get(id=dog_id, using=self.client)
            return dog.to_dict()
        except:
            return None

    async def search_dogs(self, query: str, size: int = 10, filters=None) -> List[Dict[str, Any]]:
        """Search dogs by name, breed, or rescue organization using AsyncSearch"""
        # Build search using AsyncSearch
        s = AsyncSearch(using=self.client, index=self.settings.dogs_index)
        if query:
            s = s.query(
                "multi_match",
                query=query,
                fields=["name^3", "breed^2", "rescue_organization"],
                type="best_fields",
                fuzziness="AUTO",
            )
            s = s[:size]  # Limit results
        if filters:
            if "breed" in filters:
                s = s.filter("term", **{"basic_info.breed.keyword": filters["breed"]})
            if "status" in filters:
                s = s.filter("term", **{"current_status.keyword": filters["status"]})
            if "age" in filters:
                s = s.filter("term", **{"basic_info.age.keyword": filters["age"]})

        # Execute async search
        response = await s.execute()

        return [hit.to_dict() for hit in response]

    async def get_realtime_analytics_from_es(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics for dashboard using Elasticsearch DSL

        Returns:
        - Overall success rate
        - Success rate by experience level
        - Success rate by dog difficulty
        - Average days until return (for failures)
        """
        try:
            # Use AsyncSearch to get stats from Elasticsearch
            s = AsyncSearch(using=self.client, index=self.settings.outcomes_index)
            total_count = await s.count()

            # Success count
            success_s = s.filter("term", outcome="success")
            success_count = await success_s.count()

            # Calculate success rate
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0

            analytics = {
                "total_adoptions": total_count,
                "successful_adoptions": success_count,
                "overall_success_rate": round(success_rate, 2),
                "data_source": "Elasticsearch (real-time)",
                "last_updated": datetime.datetime.now().isoformat(),
            }

            logger.info("Retrieved advanced analytics from Elasticsearch")

            return analytics

        except Exception as e:
            logger.error(f"Error getting advanced analytics: {e}")
            raise


es_service = ElasticsearchService()


def get_elasticsearch_service():
    return es_service
