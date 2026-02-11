"""
Config Loader - Loads pipeline definitions from YAML files.
"""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class PipelineConfig:
    """Pipeline configuration from YAML file."""
    name: str
    enabled: bool
    type: str  # 'static' or 'dynamic'
    url: str
    selectors: Dict[str, Any]
    storage: Dict[str, str]
    change_detection: bool = True
    notifications: bool = True
    
    # Dynamic scraper options
    browser: Dict[str, Any] = field(default_factory=dict)
    pagination: Dict[str, Any] = field(default_factory=dict)
    
    # Source file path
    config_file: str = ""

    @property
    def container_selector(self) -> str:
        """Get the container selector."""
        return self.selectors.get("container", "")
    
    @property
    def field_selectors(self) -> Dict[str, str]:
        """Get field selectors."""
        return self.selectors.get("fields", {})
    
    @property
    def source_name(self) -> str:
        """Get storage source name."""
        return self.storage.get("source_name", self.name.lower().replace(" ", "_"))
    
    @property
    def wait_for(self) -> str:
        """Get wait_for selector for dynamic scrapers."""
        return self.browser.get("wait_for", "")
    
    @property
    def headless(self) -> bool:
        """Get headless mode setting."""
        return self.browser.get("headless", True)
    
    @property
    def pagination_enabled(self) -> bool:
        """Check if pagination is enabled."""
        return self.pagination.get("enabled", False)
    
    @property
    def next_button_selector(self) -> str:
        """Get next button selector for pagination."""
        return self.pagination.get("next_button", "")


class ConfigLoader:
    """
    Loads all pipeline configurations from a directory.
    Each .yaml file represents one pipeline.
    """
    
    def __init__(self, config_dir: str = "config/pipelines"):
        """
        Initialize config loader.
        
        Args:
            config_dir: Directory containing pipeline YAML files
        """
        self.config_dir = Path(config_dir)
        self._configs: List[PipelineConfig] = []
        self._loaded = False
    
    def load_all(self) -> List[PipelineConfig]:
        """
        Load all pipeline configurations from the config directory.
        
        Returns:
            List of PipelineConfig objects
        """
        if self._loaded:
            return self._configs
        
        self._configs = []
        
        if not self.config_dir.exists():
            print(f"⚠️ Config directory not found: {self.config_dir}")
            return self._configs
        
        for yaml_file in sorted(self.config_dir.glob("*.yaml")):
            try:
                config = self._load_file(yaml_file)
                if config:
                    self._configs.append(config)
            except Exception as e:
                print(f"⚠️ Failed to load {yaml_file.name}: {e}")
        
        self._loaded = True
        return self._configs
    
    def _load_file(self, file_path: Path) -> Optional[PipelineConfig]:
        """Load a single YAML file into a PipelineConfig."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data:
            return None
        
        return PipelineConfig(
            name=data.get("name", file_path.stem),
            enabled=data.get("enabled", True),
            type=data.get("type", "static"),
            url=data.get("url", ""),
            selectors=data.get("selectors", {}),
            storage=data.get("storage", {}),
            change_detection=data.get("change_detection", True),
            notifications=data.get("notifications", True),
            browser=data.get("browser", {}),
            pagination=data.get("pagination", {}),
            config_file=str(file_path)
        )
    
    def get_enabled(self) -> List[PipelineConfig]:
        """Get only enabled pipelines."""
        return [c for c in self.load_all() if c.enabled]
    
    def get_by_name(self, name: str) -> Optional[PipelineConfig]:
        """Get a pipeline by name (case-insensitive)."""
        for config in self.load_all():
            if config.name.lower() == name.lower():
                return config
        return None
    
    def reload(self) -> List[PipelineConfig]:
        """Force reload all configurations."""
        self._loaded = False
        return self.load_all()
