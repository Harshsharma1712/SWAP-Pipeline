import csv
import os
from typing import List, Dict

def save_to_csv(filename: str, data: List[Dict]):
    if not data:
        return 
    
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
