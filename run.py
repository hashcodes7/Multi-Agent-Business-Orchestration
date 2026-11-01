"""
run.py — Environment bootstrap & server launcher.

Sets APP_ENV *before* uvicorn imports the app so that config.py
picks up the correct .env.<APP_ENV> file on first load.

Usage:
    python run.py          # defaults to 'dev'
    python run.py prod     # loads .env.prod
"""

import os
import sys

import uvicorn

# Set APP_ENV before anything in src/ is imported.
os.environ.setdefault("APP_ENV", sys.argv[1] if len(sys.argv) > 1 else "dev")

_env = os.environ["APP_ENV"]

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=(_env == "dev"),
        log_level="info",
    )