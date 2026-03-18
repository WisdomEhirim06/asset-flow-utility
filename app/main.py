"""This is the access point of this API, and the entry point for both the routings and configs"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.exceptions import register_exception_handlers
from app.routers import convert, health


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan: startup & shutdown hooks."""
    # Startup
    print(f"{settings.app_name} v{settings.app_version} starting …")
    yield
    # Shutdown
    print(f"{settings.app_name} shutting down …")


app = FastAPI(
    title=settings.app_name,
    description=(
        "This is a fast, lightweight REST API that serves an utility for converting file formats "
        "(CSV to JSON) and optimizing images (JPG/PNG to WebP)."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
register_exception_handlers(app)


# Routers
app.include_router(health.router)
app.include_router(convert.router)
