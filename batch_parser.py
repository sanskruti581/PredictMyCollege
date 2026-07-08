"""
Batch PDF parser for PredictMyCollege
- Reads PDFs from Previous_yrs_Result/
- Parses college headers, choice codes, caste categories and merit scores
- Emits cleaned JSON files into Cleaned_Data_JSON/

Usage:
    python batch_parser.py

Requirements: pdfplumber
"""
import re
import os
import json
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "Previous_yrs_Result"
OUTPUT_DIR = ROOT / "Cleaned_Data_JSON"
OUTPUT_DIR.mkdir(exist_ok=True)

COLLEGE_RE = re.compile(r"^(\d{4})\s*-\s*(.+)$")
CHOICE_RE = re.compile(r"^(\d{9})\s*-\s*(.+)$")
MERIT_RE = re.compile(r"(\d+)\s*\(([\d\.]+)%\)")
YEAR_RE = re.compile(r"(\d{4}-\d{2,4})")

# Known categories (non-exhaustive); parser will attempt to split rows containing these tokens
KNOWN_SEAT_TYPES = ["GOPEN", "GSCS", "GOBC", "LOBC", "EWS", "TFWS", "EWS/TFWS", "SEBC"]


def parse_pdf_file(pdf_path: Path):
    academic_year = "unknown"
    m = YEAR_RE.search(pdf_path.name)
    if m:
        academic_year = m.group(1)

    records = []

    current_college = None
    current_choice = None

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

            for line in lines:
                # College header
                m_col = COLLEGE_RE.match(line)
                if m_col:
                    current_college = {
                        "college_code": m_col.group(1),
                        "college_name": m_col.group(2).strip(),
                    }
                    current_choice = None
                    continue

                # Choice / course header
                m_choice = CHOICE_RE.match(line)
                if m_choice:
                    current_choice = {
                        "choice_code": m_choice.group(1),
                        "course_name": m_choice.group(2).strip(),
                    }
                    continue

                # Row that contains caste categories or merit
                # Try to detect merit entries
                m_merit = MERIT_RE.search(line)
                if m_merit and current_college and current_choice:
                    # find the nearest seat/category token within the line
                    seat = None
                    caste = None
                    for token in KNOWN_SEAT_TYPES:
                        if token in line:
                            seat = token
                            break
                    # fallback: try to extract uppercase words of length 3-6 as seat type
                    if not seat:
                        up_words = re.findall(r"\b([A-Z]{2,6})\b", line)
                        for w in up_words:
                            if w not in ["STAGE", "CET", "AND"]:
                                seat = w
                                break

                    rank = int(m_merit.group(1))
                    percent = float(m_merit.group(2))

                    rec = {
                        "college_id": current_college.get("college_code"),
                        "college_name": current_college.get("college_name"),
                        "choice_code": current_choice.get("choice_code"),
                        "branch_name": current_choice.get("course_name"),
                        "academic_year": academic_year,
                        "cap_round": 1,
                        "seat_type": seat or "UNKNOWN",
                        "caste_category": seat or "UNKNOWN",
                        "gender": "G",
                        "state_merit_rank": rank,
                        "cutoff_percentage": percent,
                        "admission_stage": "Stage-I",
                    }
                    records.append(rec)
                    continue

                # Row that likely contains a list of categories
                for token in KNOWN_SEAT_TYPES:
                    if token in line and current_college and current_choice:
                        # split and keep tokens appearing in known list
                        found = [t for t in re.split(r"[\s,;/]+", line) if t in KNOWN_SEAT_TYPES]
                        if found:
                            # create lightweight records with empty merits so downstream can map
                            for t in found:
                                rec = {
                                    "college_id": current_college.get("college_code"),
                                    "college_name": current_college.get("college_name"),
                                    "choice_code": current_choice.get("choice_code"),
                                    "branch_name": current_choice.get("course_name"),
                                    "academic_year": academic_year,
                                    "cap_round": 1,
                                    "seat_type": t,
                                    "caste_category": t,
                                    "gender": "G",
                                    "state_merit_rank": None,
                                    "cutoff_percentage": None,
                                    "admission_stage": None,
                                }
                                records.append(rec)
                        break

    return records


def run_all():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR

    for pdf_file in sorted(input_dir.glob("*.pdf")):
        try:
            print(f"Parsing {pdf_file.name}...")
            records = parse_pdf_file(pdf_file)
            out_name = (output_dir / (pdf_file.stem + ".json"))
            with open(out_name, "w", encoding="utf-8") as f:
                json.dump({"source_file": pdf_file.name, "records": records}, f, ensure_ascii=False, indent=2)
            print(f"Wrote {len(records)} records to {out_name.name}")
        except Exception as e:
            print(f"Failed to parse {pdf_file.name}: {e}")


if __name__ == "__main__":
    run_all()
