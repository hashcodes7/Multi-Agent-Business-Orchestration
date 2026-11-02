from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from src.config import Settings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that runs once on startup and once on shutdown.
    Replaces deprecated @app.on_event handlers.
    """
    settings = get_settings()
    print("=" * 64)
    print("  Multi-Agent Business Orchestration Platform Starting")
    print(f"  Environment       : {settings.APP_ENV.upper()}")
    print(f"  Ecommerce Base URL: {settings.ECOMMERCE_API_BASE_URL}")
    print("=" * 64)
    yield
    print("Shutting down Multi-Agent Business Orchestration Platform cleanly...")


app = FastAPI(
    title="Multi-Agent Business Orchestration",
    description="Enterprise multi-agent orchestration platform.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
async def root(settings: Settings = Depends(get_settings)):
    """Health-check endpoint returning the active environment configuration."""
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "ecommerce_api": settings.ECOMMERCE_API_BASE_URL,
    }


@app.get("/health", tags=["Health"])
async def health():
    """Liveness probe endpoint for Kubernetes / load balancers."""
    return {"status": "healthy"}
