# FastAPI + Uvicorn Enterprise Startup — Change Log

Tracks every diff between the last git commit (`HEAD`) and the current working version.
Covers four files: `run.py`, `src/config.py`, `src/main.py` (new), and `requirements.txt`.

---

## 1. `run.py` — Environment Bootstrap & Server Launcher

**Git version responsibility**: Load settings, print banner, call `main()`.  
**New responsibility**: Set `APP_ENV` env var *before* any import, then launch uvicorn. Zero business logic.

### What changed

```diff
-from src.config import setenv
-
-def display_startup_banner(settings):
-    """Displays current environment details on startup."""
-    print("================================================================")
-    print(f"Environment       : {settings.APP_ENV.upper()}")
-    print(f"Config Source     : .env.{settings.APP_ENV}")
-    print(f"Ecommerce Base URL: {settings.ECOMMERCE_API_BASE_URL}")
-    print("================================================================")
-    print("             "+settings.APP_ENV.upper()+ " Environment initialized")
-    print("================================================================")
-
-def main():
-    settings = setenv()
-    display_startup_banner(settings)
-
-if __name__ == "__main__":
-    main()
+"""
+run.py — Environment bootstrap & server launcher.
+Sets APP_ENV *before* uvicorn imports the app so config.py
+picks up the correct .env.<APP_ENV> file on first load.
+
+Usage:
+    python run.py          # defaults to 'dev'
+    python run.py prod     # loads .env.prod
+"""
+
+import os
+import sys
+import uvicorn
+
+# Set APP_ENV before anything in src/ is imported.
+os.environ.setdefault("APP_ENV", sys.argv[1] if len(sys.argv) > 1 else "dev")
+
+_env = os.environ["APP_ENV"]
+
+if __name__ == "__main__":
+    uvicorn.run(
+        "src.main:app",
+        host="0.0.0.0",
+        port=8000,
+        reload=(_env == "dev"),   # hot-reload in dev only
+        log_level="info",
+    )
```

### Why

| Old problem | Fix |
|---|---|
| `setenv()` was imported and called here **and** in `src/main.py` — settings instantiated twice | `run.py` now sets `os.environ["APP_ENV"]` only; `config.py` reads it once on first load |
| `display_startup_banner` was business logic inside the runner | Moved to the `lifespan` context manager in `src/main.py` |
| Env switching required editing source code or setting OS env vars manually | Pass env as CLI arg: `python run.py prod` |
| Hot-reload flag required reading settings in `run.py` | Derived directly from `_env` string — no settings import needed |

---

## 2. `src/config.py` — Settings Singleton

**Git version**: `setenv()` returned a plain `Settings()` on every call — no caching.  
**New version**: `get_settings()` decorated with `@lru_cache` — instantiated exactly **once** per process.

### What changed

```diff
 import os

+from functools import lru_cache
 from pydantic_settings import BaseSettings, SettingsConfigDict


-APP_ENV = os.getenv("MABOP_ENV", "dev")
-ENV_FILE = f".env.{APP_ENV}"
-
-
 class Settings(BaseSettings):
-    APP_ENV: str = APP_ENV
+    APP_ENV: str = "dev"
     ECOMMERCE_API_BASE_URL: str = ""

     model_config = SettingsConfigDict(
-        env_file=ENV_FILE,
-        extra="ignore"
+        env_file=f".env.{os.getenv('APP_ENV', 'dev')}",
+        extra="ignore",
     )

-def setenv() -> Settings:
+
+@lru_cache
+def get_settings() -> Settings:
+    """
+    Returns a cached Settings singleton.
+    Use FastAPI's Depends(get_settings) to inject it into routes.
+    """
     return Settings()
```

### Why

| Old problem | Fix |
|---|---|
| `MABOP_ENV` (custom OS var) was the mechanism — required pre-setting a non-standard var | Standardised to `APP_ENV`, set by `run.py` before any import |
| `APP_ENV` and `ENV_FILE` were module-level globals — evaluated at import time, before `run.py` could set the var | Moved inside `SettingsConfigDict` using `os.getenv()` — evaluated lazily at first `Settings()` call |
| `setenv()` created a new `Settings()` on every call (expensive, inconsistent) | `@lru_cache` makes `get_settings()` a singleton — same object returned on every call |
| Not injectable into FastAPI routes | `get_settings` is now compatible with `Depends(get_settings)` |

---

## 3. `src/main.py` — FastAPI Application *(New File — not in git)*

This file did not exist in git. Previously all app code and the entry point lived in a root-level `main.py`.

### Full file

```python
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from src.config import Settings, get_settings


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


app = FastAPI(
    title="Multi-Agent Business Orchestration",
    description="Enterprise multi-agent orchestration platform.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
async def root(settings: Settings = Depends(get_settings)):
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "ecommerce_api": settings.ECOMMERCE_API_BASE_URL,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
```

### Why each decision was made

| Decision | Reason |
|---|---|
| `lifespan` context manager instead of `@app.on_event("startup")` | `on_event` is **deprecated** since FastAPI 0.93. `lifespan` is the current standard |
| `Depends(get_settings)` in routes | Makes settings injectable and **overridable in tests** via `app.dependency_overrides` |
| No module-level `settings = get_settings()` | Avoids eager evaluation at import time — settings load only when the app actually starts |
| File lives in `src/` not project root | App code belongs inside the package, not alongside config files |

---

## 4. `requirements.txt` — New Dependencies

```diff
+fastapi>=0.115.0
 httpx>=0.27.0
 pydantic>=2.8.0
 pydantic-settings>=2.4.0
 python-dotenv>=1.0.1
 rich>=13.7.1
+uvicorn[standard]>=0.30.0
```

`uvicorn[standard]` includes `watchfiles` (for `--reload`) and `websockets` support.

---

## Summary — Flow Before vs After

### Before (git HEAD)
```
python run.py
  └── setenv()          ← Settings() #1 created here
  └── display_banner()
  └── main()            ← (no server, just prints)
```

### After (current)
```
python run.py [env]
  └── os.environ["APP_ENV"] = env   ← set BEFORE any src/ import
  └── uvicorn.run("src.main:app")
        └── imports src.main
              └── lifespan() calls get_settings()
                    └── @lru_cache → Settings() created ONCE, reused everywhere
```

> **Key principle**: `run.py` owns environment selection. `config.py` owns settings loading. `src/main.py` owns app logic. No file duplicates another's job.
