from app.core.logger import setup_logger
from app.core.config import settings

def main():
    logger = setup_logger()

    logger.info("Starting application")
    logger.info(f"Environment: {settings.ENV}")

    # Placeholder for future pipeline boot
    logger.info("SWMAP is running")

if __name__ == "__main__":
    main()