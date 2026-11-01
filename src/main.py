from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from src.config import Settings, get_settings


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup (before yield) and once on shutdown (after yield)."""
    s = get_settings()
    print("================================================================")
    print(f"  Environment       : {s.APP_ENV.upper()}")
    print(f"  Config Source     : .env.{s.APP_ENV}")
    print(f"  Ecommerce Base URL: {s.ECOMMERCE_API_BASE_URL}")
    print("================================================================")
    yield
    # ← shutdown logic goes here


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Multi-Agent Business Orchestration",
    description="Enterprise multi-agent orchestration platform.",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def root(settings: Settings = Depends(get_settings)):
    """Health-check — returns current environment info."""
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "ecommerce_api": settings.ECOMMERCE_API_BASE_URL,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
