PredictMyCollege
=================

This repository contains the core ETL parser and a FastAPI backend for predicting college cutoffs.

Setup
-----

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Place official CAP PDFs into `Previous_yrs_Result/`.

3. Run the parser:

```bash
python batch_parser.py
```

Cleaned JSON files will be written into `Cleaned_Data_JSON/`.

4. Start the API:

```bash
uvicorn backend_app:app --reload
```

API
---

POST /predict
- Request JSON: `{ "diploma_percentage": 85.5, "caste_category": "GOPEN", "preferred_branches": ["Computer Science and Engineering"], "district_filters": ["Amravati"] }`
- Response: grouped choices in `dream`, `realistic`, and `safe` buckets.

Notes
-----
- The parser is a best-effort state-machine using `pdfplumber` text extraction. PDF layouts vary; results may need manual post-cleaning.
- The FastAPI app expects a running MongoDB instance on `mongodb://localhost:27017` by default. Set `MONGO_URI` to change.

Full runbook (unified)
----------------------

1) ETL / Parser

 - Place official CAP PDF files inside `Previous_yrs_Result/` (or use the provided mock file at `Cleaned_Data_JSON/mock_cutoff_sample.json` for testing).
 - Run the batch parser to extract JSON datasets:

```bash
python batch_parser.py
```

2) Ingestion into MongoDB

 - Ensure MongoDB is running locally (or set `MONGO_URI` environment variable to your DB URI).
 - Ingest all JSON files from `Cleaned_Data_JSON/` into the `cutoffs` collection:

```bash
python db_ingest.py
```

3) Diagnostics / Index verification

 - Confirm indexes and inspect a query plan (helpful to verify the compound index `{ branch_name:1, seat_type:1, cutoff_percentage:-1 }`):

```bash
python scripts/inspect_indexes.py
```

4) Backend (FastAPI)

 - Start the API server (defaults to `mongodb://localhost:27017` unless `MONGO_URI` is set):

```bash
uvicorn backend_app:app --reload
```

 - The API exposes `POST /predict` which accepts the student profile and returns `dream`, `realistic`, and `safe` buckets.

5) Frontend (Vite + React + Tailwind)

 - Change directory to the frontend and install dependencies:

```bash
cd frontend
npm install
```

 - Start the dev server:

```bash
npm run dev
```

Open `http://localhost:5173` to use the Advora-themed UI. The frontend posts to `http://localhost:8000/predict` by default; set `VITE_API_URL` in the frontend environment to change this.

Troubleshooting
---------------
- If the frontend cannot reach the backend, ensure `backend_app` is running and CORS is allowed for `http://localhost:5173` (already configured by default).
- If ingestion seems slow, increase `db_ingest.py`'s `batch_size` or confirm MongoDB is healthy.

That's it — the repository now includes the end-to-end pipeline: PDF extraction → JSON → Mongo ingestion → prediction API → Advora-themed frontend with export.
