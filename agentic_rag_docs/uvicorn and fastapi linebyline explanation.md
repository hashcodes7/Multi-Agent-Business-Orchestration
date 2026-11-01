# FastAPI + Uvicorn — Line-by-Line Explanation

Every single line across all three implementation files is explained below.  
Files covered: `run.py` · `src/config.py` · `src/main.py`

---

## `run.py`

> **Role**: Set the environment, then hand control to uvicorn. Contains zero app logic.

```python
"""
run.py — Environment bootstrap & server launcher.

Sets APP_ENV *before* uvicorn imports the app so that config.py
picks up the correct .env.<APP_ENV> file on first load.

Usage:
    python run.py          # defaults to 'dev'
    python run.py prod     # loads .env.prod
"""
```
**Lines 1–10 — Module docstring**  
A plain string at the very top of the file (not assigned to any variable). Python treats it as the module's documentation. Explains what this file does and how to use it. Has no runtime effect.

---

```python
import os
```
**Line 12 — Import `os`**  
Brings in Python's built-in `os` module. Used on the next lines to read and write **operating system environment variables** (`os.environ`). Environment variables are key-value pairs the OS passes to every process.

---

```python
import sys
```
**Line 13 — Import `sys`**  
Brings in Python's built-in `sys` module. Used to read `sys.argv` — the list of command-line arguments passed when the script is run. `sys.argv[0]` is always the script name; `sys.argv[1]` onward are user-supplied arguments.

---

```python
import uvicorn
```
**Line 15 — Import `uvicorn`**  
Brings in the uvicorn ASGI server library. uvicorn is the production-grade server that actually listens on a port and serves HTTP requests to the FastAPI app.

---

```python
os.environ.setdefault("APP_ENV", sys.argv[1] if len(sys.argv) > 1 else "dev")
```
**Line 18 — Set `APP_ENV` environment variable (the most important line in this file)**  
Breaking it down piece by piece:

- `sys.argv[1] if len(sys.argv) > 1 else "dev"` — If the user ran `python run.py prod`, `sys.argv[1]` is `"prod"`. If they ran `python run.py` with no args, `len(sys.argv)` is 1, so the fallback `"dev"` is used.
- `os.environ.setdefault("APP_ENV", ...)` — Writes that value into the OS environment under the key `"APP_ENV"`, **but only if `APP_ENV` is not already set**. If the user already exported `APP_ENV=staging` in their shell, this line respects it and does nothing. This is the critical step: it must happen **before** any `src/` module is imported, because `config.py` reads `APP_ENV` at class definition time.

---

```python
_env = os.environ["APP_ENV"]
```
**Line 20 — Read `APP_ENV` into a local variable**  
Reads back the value just set (or already present) from the environment. Stored in `_env` (underscore prefix signals it's a module-private helper). Used on line 27 to decide whether to enable hot-reload. Avoids reading `os.environ` multiple times.

---

```python
if __name__ == "__main__":
```
**Line 22 — Guard block**  
Python sets `__name__` to `"__main__"` only when the file is run directly (`python run.py`). If another file were to `import run`, this block would be skipped. Prevents the server from accidentally starting on import.

---

```python
    uvicorn.run(
```
**Line 23 — Start the uvicorn ASGI server**  
Calls uvicorn's `run()` function, which blocks until the server is stopped. Everything below this line is a keyword argument to that call.

---

```python
        "src.main:app",
```
**Line 24 — App location string**  
A dotted import path telling uvicorn where to find the FastAPI app object. Format is `"module.path:variable_name"`. `src.main` is the Python module (`src/main.py`); `app` is the `FastAPI()` instance inside it. uvicorn imports this module itself, which is why `APP_ENV` must be set *before* this line runs.

---

```python
        host="0.0.0.0",
```
**Line 25 — Bind to all network interfaces**  
`"0.0.0.0"` means "listen on every available network interface" — both `localhost` and the machine's external IP. Using `"127.0.0.1"` would restrict to local-only access. `"0.0.0.0"` is standard for containerised/server deployments.

---

```python
        port=8000,
```
**Line 26 — Listen on port 8000**  
The TCP port the server listens on. `8000` is the FastAPI/uvicorn community convention for development. In production this is typically handled by a reverse proxy (nginx) on port 80/443.

---

```python
        reload=(_env == "dev"),
```
**Line 27 — Conditional hot-reload**  
`_env == "dev"` evaluates to `True` when the environment is `dev`, `False` otherwise. When `reload=True`, uvicorn watches the source files and automatically restarts the server on every save — essential in development. In `prod`, hot-reload is off because it adds overhead and instability.

---

```python
        log_level="info",
```
**Line 28 — Log verbosity**  
Sets uvicorn's logging level. `"info"` shows startup messages and every HTTP request. Other options: `"debug"` (very verbose), `"warning"` (quiet), `"error"` (errors only).

---
---

## `src/config.py`

> **Role**: Define the `Settings` model and expose a cached singleton getter. The only file that knows about `.env.*` files.

```python
import os
```
**Line 1 — Import `os`**  
Needed to call `os.getenv()` on line 12 to read the `APP_ENV` environment variable that `run.py` set.

---

```python
from functools import lru_cache
```
**Line 3 — Import `lru_cache`**  
`lru_cache` (Least Recently Used cache) is a Python standard-library decorator. When applied to a function, it caches the return value after the first call and returns the cached result on every subsequent call, without re-executing the function body. This is what makes `get_settings()` a singleton.

---

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
```
**Line 4 — Import pydantic-settings classes**  
- `BaseSettings` — A pydantic base class that automatically reads field values from environment variables and `.env` files in addition to Python defaults.
- `SettingsConfigDict` — A typed dictionary used to configure how `BaseSettings` behaves (which env file to load, what to do with unknown fields, etc.).

---

```python
class Settings(BaseSettings):
```
**Line 7 — Define the Settings model**  
Inherits from `BaseSettings`. pydantic-settings automatically validates all field values on instantiation and can load them from environment variables or an env file. Any class attribute defined below becomes a validated setting.

---

```python
    APP_ENV: str = "dev"
```
**Line 8 — `APP_ENV` field with default**  
Declares a string field named `APP_ENV`. Default is `"dev"`. When `Settings()` is instantiated, pydantic looks for an environment variable named `APP_ENV` (case-insensitive by default) and uses its value if found, otherwise falls back to `"dev"`.

---

```python
    ECOMMERCE_API_BASE_URL: str = ""
```
**Line 9 — `ECOMMERCE_API_BASE_URL` field**  
Declares the base URL for the ecommerce API. Default is an empty string. Its actual value is loaded from whichever `.env.*` file is configured below.

---

```python
    model_config = SettingsConfigDict(
```
**Line 11 — Start of model configuration**  
`model_config` is a special pydantic attribute (not a regular field). Assigning a `SettingsConfigDict` here tells pydantic how to behave when loading settings. Arguments follow on the next lines.

---

```python
        env_file=f".env.{os.getenv('APP_ENV', 'dev')}",
```
**Line 12 — Dynamic env file selection (the core of the env-switching mechanism)**  
- `os.getenv('APP_ENV', 'dev')` — Reads `APP_ENV` from the OS environment. Returns `'dev'` if not set.  
- `f".env.{...}"` — Builds the filename: `.env.dev`, `.env.prod`, etc.  
- `env_file=...` — Tells `BaseSettings` to load variables from this file before checking OS env vars.  
- **Why it works**: `run.py` sets `APP_ENV` in the OS env *before* this module is imported, so by the time Python evaluates this f-string, `APP_ENV` already has the correct value.

---

```python
        extra="ignore",
```
**Line 13 — Ignore unknown fields**  
If the `.env` file contains keys that are not declared as fields in `Settings` (e.g. editor metadata, comments-as-keys), pydantic will silently ignore them instead of raising a `ValidationError`. Keeps the config tolerant of extra values.

---

```python
@lru_cache
```
**Line 17 — Cache decorator**  
Applied to `get_settings()` below. After the first call, `lru_cache` stores the returned `Settings` object in memory. Every subsequent call to `get_settings()` — whether from a route, a test, or another module — gets back the exact same object without re-reading the env file or re-instantiating pydantic. Effectively turns the function into a singleton factory.

---

```python
def get_settings() -> Settings:
```
**Line 18 — Settings getter function**  
A plain function that returns a `Settings` instance. The `-> Settings` is a type hint telling IDEs and type checkers what this function returns. Combined with `@lru_cache` above, this is the **only** place in the codebase where `Settings()` is ever constructed.

---

```python
    """
    Returns a cached Settings singleton.

    The @lru_cache ensures Settings() is only instantiated once per process,
    regardless of how many routes or modules call get_settings().
    Use FastAPI's Depends(get_settings) to inject it into routes.
    """
```
**Lines 19–25 — Function docstring**  
Documents the behaviour and intended usage pattern of this function. Has no runtime effect.

---

```python
    return Settings()
```
**Line 26 — Instantiate and return Settings**  
The only line that actually creates the `Settings` object. On the very first call, pydantic reads the env file and OS environment, validates all fields, and returns the object. `@lru_cache` then stores that object, so this line only runs **once** per process.

---
---

## `src/main.py`

> **Role**: Define the FastAPI app, its startup behaviour, and all HTTP routes.

```python
from contextlib import asynccontextmanager
```
**Line 1 — Import `asynccontextmanager`**  
A decorator from Python's standard library that turns an `async` generator function (one that uses `yield`) into an async context manager. Used on line 12 to define the `lifespan` function, which FastAPI calls on startup and shutdown.

---

```python
from fastapi import Depends, FastAPI
```
**Line 3 — Import FastAPI core tools**  
- `FastAPI` — The main application class. Creating an instance of it gives you the ASGI app object that uvicorn serves.
- `Depends` — FastAPI's dependency injection system. Wrapping a function with `Depends(fn)` tells FastAPI to call `fn` and pass its return value as the argument — used to inject `Settings` into routes.

---

```python
from src.config import Settings, get_settings
```
**Line 5 — Import settings from config module**  
- `get_settings` — The cached getter function, used in `lifespan` and as a `Depends()` dependency in routes.
- `Settings` — The pydantic model class, used as a type hint in route function signatures so IDEs know what `settings` is.

---

```python
@asynccontextmanager
```
**Line 12 — Apply context manager decorator**  
Transforms the `async def lifespan(...)` function below into an async context manager. FastAPI will `await` entering it on startup and `await` exiting it on shutdown. Without this decorator, the function would just be a regular async generator.

---

```python
async def lifespan(app: FastAPI):
```
**Line 13 — Define the lifespan handler**  
- `async def` — This is a coroutine; uvicorn's async event loop runs it.
- `app: FastAPI` — FastAPI passes itself as the argument when calling this. Not used in the body here, but available if you need to attach state to `app.state`.
- This function replaces the now-deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")` pattern.

---

```python
    """Runs once on startup (before yield) and once on shutdown (after yield)."""
```
**Line 14 — Docstring**  
Explains the two halves of a lifespan function. No runtime effect.

---

```python
    s = get_settings()
```
**Line 15 — Get the settings singleton**  
Calls `get_settings()`. Because of `@lru_cache`, this is guaranteed to return the same `Settings` object that was (or will be) used everywhere else. No new env file is read; no new pydantic object is constructed.

---

```python
    print("================================================================")
    print(f"  Environment       : {s.APP_ENV.upper()}")
    print(f"  Config Source     : .env.{s.APP_ENV}")
    print(f"  Ecommerce Base URL: {s.ECOMMERCE_API_BASE_URL}")
    print("================================================================")
```
**Lines 16–20 — Startup banner**  
Prints a formatted block to stdout when the server starts. Confirms which environment is active, which file was loaded, and what the API base URL resolved to. Pure informational output — no side effects on the app.

---

```python
    yield
```
**Line 21 — The dividing line between startup and shutdown**  
Everything **before** `yield` runs on startup (when uvicorn starts). Everything **after** `yield` runs on shutdown (when uvicorn receives a stop signal). The app serves requests while execution is "paused" here at `yield`. This is where you would `await` cleanup tasks like closing database connections.

---

```python
    # ← shutdown logic goes here
```
**Line 22 — Shutdown placeholder comment**  
Signals where to add teardown code (e.g. `await db.disconnect()`, `await cache.close()`). Has no runtime effect.

---

```python
app = FastAPI(
```
**Line 29 — Create the FastAPI application instance**  
Instantiates the main app object. This is the ASGI-callable that uvicorn was pointed at via `"src.main:app"` in `run.py`. All routes, middleware, and event handlers are registered on this object.

---

```python
    title="Multi-Agent Business Orchestration",
```
**Line 30 — API title**  
Sets the human-readable name of the API. Appears in the auto-generated OpenAPI schema and on the `/docs` (Swagger UI) page header.

---

```python
    description="Enterprise multi-agent orchestration platform.",
```
**Line 31 — API description**  
A longer description shown in the Swagger UI. Can be multi-line Markdown.

---

```python
    version="0.1.0",
```
**Line 32 — API version**  
The version string embedded in the OpenAPI schema. Used by API clients and documentation portals to track breaking changes.

---

```python
    lifespan=lifespan,
```
**Line 33 — Register the lifespan handler**  
Tells FastAPI to use the `lifespan` async context manager defined above for startup/shutdown. Without this line, the startup banner would never print and no teardown logic would run.

---

```python
@app.get("/", tags=["Health"])
```
**Line 41 — Register a GET route at `/`**  
- `@app.get("/")` — Decorates the function below as the handler for `GET /` requests.
- `tags=["Health"]` — Groups this route under the "Health" section in Swagger UI (`/docs`). Purely organisational.

---

```python
async def root(settings: Settings = Depends(get_settings)):
```
**Line 42 — Route handler with injected settings**  
- `async def` — The handler is a coroutine, compatible with uvicorn's async event loop.
- `settings: Settings` — Type hint; tells the IDE this parameter is a `Settings` object.
- `= Depends(get_settings)` — FastAPI's DI system. Before calling `root()`, FastAPI calls `get_settings()` and passes the result as `settings`. Because `get_settings` is `@lru_cache`-d, it returns the already-cached singleton — no re-instantiation. This also makes the route **testable**: in tests you can do `app.dependency_overrides[get_settings] = lambda: mock_settings`.

---

```python
    """Health-check — returns current environment info."""
```
**Line 43 — Route docstring**  
Appears as the route description in Swagger UI (`/docs`). No runtime effect.

---

```python
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "ecommerce_api": settings.ECOMMERCE_API_BASE_URL,
    }
```
**Lines 44–48 — Return JSON response**  
FastAPI automatically serialises the returned Python dictionary to a JSON HTTP response with `Content-Type: application/json`. `settings.APP_ENV` and `settings.ECOMMERCE_API_BASE_URL` are the validated values loaded from the env file at startup.

---

```python
@app.get("/health", tags=["Health"])
```
**Line 51 — Register a GET route at `/health`**  
Same pattern as line 41. A dedicated liveness endpoint — a standard convention used by load balancers, Kubernetes probes, and monitoring tools to check if the service is alive.

---

```python
async def health():
```
**Line 52 — Health route handler (no dependencies)**  
No `Depends()` here — this route intentionally has no dependencies so it remains as fast and side-effect-free as possible. A health check should never fail due to database or config issues.

---

```python
    return {"status": "healthy"}
```
**Line 53 — Minimal health response**  
Returns the simplest possible confirmation that the process is running and the event loop is responsive. Monitoring tools check for HTTP 200 + this body.
