"""
Batch PDF parser for PredictMyCollege
- Reads PDFs from Previous_yrs_Result/
- Streams text line-by-line to preserve college and choice state
- Emits cleaned JSON files plus metadata for frontend filtering

Usage:
    python batch_parser.py

Requirements: pdfplumber
"""
import json
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "Previous_yrs_Result"
OUTPUT_DIR = ROOT / "Cleaned_Data_JSON"
METADATA_FILE = ROOT / "frontend" / "src" / "lib" / "parsed_metadata.js"
OUTPUT_DIR.mkdir(exist_ok=True)

COLLEGE_CODE_RE = re.compile(r"\b(\d{4})\b")
CHOICE_CODE_RE = re.compile(r"\b(\d{9})\b")
YEAR_RE = re.compile(r"(\d{4}-\d{2,4})")
PERCENT_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)%")
RANK_RE = re.compile(r"\b(\d{2,6})\b")
BRANCH_KEYWORDS = [
    'Engineering', 'Technology', 'Computer', 'Information', 'Electronics', 'Civil', 'Mechanical', 'AI/ML', 'Artificial', 'Production', 'Chemical', 'Biomedical'
]
CITY_KEYWORDS = [
    'Mumbai', 'Pune', 'Nagpur', 'Aurangabad', 'Nashik', 'Amravati', 'Solapur', 'Kolhapur', 'Thane', 'Navi Mumbai'
]

KNOWN_SEAT_TYPES = ['GOPEN', 'GOBC', 'GSCS', 'GST', 'EWS', 'TFWS', 'SEBC', 'OPEN', 'OBC', 'SC', 'ST', 'NT', 'VJ', 'PWD', 'DEFENCE']


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", ' ', value.strip())


def detect_year_from_filename(filename: str) -> str:
    match = YEAR_RE.search(filename)
    return match.group(1) if match else '2025-26'


def extract_metadata_from_line(line: str, branch_set: set, city_set: set):
    normalized = normalize_text(line)
    if any(keyword.lower() in normalized.lower() for keyword in BRANCH_KEYWORDS):
        branch_set.add(normalized)
    for city in CITY_KEYWORDS:
        if city.lower() in normalized.lower():
            city_set.add(city)


def parse_pdf_file(pdf_path: Path, branch_set: set, city_set: set):
    academic_year = detect_year_from_filename(pdf_path.name)
    records = []
    current_college = None
    current_choice = None

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            for raw_line in text.splitlines():
                line = normalize_text(raw_line)
                if not line:
                    continue

                extract_metadata_from_line(line, branch_set, city_set)

                try:
                    college_code_match = COLLEGE_CODE_RE.search(line)
                    if college_code_match and 'college' in line.lower():
                        current_college = {
                            'college_id': college_code_match.group(1),
                            'college_name': normalize_text(line),
                        }
                        current_choice = None
                        continue

                    choice_code_match = CHOICE_CODE_RE.search(line)
                    if choice_code_match and current_college:
                        current_choice = {
                            'choice_code': choice_code_match.group(1),
                            'branch_name': normalize_text(line.replace(choice_code_match.group(1), '')),
                        }
                        continue

                    if current_college and current_choice:
                        seat_matches = [token for token in KNOWN_SEAT_TYPES if token in line]
                        percent_match = PERCENT_RE.search(line)
                        rank_match = RANK_RE.search(line)

                        if seat_matches and percent_match:
                            for seat_type in seat_matches:
                                records.append({
                                    'college_id': current_college['college_id'],
                                    'college_name': current_college['college_name'],
                                    'choice_code': current_choice['choice_code'],
                                    'branch_name': current_choice['branch_name'],
                                    'academic_year': academic_year,
                                    'cap_round': 1,
                                    'seat_type': seat_type,
                                    'caste_category': seat_type,
                                    'gender': 'G',
                                    'state_merit_rank': int(rank_match.group(1)) if rank_match else None,
                                    'cutoff_percentage': float(percent_match.group(1)),
                                    'admission_stage': 'Stage-I',
                                })
                            continue

                        if seat_matches:
                            for seat_type in seat_matches:
                                records.append({
                                    'college_id': current_college['college_id'],
                                    'college_name': current_college['college_name'],
                                    'choice_code': current_choice['choice_code'],
                                    'branch_name': current_choice['branch_name'],
                                    'academic_year': academic_year,
                                    'cap_round': 1,
                                    'seat_type': seat_type,
                                    'caste_category': seat_type,
                                    'gender': 'G',
                                    'state_merit_rank': int(rank_match.group(1)) if rank_match else None,
                                    'cutoff_percentage': float(percent_match.group(1)) if percent_match else None,
                                    'admission_stage': 'Stage-I',
                                })
                            continue

                except Exception as exc:
                    print(f"Skipped noisy line while parsing {pdf_path.name}: {exc}")
                    continue

    return records


def write_metadata(branch_set: set, city_set: set):
    colleges = ['All Colleges']
    branches = ['All Branches'] + sorted(branch_set)
    cities = ['All Cities'] + sorted(city_set)
    years = ['2025 (Latest)']

    payload = [
        'export const AVAILABLE_COLLEGES = ' + json.dumps(colleges, ensure_ascii=False) + ';',
        'export const AVAILABLE_BRANCHES = ' + json.dumps(branches, ensure_ascii=False) + ';',
        'export const AVAILABLE_CITIES = ' + json.dumps(cities, ensure_ascii=False) + ';',
        'export const AVAILABLE_YEARS = ' + json.dumps(years, ensure_ascii=False) + ';',
    ]

    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(payload) + '\n')


def run_all():
    branch_set = set()
    city_set = set()
    all_records = []

    pdf_files = sorted(INPUT_DIR.glob('*.pdf'))
    for pdf_file in pdf_files:
        print(f'Parsing {pdf_file.name}...')
        records = parse_pdf_file(pdf_file, branch_set, city_set)
        if records:
            output_path = OUTPUT_DIR / (pdf_file.stem + '.json')
            with open(output_path, 'w', encoding='utf-8') as fh:
                json.dump({'source_file': pdf_file.name, 'records': records}, fh, ensure_ascii=False, indent=2)
            print(f'  Wrote {len(records)} records to {output_path.name}')
        else:
            print(f'  No records parsed from {pdf_file.name}')
        all_records.extend(records)

    write_metadata(branch_set, city_set)
    print(f'Generated metadata for {len(branch_set)} branches and {len(city_set)} cities.')


if __name__ == '__main__':
    run_all()
