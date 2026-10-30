from src.config import setenv


def display_startup_banner(settings):
    """Displays current environment details on startup."""
    print("================================================================")

    print(f"Environment       : {settings.APP_ENV.upper()}")
    print(f"Config Source     : .env.{settings.APP_ENV}")
    print(f"Ecommerce Base URL: {settings.ECOMMERCE_API_BASE_URL}")
    print("================================================================")
    print("             "+settings.APP_ENV.upper()+ " Environment initialized")
    print("================================================================")


def main():
    settings = setenv()
    display_startup_banner(settings)


if __name__ == "__main__":
    main()