import warnings

# Suppress Pydantic warnings from Google Cloud SDK internal classes
# Must be set before importing any Google Cloud libraries
warnings.filterwarnings("ignore", message="Field name .* shadows an attribute in parent")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes, dogs, knowledge, case_studies, chat, applications, outcomes, analytics
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    description="AI-powered veterinary assistance for rescue organizations",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Frontend dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "*",  # Allow all for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routers
api_v1_prefix = "/api/v1"
app.include_router(routes.router, prefix=api_v1_prefix, tags=["health"])
app.include_router(dogs.router, prefix=f"{api_v1_prefix}/dogs", tags=["dogs"])
app.include_router(knowledge.router, prefix=f"{api_v1_prefix}/knowledge", tags=["knowledge"])
app.include_router(
    case_studies.router, prefix=f"{api_v1_prefix}/case-studies", tags=["case-studies"]
)
app.include_router(
    applications.router, prefix=f"{api_v1_prefix}/applications", tags=["applications"]
)
app.include_router(outcomes.router, prefix=f"{api_v1_prefix}/outcomes", tags=["outcomes"])
app.include_router(analytics.router, prefix=f"{api_v1_prefix}/analytics", tags=["analytics"])
app.include_router(chat.router, prefix=f"{api_v1_prefix}/chat", tags=["chat"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to PawBondAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{api_v1_prefix}/health",
    }
