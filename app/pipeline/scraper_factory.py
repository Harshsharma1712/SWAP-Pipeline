"""
Scraper Factory - Creates appropriate scraper instances from config.
"""
from app.pipeline.config_loader import PipelineConfig
from app.scrapers.static import StaticScraper
from app.scrapers.dynamic import DynamicScraper


class ScraperFactory:
    """
    Factory for creating scrapers based on pipeline configuration.
    """
    
    @staticmethod
    def create(config: PipelineConfig):
        """
        Create a scraper instance based on config type.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Scraper instance (StaticScraper or DynamicScraper)
        """
        if config.type == "static":
            return StaticScraper(config.url)
        
        elif config.type == "dynamic":
            return DynamicScraper(
                url=config.url,
                wait_for=config.wait_for or None,
                headless=config.headless
            )
        
        else:
            raise ValueError(f"Unknown scraper type: {config.type}")
