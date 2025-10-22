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

    async def semantic_search(
        self,
        index: str,
        query: str,
        semantic_field: str,
        filters: Optional[List[Dict[str, Any]]] = None,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Semantic search on any index using ES inference endpoint
        """
        s = AsyncSearch(using=self.client, index=index)
        s = s.query("semantic", field=semantic_field, query=query)

        # Apply filters
        if filters:
            for filter_dict in filters:
                for key, value in filter_dict.items():
                    s = s.filter("term", **{key: value})

        s = s[0:size]
        response = await s.execute()

        return {
            "hits": [
                {"id": hit.meta.id, "score": hit.meta.score, "data": hit.to_dict()}
                for hit in response
            ],
            "total": response.hits.total.value if hasattr(response.hits.total, "value") else len(response),
        }

    async def hybrid_search(
        self,
        index: str,
        query: str,
        semantic_field: str,
        text_fields: List[str],
        filters: Optional[Dict[str, Any]] = None,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Hybrid search combining semantic + text search with structured filters

        Args:
            filters: Dictionary with structured filter criteria:
                - has_yard: bool
                - yard_size_min: int (minimum square meters)
                - experience_levels: List[str]
                - housing_types: List[str]
                - has_other_pets: bool
                - behavioral_keywords: List[str] (for boosting relevance)
        """
        s = AsyncSearch(using=self.client, index=index)

        # Combine semantic and text queries
        # NOTE: semantic_field should be semantic_text type and use semantic query
        # text_fields should be regular text/keyword fields for multi_match
        semantic_query = Q("semantic", field=semantic_field, query=query)

        # Only create text query if we have non-semantic text fields
        text_query = Q("multi_match", query=query, fields=text_fields, fuzziness="AUTO") if text_fields else None

        # Boost by behavioral keywords if provided
        if filters and "behavioral_keywords" in filters and filters["behavioral_keywords"]:
            behavioral_query = Q(
                "multi_match",
                query=" ".join(filters["behavioral_keywords"]),
                fields=text_fields,  # Use only the text_fields provided, not semantic fields
                fuzziness="AUTO"
            )
            queries = [semantic_query, behavioral_query]
            if text_query:
                queries.append(text_query)
            s = s.query("bool", should=queries)
        else:
            queries = [semantic_query]
            if text_query:
                queries.append(text_query)
            s = s.query("bool", should=queries)

        # Apply structured filters
        if filters:
            # Boolean field: has_yard
            if "has_yard" in filters and filters["has_yard"] is not None:
                s = s.filter("term", has_yard=filters["has_yard"])

            # Range filter: yard_size_min
            if "yard_size_min" in filters and filters["yard_size_min"] is not None:
                s = s.filter("range", yard_size_sqm={"gte": filters["yard_size_min"]})

            # Terms filter: experience_levels (multi-value)
            if "experience_levels" in filters and filters["experience_levels"]:
                s = s.filter("terms", experience_level=filters["experience_levels"])

            # Terms filter: housing_types (multi-value)
            if "housing_types" in filters and filters["housing_types"]:
                s = s.filter("terms", housing_type=filters["housing_types"])

            # Boolean field: has_other_pets
            if "has_other_pets" in filters and filters["has_other_pets"] is not None:
                s = s.filter("term", has_other_pets=filters["has_other_pets"])

        s = s[0:size]
        response = await s.execute()

        return {
            "hits": [
                {"id": hit.meta.id, "score": hit.meta.score, "data": hit.to_dict()}
                for hit in response
            ],
            "total": response.hits.total.value if hasattr(response.hits.total, "value") else len(response),
        }

    async def get_document(self, index: str, doc_id: str) -> Dict[str, Any]:
        """
        Get a document by ID
        """
        s = AsyncSearch(using=self.client, index=index)
        s = s.query("ids", values=[doc_id])
        response = await s.execute()

        if len(response) > 0:
            return response[0].to_dict()
        raise Exception(f"Document {doc_id} not found in index {index}")

    async def aggregations(
        self, index: str, field: str, filters: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Get aggregations for a field
        """
        s = AsyncSearch(using=self.client, index=index)

        # Apply filters
        if filters:
            for filter_dict in filters:
                for key, value in filter_dict.items():
                    s = s.filter("term", **{key: value})

        # Add aggregation
        s.aggs.bucket("field_agg", "terms", field=field)
        response = await s.execute()

        # Parse aggregation results
        if hasattr(response.aggregations, "field_agg"):
            return {
                bucket.key: bucket.doc_count for bucket in response.aggregations.field_agg.buckets
            }
        return {}

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
