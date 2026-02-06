from typing import Optional
from .base_notifier import BaseNotifier
from app.detection.base_detector import ChangeReport


class ConsoleNotifier(BaseNotifier):
    """
    Console-based notifier that prints change reports with color coding.
    
    Uses ANSI escape codes for colored output:
    - Green: New items
    - Red: Removed items
    - Yellow: Modified items
    """

    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True, verbose: bool = True):
        """
        Initialize the console notifier.
        
        Args:
            use_colors: Whether to use ANSI color codes
            verbose: Whether to show detailed item information
        """
        self.use_colors = use_colors
        self.verbose = verbose

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if self.use_colors:
            return f"{color}{text}{self.RESET}"
        return text

    def notify(self, change_report: ChangeReport, source_name: str = None) -> None:
        """Print the change report to console."""
        header = f"Change Report"
        if source_name:
            header += f" for {source_name}"

        print("\n" + "=" * 60)
        print(self._color(f"📊 {header}", self.BOLD + self.BLUE))
        print("=" * 60)

        if not change_report.has_changes:
            print(self._color("✅ No changes detected", self.GREEN))
            print("=" * 60 + "\n")
            return

        print(f"📈 Summary: {change_report.summary()}")
        print("-" * 60)

        # New items
        if change_report.new_items:
            print(self._color(f"\n🆕 NEW ITEMS ({len(change_report.new_items)}):", self.GREEN))
            for item in change_report.new_items[:10]:  # Limit display
                self._print_item(item, self.GREEN)
            if len(change_report.new_items) > 10:
                print(f"   ... and {len(change_report.new_items) - 10} more")

        # Removed items
        if change_report.removed_items:
            print(self._color(f"\n❌ REMOVED ITEMS ({len(change_report.removed_items)}):", self.RED))
            for item in change_report.removed_items[:10]:
                self._print_item(item, self.RED)
            if len(change_report.removed_items) > 10:
                print(f"   ... and {len(change_report.removed_items) - 10} more")

        # Modified items
        if change_report.modified_items:
            print(self._color(f"\n📝 MODIFIED ITEMS ({len(change_report.modified_items)}):", self.YELLOW))
            for change in change_report.modified_items[:10]:
                self._print_modification(change)
            if len(change_report.modified_items) > 10:
                print(f"   ... and {len(change_report.modified_items) - 10} more")

        print("\n" + "=" * 60 + "\n")

    def _print_item(self, item: dict, color: str):
        """Print a single item."""
        if self.verbose:
            # Show key fields
            display = " | ".join(f"{k}: {v}" for k, v in list(item.items())[:3])
            print(f"   {self._color('→', color)} {display}")
        else:
            # Just show first field
            first_val = list(item.values())[0] if item else "Unknown"
            print(f"   {self._color('→', color)} {first_val}")

    def _print_modification(self, change):
        """Print a modified item with field changes."""
        print(f"   {self._color('→', self.YELLOW)} Item: {change.item_id}")
        if self.verbose:
            for field, (old_val, new_val) in change.changed_fields.items():
                print(f"      {field}: {self._color(str(old_val), self.RED)} → {self._color(str(new_val), self.GREEN)}")
