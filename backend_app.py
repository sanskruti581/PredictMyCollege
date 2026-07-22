"""
FastAPI backend for PredictMyCollege
- Connects to MongoDB when available
- Falls back to local mock JSON data when MongoDB is unavailable
- Ensures indexes when a real database is present
- Provides `/predict` endpoint to compute confidence buckets

Run:
    uvicorn backend_app:app --reload

Environment:
    MONGO_URI (optional, defaults to mongodb://localhost:27017)
"""
from typing import List, Optional
import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, DESCENDING

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "predictmycollege")
FALLBACK_JSON_PATH = Path(__file__).resolve().parent / "Cleaned_Data_JSON" / "mock_cutoff_sample.json"

client = None
db = None
fallback_cutoffs = []


def load_fallback_records():
    try:
        with open(FALLBACK_JSON_PATH, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return [record for record in payload.get("records", []) if record.get("cutoff_percentage") is not None]
    except Exception as exc:
        print(f"Warning: could not load fallback mock data: {exc}")
        return []

fallback_cutoffs = load_fallback_records()

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
    global client, db
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        db = client[DB_NAME]
        coll = db.cutoffs
        coll.create_index([("branch_name", ASCENDING), ("seat_type", ASCENDING), ("cutoff_percentage", DESCENDING)], name="branch_seattype_cutoff_idx")
        coll.create_index([("college_id", ASCENDING), ("choice_code", ASCENDING), ("seat_type", ASCENDING), ("academic_year", ASCENDING)], name="unique_ingest_idx")
        print("MongoDB connected and indexes ensured on startup")
    except Exception as e:
        db = None
        print("Warning: MongoDB unavailable, using local fallback data:", e)
        if not fallback_cutoffs:
            print("Warning: fallback data is empty or unavailable")


@app.on_event("shutdown")
def close_db_on_shutdown():
    try:
        if client is not None:
            client.close()
    except Exception:
        pass


def get_fallback_records(q, limit):
    results = []
    for doc in fallback_cutoffs:
        if q.get("branch_name") and doc.get("branch_name") not in q["branch_name"]["$in"]:
            continue
        if q.get("seat_type") and doc.get("seat_type") != q["seat_type"]:
            continue
        if q.get("caste_category") and doc.get("caste_category") != q["caste_category"]:
            continue
        if q.get("academic_year"):
            year_prefix = q["academic_year"]["$regex"].lstrip("^")
            if not (doc.get("academic_year") or "").startswith(year_prefix):
                continue
        if q.get("college_name"):
            terms = q["college_name"]["$regex"].split("|")
            name = (doc.get("college_name") or "").lower()
            if not any(term.lower() in name for term in terms):
                continue
        cutoff = doc.get("cutoff_percentage")
        if cutoff is None:
            continue
        results.append(doc)
    results.sort(key=lambda rec: rec.get("cutoff_percentage", 0), reverse=True)
    return results[:limit]


class Flags(BaseModel):
    defence: Optional[bool] = False
    pwd: Optional[bool] = False


class SpecialSeats(BaseModel):
    tfws: Optional[bool] = False
    minority: Optional[bool] = False


class AdvancedFilters(BaseModel):
    college: Optional[str] = None
    branch: Optional[str] = None
    city: Optional[str] = None
    data_year: Optional[str] = None
    safety_zones: Optional[List[str]] = None
    gap_filter: Optional[str] = None


class PredictRequest(BaseModel):
    mode: Optional[str] = "percentage"
    metric_value: Optional[float] = None
    diploma_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    state_merit_rank: Optional[float] = None
    caste_category: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    seat_type: Optional[str] = None
    flags: Optional[Flags] = None
    special_seats: Optional[SpecialSeats] = None
    advanced_filters: Optional[AdvancedFilters] = None
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


def _is_all_filter(value: Optional[str]) -> bool:
    return not value or value.lower().startswith("all ")


def _has_advanced_value(value: Optional[str]) -> bool:
    return bool(value) and not _is_all_filter(value)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    diploma_percentage = req.diploma_percentage
    if diploma_percentage is None and req.mode == "percentage":
        diploma_percentage = req.metric_value
    if diploma_percentage is None:
        raise HTTPException(status_code=422, detail="diploma_percentage is required for percentage-based prediction")

    # build query
    q = {}
    preferred_branches = req.preferred_branches
    if not preferred_branches and req.advanced_filters and _has_advanced_value(req.advanced_filters.branch):
        preferred_branches = [req.advanced_filters.branch]
    if preferred_branches:
        q["branch_name"] = {"$in": preferred_branches}

    if req.category:
        q["caste_category"] = req.category
    elif req.caste_category:
        q["seat_type"] = req.caste_category

    college_terms = list(req.district_filters or [])
    if req.advanced_filters:
        if _has_advanced_value(req.advanced_filters.college):
            college_terms.append(req.advanced_filters.college)
        if _has_advanced_value(req.advanced_filters.city):
            college_terms.append(req.advanced_filters.city)
        if _has_advanced_value(req.advanced_filters.data_year):
            q["academic_year"] = {"$regex": f"^{req.advanced_filters.data_year.split()[0]}"}

    if college_terms:
        q["college_name"] = {"$regex": "|".join(college_terms), "$options": "i"}

    # only consider records with cutoff_percentage
    q["cutoff_percentage"] = {"$ne": None}

    if db is not None:
        try:
            cursor = db.cutoffs.find(q, {"_id": 0}).sort([("cutoff_percentage", -1)]).limit(req.top_k)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Database unavailable: " + str(e))
    else:
        cursor = get_fallback_records(q, req.top_k)

    dream = []
    realistic = []
    safe = []

    for doc in cursor:
        cutoff = doc.get("cutoff_percentage")
        if cutoff is None:
            continue
        delta = round(diploma_percentage - cutoff, 2)
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
