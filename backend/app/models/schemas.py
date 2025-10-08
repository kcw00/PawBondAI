from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class UrgencyLevel(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"


# Dog Models
class DogBase(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    sex: Optional[str] = None
    intake_date: Optional[datetime] = None
    rescue_organization: Optional[str] = None


class DogCreate(DogBase):
    pass


class Dog(DogBase):
    id: str
    medical_history: List[str] = []
    photos: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Article Models
class ArticleBase(BaseModel):
    title: str
    content: str
    source: str
    language: str = "en"
    tags: List[str] = []


class Article(ArticleBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Case Study Models
class CaseStudyBase(BaseModel):
    title: str
    description: str
    diagnosis: str
    treatment: str
    outcome: str
    species: str = "dog"
    breed: Optional[str] = None
    age: Optional[int] = None
    symptoms: List[str] = []
    cost_estimate: Optional[float] = None
    rescue_organization: Optional[str] = None
    origin_country: Optional[str] = None
    origin_language: Optional[str] = "en"


class CaseStudyCreate(CaseStudyBase):
    pass


class CaseStudy(CaseStudyBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Chat Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[List[dict]] = None


class ChatRequest(BaseModel):
    message: str
    dog_id: Optional[str] = None
    image_url: Optional[str] = None
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    message: str
    urgency: Optional[UrgencyLevel] = None
    sources: List[dict] = []
    tool_calls: List[dict] = []


# Search Models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    score: float
    source: Optional[str] = None
