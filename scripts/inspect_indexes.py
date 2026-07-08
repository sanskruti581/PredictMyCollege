"""
Diagnostic script to verify indexes and explain a sample query on the `cutoffs` collection.

Run:
    python scripts/inspect_indexes.py

It prints the collection indexes and runs an explain() on a representative query to show whether an index is used.
"""
import os
from pymongo import MongoClient
import json

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('MONGO_DB', 'predictmycollege')


def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db.cutoffs

    print(f"Connected to {MONGO_URI} -> DB: {DB_NAME}")

    print("\nIndexes on 'cutoffs':")
    for idx in coll.list_indexes():
        print(json.dumps(idx, default=str, indent=2))

    # Prepare a representative query that should use the compound index
    query = {"branch_name": "Computer Science and Engineering", "seat_type": "GOPEN", "cutoff_percentage": {"$ne": None}}
    sort = [("cutoff_percentage", -1)]

    print("\nRunning explain() for representative query:")
    try:
        expl = coll.find(query).sort(sort).limit(5).explain(verbosity='executionStats')
        print(json.dumps(expl, default=str, indent=2))
        print('\nLook for "IXSCAN" in the explain output to confirm index usage, and check the indexName in the winningPlan.')
    except Exception as e:
        print(f"Failed to run explain(): {e}")


if __name__ == '__main__':
    main()
