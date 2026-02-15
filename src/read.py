import csv
import time
import aiofiles
import os
from typing import Set, Dict

CSV_FILE = os.getenv("CSV_FILE", "ads_monitor.csv")

def load_seen_ids() -> Set[str]:
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["id"] for row in reader}
    except FileNotFoundError:
        return set()

async def save_ad(ad: Dict):
    fieldnames = ["id", "title", "price", "link", "source", "city", "category", "timestamp"]
    ad["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    async with aiofiles.open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        fstat = await f.tell()
        if fstat == 0:
            await f.write(",".join(fieldnames) + "\n")
        row = ",".join(f'"{ad.get(f, "")}"' for f in fieldnames)
        await f.write(row + "\n")
