# PredictMyCollege Project Redesign

## Phase 1: Complete Project Audit

### Current Repository Shape

The project currently has a flat backend and ETL layout:

- `batch_parser.py`: PDF parser and metadata generator.
- `db_ingest.py`: JSON-to-MongoDB ingestion script.
- `backend_app.py`: FastAPI app, MongoDB connection, fallback data, schemas, route, and prediction logic in one file.
- `models.py`: unused or weakly connected Pydantic models.
- `frontend/src`: single React screen with a form, results matrix, choice-list builder, and export component.
- `Cleaned_Data_JSON`: parsed data files and a small mock sample.
- `Previous_yrs_Result`: raw CAP PDFs.

### Data Audit

Current parsed real-data output is not usable for admission prediction:

| File | Records | Missing cutoff | Missing college | Missing branch | Academic years |
| --- | ---: | ---: | ---: | ---: | --- |
| `2025-26.json` | 14,523 | 14,523 | 0 | 0 | `2025-26` |
| `23-24.json` | 11,333 | 11,333 | 0 | 0 | `2025-26` |
| `mock_cutoff_sample.json` | 7 | 0 | 0 | 0 | `2025-26` |

Key finding: both real parsed datasets contain `cutoff_percentage: null` for every record. The app can appear to work only because `mock_cutoff_sample.json` contains hand-shaped data.

### Parser Audit

- The parser is a best-effort line scanner, not a reliable CAP table parser.
- It records rows even when cutoff and rank are missing.
- It hardcodes `cap_round = 1`.
- It mis-detects academic year for `23-24.pdf` as `2025-26`.
- It does not extract district, city, university, institute status, minority, TFWS, PWD, or defence attributes reliably.
- `branch_name` includes label noise such as `Choice Code : Course Name : Civil Engineering`.
- Seat type detection is token-based and can create false records from header or summary lines.
- It prints parsing errors to stdout instead of writing structured parser logs.
- It silently accepts incomplete records.
- It does not generate parser accuracy, duplicate, rejected-row, missing-value, or page-level reports.
- Frontend metadata is generated directly by the parser, coupling ETL to UI code.

### Database Audit

- MongoDB uses one denormalized `cutoffs` collection.
- There are no normalized `colleges`, `branches`, `districts`, `metadata`, or `parser_logs` collections.
- No enforced unique index exists for a full cutoff identity including round, category, gender, quota, year, branch, and college.
- `unique_ingest_idx` is not declared unique and omits important fields.
- Missing cutoff records are ingested unless manually filtered elsewhere.
- College, city, district, university, and branch names are stored as repeated strings.
- Mock and real data have incompatible category semantics.

### Backend Audit

- `backend_app.py` mixes configuration, database lifecycle, request schemas, query construction, route handling, and prediction logic.
- Business logic lives directly inside the route.
- MongoDB access is not abstracted behind repositories.
- There is no service layer.
- There is no centralized error handling or response envelope.
- CORS allows `"*"`, which is not production-safe.
- Startup uses deprecated FastAPI event style rather than lifespan.
- There is no pagination, sorting contract, API versioning, or metadata endpoint.
- Rank mode is accepted by the frontend, but prediction still requires percentage-based logic.
- `category` is mapped inconsistently: sometimes to `caste_category`, sometimes to `seat_type`.
- `seat_type`, gender, flags, special seats, district, safety zones, and gap filters are mostly ignored.
- The API returns only `dream`, `realistic`, and `safe`, but the requested product needs probability, confidence, reason, trend, and compare data.

### Frontend Audit

- The UI is a single-page prototype, not the requested multi-page app.
- Navbar links are anchors that do not route.
- There is no dark-mode toggle, GitHub link, responsive mobile menu, footer, explorer, compare page, dashboard, about page, or contact page.
- The prediction form contains many controls the backend ignores.
- Result cards are a table and omit probability, confidence, trend, reason, favorite, and compare actions.
- There are encoding artifacts in visible text, for example `â€”`, `â€¢`, and garbled emoji.
- The metadata dropdowns are static and stale.
- There is no TypeScript, route-level loading, error boundary, API client abstraction beyond one function, skeleton states, or reusable form primitives.
- The current UI uses rounded and glass styling, but does not yet meet the requested premium application workflow.

### Testing Audit

- Tests are tied to `backend_app.py` internals.
- Tests validate fallback behavior, not parser accuracy, data validation, database normalization, or prediction correctness.
- There are no frontend tests.
- There are no API contract tests.
- There are no ingestion idempotency tests.

## Phase 2: Problem List

### Critical

- Real parsed cutoff data has no cutoff percentages, so prediction accuracy is currently impossible.
- Parser accepts invalid records instead of rejecting and reporting them.
- Academic year extraction is wrong for at least `23-24.pdf`.
- Prediction logic is a simple cutoff delta bucket, not a probability engine.
- API accepts frontend payload fields that it does not truly honor.

### High

- Backend architecture is not maintainable at production scale.
- Database schema is denormalized and weakly indexed.
- Mongo ingestion is not protected by strong uniqueness rules.
- UI promises filters and modes that the backend does not implement.
- No structured observability exists for parser failures.

### Medium

- Frontend lacks routing, page structure, reusable services, and robust states.
- Static parser-generated frontend metadata couples ETL to UI.
- CORS and configuration are development-oriented.
- Documentation describes the pipeline as complete even though real parsed data is invalid.

### Low

- Dead or weakly used files include `models.py` and some UI components that support the old choice-list workflow.
- Visual polish is inconsistent.
- Encoding artifacts reduce trust.

## Phase 3: New Architecture

### Target Pipeline

```text
Raw CAP PDFs
  -> PDF extraction layer
  -> table/line normalization
  -> record validation
  -> normalized JSON artifacts
  -> MongoDB ingest
  -> repository layer
  -> prediction engine
  -> REST API
  -> React UI
```

### Backend Layers

```text
backend/app
  config        application settings and environment parsing
  database      MongoDB client, indexes, sessions, health checks
  exceptions    domain exceptions and API error mapping
  middleware    request IDs, timing, CORS, error boundaries
  models        persistence/domain models
  parser        PDF extraction, normalization, validation, reports
  prediction    scoring engine, trend analysis, confidence calculation
  repositories  collection-specific database access
  routers       route declarations only
  schemas       request/response DTOs
  services      orchestration and business use cases
  utils         logging, normalization, pagination, IDs
```

### Frontend Layers

```text
frontend/src
  assets
  components    shared UI primitives and feature components
  hooks         reusable state/query hooks
  layouts       app shell, navbar, footer
  pages         Home, Predict, Colleges, Compare, Dashboard, About, Contact
  services      API client and endpoint modules
  types         shared TypeScript interfaces
  utils         formatting, validation, constants
```

## Phase 4: Created Folder Structure

The following migration structure has been created without removing the existing working prototype:

- `backend/app/config`
- `backend/app/database`
- `backend/app/exceptions`
- `backend/app/middleware`
- `backend/app/models`
- `backend/app/parser`
- `backend/app/prediction`
- `backend/app/repositories`
- `backend/app/routers`
- `backend/app/schemas`
- `backend/app/services`
- `backend/app/utils`
- `frontend/src/assets`
- `frontend/src/hooks`
- `frontend/src/layouts`
- `frontend/src/pages`
- `frontend/src/services`
- `frontend/src/types`
- `frontend/src/utils`

## Phase 5: Database Schema

### `colleges`

```json
{
  "_id": "1002",
  "institute_code": "1002",
  "name": "Government College of Engineering, Amravati",
  "status": "Government Autonomous",
  "city": "Amravati",
  "district_id": "amravati",
  "university_id": "sgbau",
  "minority": null,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

Indexes:

- Unique: `institute_code`
- Search: `name`
- Filter: `district_id`, `university_id`, `status`

### `branches`

```json
{
  "_id": "civil-engineering",
  "name": "Civil Engineering",
  "normalized_name": "civil engineering",
  "group": "Core Engineering"
}
```

Indexes:

- Unique: `normalized_name`
- Filter: `group`

### `districts`

```json
{
  "_id": "amravati",
  "name": "Amravati",
  "region": "Vidarbha"
}
```

Indexes:

- Unique: `name`
- Filter: `region`

### `universities`

```json
{
  "_id": "sgbau",
  "name": "Sant Gadge Baba Amravati University",
  "city": "Amravati"
}
```

Indexes:

- Unique: `name`

### `cutoffs`

```json
{
  "_id": "2025-26:1:1002:100219110:GOPEN",
  "academic_year": "2025-26",
  "cap_round": 1,
  "college_id": "1002",
  "branch_id": "civil-engineering",
  "choice_code": "100219110",
  "seat_type": "GOPEN",
  "category": "OPEN",
  "gender": "G",
  "quota": "STATE",
  "rank": 12345,
  "cutoff_percentage": 87.42,
  "status": "valid",
  "source_pdf": "2025-26.pdf",
  "source_page": 42,
  "created_at": "datetime"
}
```

Indexes:

- Unique compound: `academic_year`, `cap_round`, `college_id`, `branch_id`, `seat_type`, `category`, `gender`, `quota`
- Prediction: `branch_id`, `category`, `gender`, `quota`, `seat_type`, `cutoff_percentage`
- Trends: `college_id`, `branch_id`, `seat_type`, `academic_year`, `cap_round`
- Explorer: `college_id`, `branch_id`, `cutoff_percentage`

### `parser_logs`

```json
{
  "_id": "run-id",
  "source_pdf": "2025-26.pdf",
  "academic_year": "2025-26",
  "started_at": "datetime",
  "finished_at": "datetime",
  "total_pages": 300,
  "rows_found": 18000,
  "rows_valid": 16000,
  "rows_rejected": 2000,
  "missing_values": {
    "cutoff_percentage": 100,
    "rank": 240
  },
  "duplicate_records": 12,
  "parser_accuracy": 0.91,
  "errors": []
}
```

Indexes:

- `source_pdf`, `academic_year`
- `started_at`

### `metadata`

```json
{
  "_id": "dataset",
  "latest_academic_year": "2025-26",
  "available_years": ["2023-24", "2024-25", "2025-26"],
  "available_rounds": [1, 2, 3],
  "last_ingested_at": "datetime"
}
```

## Phase 6: API Contracts

All successful responses should use:

```json
{
  "success": true,
  "data": {},
  "meta": {},
  "error": null
}
```

All errors should use:

```json
{
  "success": false,
  "data": null,
  "meta": {},
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### `GET /api/v1/colleges`

Query params: `q`, `district_id`, `branch_id`, `university_id`, `category`, `seat_type`, `min_cutoff`, `max_cutoff`, `page`, `limit`, `sort`.

Returns paginated college cards with district, university, available branches, and latest cutoff summary.

### `GET /api/v1/branches`

Returns normalized branches with IDs and groups.

### `GET /api/v1/districts`

Returns districts and regions.

### `GET /api/v1/metadata`

Returns years, rounds, categories, seat types, genders, latest dataset, and parser freshness.

### `POST /api/v1/predict`

Request:

```json
{
  "diploma_percentage": 88.5,
  "category": "OPEN",
  "gender": "G",
  "seat_type": "GOPEN",
  "district_id": "amravati",
  "preferred_branch_id": "computer-science-and-engineering",
  "preferred_college_id": null,
  "cap_round": 1,
  "flags": {
    "minority": false,
    "tfws": false,
    "pwd": false,
    "defence": false
  }
}
```

Response item:

```json
{
  "college": {
    "id": "1002",
    "name": "Government College of Engineering, Amravati",
    "district": "Amravati",
    "city": "Amravati",
    "university": "Sant Gadge Baba Amravati University"
  },
  "branch": {
    "id": "computer-science-and-engineering",
    "name": "Computer Science and Engineering"
  },
  "cutoff": 87.42,
  "difference": 1.08,
  "admission_probability": 0.68,
  "confidence": 0.82,
  "classification": "Target",
  "reason": "Your score is 1.08 percentage points above the latest matching cutoff.",
  "historical_trend": {
    "direction": "stable",
    "values": [
      { "year": "2023-24", "cutoff": 86.9 },
      { "year": "2024-25", "cutoff": 87.1 },
      { "year": "2025-26", "cutoff": 87.42 }
    ]
  }
}
```

### `POST /api/v1/compare`

Compares two colleges or two college-branch pairs across cutoff, location, university, branch availability, trend, fees, and placement fields when available.

### `GET /api/v1/statistics`

Returns dashboard aggregates for CAP trends, category distribution, branch popularity, district statistics, and college statistics.

### `GET /api/v1/parser-report`

Returns latest parser logs and per-source parser quality metrics.

## Phase 7: UI Wireframe

### App Shell

- Sticky navbar with logo, Predict, Colleges, Dashboard, About, Contact, dark-mode toggle, GitHub link, and mobile menu.
- Footer with project purpose, data disclaimer, source note, and contact links.
- Dark theme default using `#0F172A`, primary `#2563EB`, accent `#38BDF8`, card color `#1E293B`.

### Home

- First viewport: brand/product signal, hero CTA to Predict, animated but restrained background.
- Project overview.
- Feature cards: reliable CAP data, explainable prediction, college comparison, district/branch insights.
- How prediction works: profile, matching cutoffs, trend scoring, classification.
- Statistics strip: colleges, branches, records, years, latest parser accuracy.

### Predict College

- Inputs only: Diploma Percentage, Category, Gender, Seat Type, District, Preferred Branch, Preferred College optional, CAP Round.
- Inline validation.
- Predict button.
- Result cards with college, branch, cutoff, difference, probability, confidence, reason, trend, favorite, compare.

### College Explorer

- Search box.
- Filters: District, Branch, University, Category, Seat Type, Cutoff Range.
- Paginated results with quick compare/favorite actions.

### Compare Colleges

- Two selector panels.
- Side-by-side comparison: location, university, branches, latest cutoff, historical trend, fees, placement when available.

### Statistics Dashboard

- CAP trends by year and round.
- Category distribution.
- Branch popularity.
- District statistics.
- College statistics.

### About

- Project goal, data source explanation, limitations, transparency note.

### Contact

- Contact form or contact cards with validation.

## Phase 8: Implementation Roadmap

### Module 1: Parser and Validation

- Build parser package with typed extracted rows.
- Add validators for college, branch, seat type, category, rank, cutoff, year, round, district, city, university.
- Reject invalid rows with structured reasons.
- Generate JSON artifacts and parser reports.
- Add parser unit tests using fixture snippets.

Exit criteria:

- Real parsed records contain valid cutoff percentages and ranks when available.
- Invalid rows are rejected and counted.
- Parser report includes all required metrics.

### Module 2: Database and Ingestion

- Add normalized collections and index creation.
- Implement idempotent ingest using deterministic IDs.
- Add repository tests for uniqueness and lookup performance.

Exit criteria:

- Ingest creates colleges, branches, districts, universities, cutoffs, metadata, and parser logs.
- Duplicate ingest does not duplicate records.

### Module 3: FastAPI Foundation

- Move app to `backend/app`.
- Add settings, lifespan, database dependency, routers, repositories, services, schemas, exceptions, middleware.
- Add consistent response envelope.

Exit criteria:

- Health, metadata, colleges, branches, districts, and parser-report APIs work.
- Old single-file app can be retired after frontend migration.

### Module 4: Prediction Engine

- Implement score calculation from cutoff gap, category/seat match, district preference, branch/college preference, CAP round, special flags, and year trend.
- Return probability, confidence, reason, trend, and Dream/Target/Safe classification.
- Add deterministic tests for scoring edge cases.

Exit criteria:

- Prediction is explainable and tested.
- Rank mode is either properly implemented from rank cutoffs or removed from UI until supported.

### Module 5: React App Shell

- Convert to TypeScript.
- Add routing, app layout, navbar, footer, error boundary, API client, loading states.
- Replace static metadata with API metadata.

Exit criteria:

- Home, Predict, Colleges, Compare, Dashboard, About, and Contact routes exist.
- Navbar and mobile menu work.

### Module 6: Feature Pages

- Build Predict page and result cards.
- Build College Explorer.
- Build Compare page.
- Build Statistics Dashboard.

Exit criteria:

- All visible controls call real API fields.
- No dead filters remain.

### Module 7: Production Readiness

- Add test suite, linting, formatting, env examples, runbook, deployment notes.
- Add parser and backend logging.
- Add frontend accessibility checks and responsive QA.

Exit criteria:

- `pytest` and frontend build pass.
- README reflects the new architecture.

## Phase 9: Implementation Start

Implementation should begin with Module 1: Parser and Validation because no backend or UI prediction work can be accurate until the cutoff dataset is trustworthy.

The first production-ready implementation target is:

```text
backend/app/parser
  models.py       typed parser records and parser report models
  validators.py  row-level validation and normalization
  reader.py      PDF text/table extraction
  service.py     parse source PDF into valid records plus report
```

No old parser behavior should be deleted until the new parser has tests and produces valid records for at least one real CAP PDF sample.
