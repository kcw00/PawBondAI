from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.schemas import SearchRequest, SearchResult, ArticleResponse, ArticleCreate, Language
from app.models.es_documents import KnowledgeArticle
from app.services.elasticsearch_client import es_client
from app.core.config import get_settings
from app.core.logger import setup_logger
from elasticsearch.dsl import AsyncSearch, Q

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
    """Create a new veterinary knowledge article using DSL"""
    logger.info(f"Creating article: {article.title}")

    # Generate a filename based on the title or use a default
    filename = f"{article.title.lower().replace(' ', '_') if article.title else 'untitled'}.txt"

    # Current timestamp for upload_date
    current_time = datetime.now()

    # ID
    article_id = str(uuid.uuid4())

    try:
        # Create DSL Document instance
        doc = KnowledgeArticle(meta={"id": article_id})
        doc.title = article.title
        doc.content_chunk = article.content
        doc.source = article.source
        doc.filename = filename
        doc.upload_date = current_time
        doc.tags = article.tags
        doc.language = article.language.value if article.language else Language.ENGLISH.value

        # Save the document
        await doc.save(using=es_client.client)

        # Return the response
        return {
            "id": article_id,
            "title": article.title,
            "content": article.content,
            "source": article.source,
            "language": article.language,
            "tags": article.tags,
            "upload_date": current_time,
        }

    except Exception as e:
        logger.error(f"Failed to create article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


# 2. Get an article by ID
# ~~~~worked! testing done by with postman.
@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str = Path(..., description="The ID of the article to retrieve")):
    """Get article by ID using DSL"""
    try:
        # Use DSL Document.get()
        doc = await KnowledgeArticle.get(id=article_id, using=es_client.client)

        return {
            "id": article_id,
            "title": doc.title,
            "content": doc.content_chunk,
            "source": doc.source,
            "language": Language(doc.language) if doc.language else Language.ENGLISH,
            "tags": doc.tags or [],
            "upload_date": doc.upload_date,
        }

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
    """List all articles using DSL, optionally filter by language"""
    # Build search using AsyncSearch
    s = AsyncSearch(using=es_client.client, index=settings.vet_knowledge_index)
    s = s.query("match_all")

    # Add filters if provided
    if source:
        s = s.filter("term", source=source)
    if language:
        s = s.filter("term", language=language.value)
    if tag:
        s = s.filter("term", tags=tag)

    # Sort and paginate
    s = s.sort({"upload_date": {"order": "desc"}})
    s = s[skip : skip + limit]

    try:
        # Execute async search
        response = await s.execute()

        # Convert to ArticleResponse objects
        articles = []
        for hit in response:
            articles.append(
                {
                    "id": hit.meta.id,
                    "title": hit.title,
                    "content": hit.content_chunk,
                    "source": hit.source,
                    "language": Language(hit.language) if hit.language else Language.ENGLISH,
                    "tags": hit.tags or [],
                    "upload_date": hit.upload_date,
                }
            )

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
    """Update an article using DSL"""
    # Check if the article exists
    try:
        doc = await KnowledgeArticle.get(id=article_id, using=es_client.client)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Article not found: {str(e)}")

    try:
        # Update fields
        doc.title = article.title
        doc.content_chunk = article.content
        doc.source = article.source
        doc.tags = article.tags
        doc.language = article.language.value if article.language else Language.ENGLISH.value
        doc.updated_at = datetime.now()

        # Save the updated document
        await doc.save(using=es_client.client)

        return {
            "id": article_id,
            "title": doc.title,
            "content": doc.content_chunk,
            "source": doc.source,
            "language": article.language,
            "tags": doc.tags,
            "upload_date": doc.upload_date,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")


# 5. Delete an article
# ~~~~~worked! testing done by with postman.
@router.delete("/{article_id}")
async def delete_article(
    article_id: str = Path(..., description="The ID of the article to delete")
):
    """Delete an article using DSL"""

    try:
        # Get and delete the article
        doc = await KnowledgeArticle.get(id=article_id, using=es_client.client)
        await doc.delete(using=es_client.client)

        logger.info(f"Article {article_id} deleted successfully")
        return {"message": "Article deleted successfully", "article_id": article_id}

    except Exception as e:
        logger.error(f"Error deleting article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")


# 6. Search articles
# testing needed
@router.get("/search", response_model=List[ArticleResponse])
async def search_articles(
    word: str = Query(..., description="Search word or phrase"),
    fields: List[str] = Query(["content_chunk"], description="Fields to search"),
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of articles to return"),
    language: Optional[Language] = Query(None, description="Filter by language"),
    source: Optional[str] = Query(None, description="Filter by source"),
):
    """Search articles using DSL"""
    # Build search using AsyncSearch
    s = AsyncSearch(using=es_client.client, index=settings.vet_knowledge_index)

    # Add multi-match query
    s = s.query("multi_match", query=word, fields=fields, fuzziness="AUTO")

    # Add filters if provided
    if language:
        s = s.filter("term", language=language.value)
    if source:
        s = s.filter("term", source=source)

    # Sort and paginate
    s = s.sort({"upload_date": {"order": "desc"}})
    s = s[skip : skip + limit]

    try:
        # Execute async search
        response = await s.execute()

        logger.info(f"Search for '{word}' returned {response.hits.total.value} hits")

        # Convert to ArticleResponse objects
        articles = []
        for hit in response:
            articles.append(
                {
                    "id": hit.meta.id,
                    "title": hit.title,
                    "content": hit.content_chunk,
                    "source": hit.source,
                    "language": Language(hit.language) if hit.language else Language.ENGLISH,
                    "tags": hit.tags or [],
                    "upload_date": hit.upload_date,
                }
            )

        logger.info(f"Listed {len(articles)} articles (skip={skip}, limit={limit})")

        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
