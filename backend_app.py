"""
FastAPI backend for PredictMyCollege
- Connects to MongoDB
- Ensures indexes
- Provides `/predict` endpoint to compute confidence buckets

Run:
    uvicorn backend_app:app --reload

Environment:
    MONGO_URI (optional, defaults to mongodb://localhost:27017)
"""
from typing import List, Optional
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, DESCENDING

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "predictmycollege")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

app = FastAPI(title="PredictMyCollege API")

# CORS - allow Vite dev server and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_indexes_on_startup():
    try:
        coll = db.cutoffs
        coll.create_index([("branch_name", ASCENDING), ("seat_type", ASCENDING), ("cutoff_percentage", DESCENDING)], name="branch_seattype_cutoff_idx")
        coll.create_index([("college_id", ASCENDING), ("choice_code", ASCENDING), ("seat_type", ASCENDING), ("academic_year", ASCENDING)], name="unique_ingest_idx")
        print("Indexes ensured on startup")
    except Exception as e:
        print("Warning: could not create/verify indexes on startup:", e)


@app.on_event("shutdown")
def close_db_on_shutdown():
    try:
        client.close()
    except Exception:
        pass


class PredictRequest(BaseModel):
    diploma_percentage: float = Field(..., ge=0.0, le=100.0)
    caste_category: Optional[str]
    preferred_branches: Optional[List[str]] = None
    district_filters: Optional[List[str]] = None
    top_k: Optional[int] = 50


class ChoiceOut(BaseModel):
    college_id: str
    college_name: str
    branch_name: str
    choice_code: str
    academic_year: str
    seat_type: Optional[str]
    cutoff_percentage: Optional[float]
    delta: Optional[float]


class PredictResponse(BaseModel):
    dream: List[ChoiceOut]
    realistic: List[ChoiceOut]
    safe: List[ChoiceOut]


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # build query
    q = {}
    if req.preferred_branches:
        q["branch_name"] = {"$in": req.preferred_branches}
    if req.caste_category:
        q["seat_type"] = req.caste_category

    if req.district_filters:
        q["college_name"] = {"$regex": "|".join(req.district_filters), "$options": "i"}

    # only consider records with cutoff_percentage
    q["cutoff_percentage"] = {"$ne": None}

    try:
        cursor = db.cutoffs.find(q, {"_id": 0}).sort([("cutoff_percentage", -1)]).limit(req.top_k)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable: " + str(e))

    dream = []
    realistic = []
    safe = []

    for doc in cursor:
        cutoff = doc.get("cutoff_percentage")
        if cutoff is None:
            continue
        delta = round(req.diploma_percentage - cutoff, 2)
        out = ChoiceOut(
            college_id=doc.get("college_id"),
            college_name=doc.get("college_name"),
            branch_name=doc.get("branch_name"),
            choice_code=doc.get("choice_code"),
            academic_year=doc.get("academic_year"),
            seat_type=doc.get("seat_type"),
            cutoff_percentage=doc.get("cutoff_percentage"),
            delta=delta,
        )
        if delta < 0.0:
            dream.append(out)
        elif 0.0 <= delta <= 3.0:
            realistic.append(out)
        else:
            safe.append(out)

    return PredictResponse(dream=dream, realistic=realistic, safe=safe)


@app.get("/health")
def health():
    return {"status": "ok"}
