from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ItemChange:
    """Represents a change in a single item."""
    item_id: str
    old_item: Optional[Dict[str, Any]]
    new_item: Optional[Dict[str, Any]]
    changed_fields: Dict[str, tuple]  # {field: (old_val, new_val)}


@dataclass
class ChangeReport:
    """Report containing all detected changes between old and new data."""
    new_items: List[Dict[str, Any]] = field(default_factory=list)
    removed_items: List[Dict[str, Any]] = field(default_factory=list)
    modified_items: List[ItemChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Check if any changes were detected."""
        return bool(self.new_items or self.removed_items or self.modified_items)

    @property
    def total_changes(self) -> int:
        """Total number of changes detected."""
        return len(self.new_items) + len(self.removed_items) + len(self.modified_items)

    def summary(self) -> str:
        """Get a summary string of changes."""
        parts = []
        if self.new_items:
            parts.append(f"{len(self.new_items)} new")
        if self.removed_items:
            parts.append(f"{len(self.removed_items)} removed")
        if self.modified_items:
            parts.append(f"{len(self.modified_items)} modified")
        return ", ".join(parts) if parts else "No changes"


class BaseDetector(ABC):
    """Abstract base class for change detectors."""

    @abstractmethod
    def detect(self, old_data: List[Dict], new_data: List[Dict]) -> ChangeReport:
        """
        Detect changes between old and new data.
        
        Args:
            old_data: Previously stored data
            new_data: Newly scraped data
            
        Returns:
            ChangeReport containing all detected changes
        """
        pass
