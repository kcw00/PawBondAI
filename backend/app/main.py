from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes, dogs, knowledge, case_studies
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
    allow_origins=["*"],  # Configure this properly in production
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


@app.get("/")
async def root():
    return {
        "message": "Welcome to PawBondAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{api_v1_prefix}/health",
    }
