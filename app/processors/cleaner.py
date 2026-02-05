from typing import List, Dict, Callable
import re

class DataCleaner:

    def __init__(self, steps: List[Callable]):
        self.steps = steps
    
    def clean(self, data: List[Dict]) -> List[Dict]:
        for step in self.steps:
            data = step(data)
        return data

def remove_duplicates(data: List[Dict], key_fields: List[str]):
        seen = set()
        unique = []

        for item in data:
            key = tuple(item.get(field) for field in key_fields)
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)

        return unique

def validate_required_fields(data: List[Dict], required_fields: List[str]):
        valid = []

        for item in data:
            if all(item.get(field) for field in required_fields):
                valid.append(item)

        return valid
    
def normalize_text_fields(data: List[Dict], fields: List[str]):
        for item in data:
            for field in fields:
                if item.get(field):
                    item[field] = " ".join(item[field].split()).strip()

        return data

def normalize_price(data: List[Dict], field: str):
        for item in data:
            value = item.get(field)
            if not value:
                continue

            cleaned = re.sub(r"[^\d.]", "", value)
            item[field] = float(cleaned) if cleaned else None

        return data

