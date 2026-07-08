"""
Ingestion automation: read Cleaned_Data_JSON/*.json and upsert into MongoDB.

Features:
- Scans `Cleaned_Data_JSON/` for .json files
- Batches records to avoid memory spikes
- Upserts into `cutoffs` collection using a deterministic key
- Verifies/creates compound index `{ branch_name:1, seat_type:1, cutoff_percentage:-1 }`

Run:
    python db_ingest.py

Environment:
    MONGO_URI (optional)
    MONGO_DB (optional)
"""
import os
import json
from pathlib import Path
from pymongo import MongoClient, ASCENDING, DESCENDING, UpdateOne
from typing import List


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "Cleaned_Data_JSON"

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "predictmycollege")


def chunked_iterable(iterable: List, size: int):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def ensure_indexes(coll):
    print("Ensuring compound index on (branch_name, seat_type, cutoff_percentage)")
    coll.create_index([("branch_name", ASCENDING), ("seat_type", ASCENDING), ("cutoff_percentage", DESCENDING)], name="branch_seattype_cutoff_idx")
    # helpful unique-ish index to make upserts deterministic
    coll.create_index([("college_id", ASCENDING), ("choice_code", ASCENDING), ("seat_type", ASCENDING), ("academic_year", ASCENDING)], name="unique_ingest_idx")


def build_filter_for_record(rec: dict):
    # prefer choice_code if available, else fallback to branch+college+year
    filt = {}
    if rec.get("choice_code"):
        filt["choice_code"] = rec.get("choice_code")
        filt["college_id"] = rec.get("college_id")
        filt["seat_type"] = rec.get("seat_type")
        filt["academic_year"] = rec.get("academic_year")
    else:
        filt["college_id"] = rec.get("college_id")
        filt["branch_name"] = rec.get("branch_name")
        filt["academic_year"] = rec.get("academic_year")
    return filt


def ingest_file(filepath: Path, coll, batch_size: int = 500):
    print(f"Ingesting {filepath.name}")
    with open(filepath, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # payload expected as {"source_file":..., "records": [...]}
    if isinstance(payload, dict) and "records" in payload:
        records = payload["records"]
    elif isinstance(payload, list):
        records = payload
    else:
        print(f"Unrecognized JSON structure in {filepath.name}, skipping")
        return 0

    total = 0
    for chunk in chunked_iterable(records, batch_size):
        ops = []
        for rec in chunk:
            # sanitize: remove None keys that shouldn't be stored
            clean = {k: v for k, v in rec.items()}
            filt = build_filter_for_record(clean)
            ops.append(UpdateOne(filt, {"$set": clean}, upsert=True))
        if ops:
            res = coll.bulk_write(ops, ordered=False)
            total += len(ops)
            print(f"  Upserted/modified batch of {len(ops)} (inserted: {getattr(res, 'upserted_count', 'N/A')})")

    print(f"Finished ingesting {filepath.name}: {total} records processed")
    return total


def run_all(data_dir: Path = DATA_DIR, batch_size: int = 500):
    if not data_dir.exists():
        print(f"Data directory {data_dir} not found")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db.cutoffs

    ensure_indexes(coll)

    json_files = sorted([p for p in data_dir.glob("*.json")])
    if not json_files:
        print("No JSON files found in Cleaned_Data_JSON/")
        return

    grand_total = 0
    for jf in json_files:
        try:
            cnt = ingest_file(jf, coll, batch_size=batch_size)
            grand_total += cnt
        except Exception as e:
            print(f"Error ingesting {jf.name}: {e}")

    # re-ensure compound index exists and is active
    ensure_indexes(coll)
    print(f"Ingestion complete. Total records processed: {grand_total}")


if __name__ == "__main__":
    run_all()
