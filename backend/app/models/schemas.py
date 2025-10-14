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
    id: str
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
        from_attributes = True


# Case Study Models
class CaseStudyBase(BaseModel):
    title: str
    diagnosis: str
    treatment_plan: str
    outcome: str
    presenting_complaint: Optional[str] = None
    clinical_history: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnostic_tests: Optional[str] = None
    follow_up: Optional[str] = None
    learning_points: Optional[str] = None

    # Patient info
    patient_species: str = "canine"
    patient_breed: Optional[str] = None
    patient_age_years: Optional[int] = None
    patient_age_months: Optional[int] = None
    patient_age_category: Optional[str] = None
    patient_sex: Optional[str] = None
    patient_weight_kg: Optional[float] = None
    patient_weight_category: Optional[str] = None
    is_juvenile: bool = False
    is_geriatric: bool = False

    # Organization & Location
    rescue_organization: Optional[str] = None
    organization_contact: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None

    # Cost & Classification
    estimated_cost: Optional[float] = None
    cost_breakdown: Optional[str] = None
    disease_category: Optional[str] = None
    urgency_level: Optional[str] = None

    # Metadata
    tags: List[str] = []
    references: Optional[str] = None
    visibility: str = "public"
    is_shareable: bool = True
    date_published: Optional[str] = None


class CaseStudyCreate(CaseStudyBase):
    pass


class CaseStudyResponse(CaseStudyBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

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
