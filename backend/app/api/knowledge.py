from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.schemas import SearchRequest, SearchResult, ArticleResponse, ArticleCreate, Language
from app.services.elasticsearch_client import es_client
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


# Helper function to convert Elasticsearch document to ArticleResponse
def es_doc_to_article(doc_id: str, source: dict) -> dict:
    # Parse the ISO format string back to datetime if it exists
    upload_date = (
        datetime.fromisoformat(source.get("upload_date"))
        if source.get("upload_date")
        else datetime.now()
    )

    return {
        "id": doc_id,
        "title": source.get("attachment.title"),
        "content": source.get("attachment.content_chunk"),
        "source": source.get("source"),
        "language": source.get("language", Language.ENGLISH.value),
        "tags": source.get("tags", []),
        "upload_date": upload_date,
    }


# 1. Create a new article
# ~~~~~worked! testing done by with postman.
@router.post("", response_model=ArticleResponse)
async def create_article(article: ArticleCreate):
    """Create a new veterinary knowledge article"""
    logger.info(f"Creating article: {article.title}")
    # Generate a filename based on the title or use a default
    filename = f"{article.title.lower().replace(' ', '_') if article.title else 'untitled'}.txt"

    # Current timestamp for upload_date
    current_time = datetime.now()

    # ID
    article_id = str(uuid.uuid4())

    # Prepare the document for Elasticsearch
    doc = {
        "id": article_id,
        "attachment.title": article.title,
        "attachment.content_chunk": article.content,
        "source": article.source,
        "filename": filename,
        "upload_date": current_time.isoformat(),  # Store as ISO format string in Elasticsearch
        "tags": article.tags,
        "language": article.language.value if article.language else Language.ENGLISH.value,
    }

    try:
        # Index the document
        response = await es_client.index_document(
            index_name=settings.vet_knowledge_index, document=doc, id=article_id
        )

        # Return the response with the proper datetime object
        return {
            "id": response["_id"],
            "title": article.title,
            "content": article.content,
            "source": article.source,
            "language": article.language,
            "tags": article.tags,
            "upload_date": current_time,  # Return as datetime object
        }

    except Exception as e:
        logger.error(f"Failed to create article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


# 2. Get an article by ID
# ~~~~worked! testing done by with postman.
@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str = Path(..., description="The ID of the article to retrieve")):
    """Get article by ID"""
    try:
        response = await es_client.get_document(
            index_name=settings.vet_knowledge_index, id=article_id
        )
        return es_doc_to_article(response["_id"], response["_source"])

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Article not found: {str(e)}")


# 3. List all articles with pagination
# ~~~~worked! testing done by with postman.
# need to add filter by source, language, tag
# currently returns all articles.
@router.get("", response_model=List[ArticleResponse])
async def list_articles(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of articles to return"),
    source: Optional[str] = Query(None, description="Filter by source"),
    language: Optional[Language] = Query(None, description="Filter by language"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
):
    """List all articles, optionally filter by language"""
    # Build the query
    query = {"bool": {"must": [{"match_all": {}}]}}

    # Add filters if provided
    if source:
        query["bool"]["must"].append({"term": {"source": source}})
    if language:
        query["bool"]["must"].append({"term": {"language": language.value}})
    if tag:
        query["bool"]["must"].append({"term": {"tags": tag}})

    try:
        response = await es_client.search(
            index_name=settings.vet_knowledge_index,
            body={
                "query": query,
                "from": skip,
                "size": limit,
                "sort": [{"upload_date": {"order": "desc"}}],  # Sort by upload_date descending
            },
        )

        # Convert Elasticsearch results to ArticleResponse objects
        articles = [
            es_doc_to_article(hit["_id"], hit["_source"]) for hit in response["hits"]["hits"]
        ]

        logger.info(f"Listed {len(articles)} articles (skip={skip}, limit={limit})")

        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing articles: {str(e)}")


# 4. Update an article
#  ~~~~worked! testing done by with postman.
@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article: ArticleCreate,
    article_id: str = Path(..., description="The ID of the article to update"),
):
    """Update an article"""
    # Check if the article exists
    try:
        existing = await es_client.get_document(
            index_name=settings.vet_knowledge_index, id=article_id
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Article not found: {str(e)}")

    # Get the existing upload_date or use current time if not available
    existing_source = existing.get("_source", {})
    existing_upload_date = existing_source.get("upload_date")

    # Prepare the updated document
    doc = {
        "attachment.title": article.title,
        "attachment.content_chunk": article.content,
        "source": article.source,
        "filename": existing_source.get("filename")
        or f"{article.title.lower().replace(' ', '_') if article.title else 'untitled'}.txt",
        "upload_date": existing_upload_date or datetime.now().isoformat(),
        "tags": article.tags,
        "language": article.language.value if article.language else Language.ENGLISH.value,
        # Add an updated_at field to track when the article was last modified
        "updated_at": datetime.now().isoformat(),
    }

    try:
        # Update the document
        await es_client.update_document(
            index_name=settings.vet_knowledge_index, document=doc, id=article_id
        )

        # Get the updated document
        updated = await es_client.get_document(
            index_name=settings.vet_knowledge_index, id=article_id
        )

        return es_doc_to_article(updated["_id"], updated["_source"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")


# 5. Delete an article
# ~~~~~worked! testing done by with postman.
@router.delete("/{article_id}")
async def delete_article(
    article_id: str = Path(..., description="The ID of the article to delete")
):
    """Delete an article"""

    try:
        # Check if the article exists
        es_client.get_document(index_name=settings.vet_knowledge_index, id=article_id)

        # Delete the article
        result = await es_client.delete_document(
            index_name=settings.vet_knowledge_index, id=article_id
        )

        if isinstance(result, dict):
            es_result = result.get("result", "")
            logger.info(f"Article {article_id} deletion result: {es_result}")

            if es_result == "deleted":
                return {"message": "Article deleted successfully", "article_id": article_id}
            elif es_result == "not_found":
                raise HTTPException(status_code=404, detail=f"Article not found: {article_id}")

        return {"message": "Article deleted successfully", "article_id": article_id}

    except Exception as e:
        logger.error(f"Error deleting article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")


# 6. Search articles
# testing needed
@router.get("/search", response_model=List[ArticleResponse])
async def search_articles(
    word: str = Query(..., description="Search word or phrase"),
    fields: str = Query(["attachment.content_chunk"], description="Fields to search"),
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of articles to return"),
    language: Optional[Language] = Query(None, description="Filter by language"),
    source: Optional[str] = Query(None, description="Filter by source"),
):
    # Build the search query
    query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": word,
                        "fields": fields,
                        "fuzziness": "AUTO",
                    }
                }
            ],
            "filter": [],
        }
    }

    # Add filters if provided
    if language:
        query["bool"]["filter"].append({"term": {"language": language.value}})
    if source:
        query["bool"]["filter"].append({"term": {"source": source}})

    try:
        response = await es_client.search(
            index_name=settings.vet_knowledge_index,
            body={
                "query": query,
                "from": skip,
                "size": limit,
                "sort": [{"upload_date": {"order": "desc"}}],  # Sort by upload_date descending
            },
        )

        logger.info(f"Search for '{word}' returned {response['hits']['total']['value']} hits")

        # Convert Elasticsearch results to ArticleResponse objects
        articles = [
            es_doc_to_article(hit["_id"], hit["_source"]) for hit in response["hits"]["hits"]
        ]

        logger.info(f"Listed {len(articles)} articles (skip={skip}, limit={limit})")

        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
