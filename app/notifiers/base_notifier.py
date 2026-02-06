from abc import ABC, abstractmethod
from app.detection.base_detector import ChangeReport


class BaseNotifier(ABC):
    """Abstract base class for change notification handlers."""

    @abstractmethod
    def notify(self, change_report: ChangeReport, source_name: str = None) -> None:
        """
        Send notification about detected changes.
        
        Args:
            change_report: The ChangeReport containing detected changes
            source_name: Optional identifier for the data source
        """
        pass
