from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import get_settings
from backend.app.core.database import init_db
from backend.app.api import issues, health

settings = get_settings()

app = FastAPI(
    title="tensor-hub-ryan-vo",
    description="PHP Issue Analyzer - Analyze PHP interpreter issues from GitHub",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(issues.router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {
        "name": "tensor-hub-ryan-vo",
        "version": "1.0.0",
        "description": "PHP Issue Analyzer",
        "docs": "/docs",
    }