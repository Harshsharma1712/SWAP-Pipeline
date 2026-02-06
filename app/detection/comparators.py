import re
from typing import List, Dict, Any, Tuple, Set, Optional
from dataclasses import dataclass


@dataclass
class PriceChange:
    """Represents a price change."""
    old_price: Optional[float]
    new_price: Optional[float]
    
    @property
    def difference(self) -> float:
        """Calculate price difference."""
        if self.old_price is None or self.new_price is None:
            return 0.0
        return self.new_price - self.old_price
    
    @property
    def percentage_change(self) -> float:
        """Calculate percentage change."""
        if not self.old_price:
            return 0.0
        return ((self.new_price or 0) - self.old_price) / self.old_price * 100


def compare_sets(old_ids: Set[str], new_ids: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Compare two sets of IDs to find additions, removals, and common items.
    
    Args:
        old_ids: Set of old item identifiers
        new_ids: Set of new item identifiers
        
    Returns:
        Tuple of (added, removed, common) sets
    """
    added = new_ids - old_ids
    removed = old_ids - new_ids
    common = old_ids & new_ids
    return added, removed, common


def compare_fields(
    old_item: Dict[str, Any], 
    new_item: Dict[str, Any], 
    fields: List[str]
) -> Dict[str, Tuple[Any, Any]]:
    """
    Compare specific fields between two items.
    
    Args:
        old_item: Previous version of item
        new_item: New version of item
        fields: Fields to compare
        
    Returns:
        Dictionary of changed fields: {field: (old_val, new_val)}
    """
    changes = {}
    for field in fields:
        old_val = old_item.get(field)
        new_val = new_item.get(field)
        if old_val != new_val:
            changes[field] = (old_val, new_val)
    return changes


def parse_price(price_str: str) -> Optional[float]:
    """
    Parse a price string to float.
    
    Args:
        price_str: Price string (e.g., "$199.99", "Rs. 1,299")
        
    Returns:
        Float price or None if parsing fails
    """
    if not price_str:
        return None
    # Remove currency symbols and commas
    cleaned = re.sub(r"[^\d.]", "", str(price_str))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def detect_price_change(
    old_item: Dict[str, Any], 
    new_item: Dict[str, Any], 
    price_field: str
) -> Optional[PriceChange]:
    """
    Detect price changes between items.
    
    Args:
        old_item: Previous item
        new_item: New item
        price_field: Name of the price field
        
    Returns:
        PriceChange object if price changed, None otherwise
    """
    old_price = parse_price(str(old_item.get(price_field, "")))
    new_price = parse_price(str(new_item.get(price_field, "")))
    
    if old_price != new_price:
        return PriceChange(old_price=old_price, new_price=new_price)
    return None


def normalize_for_comparison(value: Any) -> str:
    """
    Normalize a value for comparison (strips whitespace, lowercases).
    
    Args:
        value: Any value to normalize
        
    Returns:
        Normalized string representation
    """
    if value is None:
        return ""
    return " ".join(str(value).lower().split())
