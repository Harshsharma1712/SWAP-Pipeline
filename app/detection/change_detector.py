from typing import List, Dict, Any, Optional
from .base_detector import BaseDetector, ChangeReport, ItemChange
from .hashers import generate_item_id
from .comparators import compare_sets, compare_fields


class ChangeDetector(BaseDetector):
    """
    Core change detection engine.
    
    Compares old and new data to detect:
    - New items
    - Removed items
    - Modified items (with specific field changes)
    """

    def __init__(
        self, 
        key_fields: List[str], 
        compare_fields: List[str] = None,
        price_field: str = None
    ):
        """
        Initialize the change detector.
        
        Args:
            key_fields: Fields that uniquely identify an item (e.g., ["title"])
            compare_fields: Fields to compare for modifications. If None, uses all fields.
            price_field: Optional field name for special price comparison handling
        """
        self.key_fields = key_fields
        self.compare_fields = compare_fields
        self.price_field = price_field

    def _build_index(self, data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Build an index mapping item IDs to items."""
        return {
            generate_item_id(item, self.key_fields): item 
            for item in data
        }

    def detect(self, old_data: List[Dict], new_data: List[Dict]) -> ChangeReport:
        """
        Detect changes between old and new data.
        
        Args:
            old_data: Previously stored data
            new_data: Newly scraped data
            
        Returns:
            ChangeReport with new, removed, and modified items
        """
        report = ChangeReport()

        # Handle edge cases
        if not old_data and not new_data:
            return report
        
        if not old_data:
            # All items are new
            report.new_items = list(new_data)
            return report
        
        if not new_data:
            # All items were removed
            report.removed_items = list(old_data)
            return report

        # Build indexes for O(1) lookups
        old_index = self._build_index(old_data)
        new_index = self._build_index(new_data)

        # Compare sets to find new, removed, and common items
        added_ids, removed_ids, common_ids = compare_sets(
            set(old_index.keys()), 
            set(new_index.keys())
        )

        # Collect new items
        report.new_items = [new_index[item_id] for item_id in added_ids]

        # Collect removed items
        report.removed_items = [old_index[item_id] for item_id in removed_ids]

        # Check modifications in common items
        fields_to_compare = self.compare_fields or list(
            set(old_data[0].keys()) if old_data else set()
        )
        
        for item_id in common_ids:
            old_item = old_index[item_id]
            new_item = new_index[item_id]
            
            changes = compare_fields(old_item, new_item, fields_to_compare)
            
            if changes:
                report.modified_items.append(ItemChange(
                    item_id=item_id,
                    old_item=old_item,
                    new_item=new_item,
                    changed_fields=changes
                ))

        return report

    def has_any_changes(self, old_data: List[Dict], new_data: List[Dict]) -> bool:
        """
        Quick check if there are any changes (without full report).
        
        This is more efficient when you only need to know if something changed.
        """
        report = self.detect(old_data, new_data)
        return report.has_changes
