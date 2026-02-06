import hashlib
import json
from typing import List, Dict, Any


def generate_hash(item: Dict[str, Any], fields: List[str] = None) -> str:
    """
    Generate a hash for an item based on specified fields.
    
    Args:
        item: The data item to hash
        fields: Specific fields to include in hash. If None, uses all fields.
        
    Returns:
        MD5 hash string of the item content
    """
    if fields:
        data = {k: item.get(k) for k in fields}
    else:
        data = item

    # Sort keys for consistent hashing
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()


def generate_item_id(item: Dict[str, Any], key_fields: List[str]) -> str:
    """
    Generate a unique identifier for an item based on key fields.
    
    Args:
        item: The data item
        key_fields: Fields that uniquely identify the item
        
    Returns:
        String identifier for set comparisons
    """
    parts = [str(item.get(field, "")) for field in key_fields]
    return "||".join(parts)


def generate_content_hash(item: Dict[str, Any], content_fields: List[str]) -> str:
    """
    Generate a hash of the item's content fields (for detecting modifications).
    
    Args:
        item: The data item
        content_fields: Fields to include in content hash
        
    Returns:
        SHA256 hash of content
    """
    data = {k: item.get(k) for k in content_fields}
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()


def hash_dataset(data: List[Dict[str, Any]]) -> str:
    """
    Generate a hash for an entire dataset.
    
    Args:
        data: List of data items
        
    Returns:
        MD5 hash of the dataset
    """
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()
