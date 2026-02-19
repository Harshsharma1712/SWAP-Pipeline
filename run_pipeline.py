"""
Non-interactive runner for CI/CD
Runs all enabled pipelines
"""

from app.core.logger import setup_logger
from app.pipeline.config_loader import ConfigLoader
from app.pipeline.pipeline_runner import PipelineRunner


def main():
    logger = setup_logger()
    logger.info("CI/CD pipeline runner started")

    loader = ConfigLoader("config/pipelines")
    pipelines = loader.get_enabled()

    if not pipelines:
        logger.warning("No enabled pipelines found")
        return

    for config in pipelines:
        try:
            logger.info(f"▶ Running pipeline: {config.name}")
            PipelineRunner(config).run()
        except Exception as e:
            logger.error(f"❌ Pipeline '{config.name}' failed: {e}")

    logger.info("All pipelines execution complete")

if __name__ == "__main__":
    main()

