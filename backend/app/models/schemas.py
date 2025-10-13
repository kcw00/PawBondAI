from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class UrgencyLevel(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"


class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    RUSSIAN = "ru"
    HINDI = "hi"


# Dog Models
class DogBase(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    sex: Optional[str] = None
    rescue_date: Optional[str] = None
    adoption_status: Optional[str] = None
    behavioral_notes: Optional[str] = None
    combined_profile: Optional[str] = None


class DogCreate(DogBase):
    pass


class DogResponse(DogBase):
    dog_id: str
    medical_history: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# Article Models
class ArticleBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    language: Language = Language.ENGLISH
    tags: List[str] = []


class ArticleCreate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    id: str
    upload_date: datetime

    class Config:
        orm_mode = True


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
    origin_language: Language = Language.ENGLISH


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
