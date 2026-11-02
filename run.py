"""
run.py — Local developer entrypoint and server launcher.

In enterprise production (Docker / Kubernetes), the ASGI server is executed directly:
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

For local development, this script bootstraps the environment and launches Uvicorn
with auto-reload enabled in 'dev' mode.

Usage:
    python run.py               # Runs in dev (or inherits $APP_ENV if set)
    python run.py --env prod    # Runs in prod mode
    python run.py -e prod       # Short flag syntax
"""

import argparse
import os
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Platform Local Development Runner")
    parser.add_argument(
        "-e",
        "--env",
        choices=["dev", "prod", "staging", "test"],
        default=os.getenv("APP_ENV", "dev"),
        help="Target execution environment (default: $APP_ENV or 'dev')",
    )

    args = parser.parse_args()
    os.environ["APP_ENV"] = args.env

    # Import settings after environment variable is established
    from src.config import get_settings

    settings = get_settings()
    is_dev = settings.APP_ENV == "dev"

    print(f"[run.py] Starting local Uvicorn server in {settings.APP_ENV.upper()} mode...")
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=is_dev,
        log_level="info",
    )


if __name__ == "__main__":
    main()
