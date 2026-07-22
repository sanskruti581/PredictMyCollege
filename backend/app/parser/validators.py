import re
from typing import Iterable, List, Optional, Tuple

from pydantic import ValidationError

from .models import ParserReport, RawCutoffRow, RowRejection, ValidatedCutoffRecord

YEAR_RE = re.compile(r"^(20)?(\d{2})-(\d{2})$")
BRANCH_LABEL_RE = re.compile(r"^\s*(choice\s+code\s*:)?\s*(course\s+name\s*:)?\s*", re.IGNORECASE)
KNOWN_CATEGORIES = ("OPEN", "OBC", "SC", "ST", "VJ", "NT", "EWS", "SEBC", "TFWS", "PWD", "DEFENCE")


def normalize_spaces(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    normalized = re.sub(r"\s+", " ", str(value).strip())
    return normalized or None


def normalize_academic_year(value: Optional[object]) -> Optional[str]:
    text = normalize_spaces(value)
    if not text:
        return None
    match = YEAR_RE.match(text)
    if not match:
        return text
    start = int(match.group(2))
    end = int(match.group(3))
    return f"20{start:02d}-{end:02d}"


def normalize_branch_name(value: Optional[object], choice_code: Optional[str] = None) -> Optional[str]:
    text = normalize_spaces(value)
    if not text:
        return None
    if choice_code:
        text = text.replace(choice_code, " ")
    text = BRANCH_LABEL_RE.sub("", text)
    text = re.sub(r"\s*:\s*", ": ", text)
    text = normalize_spaces(text)
    if text and text.lower().startswith("course name:"):
        text = normalize_spaces(text.split(":", 1)[1])
    return text


def parse_cutoff_percentage(value: Optional[object]) -> Optional[float]:
    text = normalize_spaces(value)
    if not text:
        return None
    match = re.search(r"\d{1,3}(?:\.\d+)?", text)
    if not match:
        return None
    cutoff = float(match.group(0))
    if cutoff < 0 or cutoff > 100:
        return None
    return cutoff


def parse_rank(value: Optional[object]) -> Optional[int]:
    text = normalize_spaces(value)
    if not text:
        return None
    match = re.search(r"\d+", text)
    if not match:
        return None
    rank = int(match.group(0))
    return rank if rank > 0 else None


def normalize_seat_type(value: Optional[object]) -> Optional[str]:
    text = normalize_spaces(value)
    return text.upper() if text else None


def infer_category(seat_type: Optional[str], explicit_category: Optional[object]) -> Optional[str]:
    category = normalize_spaces(explicit_category)
    if category:
        category = category.upper()
        if category in KNOWN_CATEGORIES:
            return category

    seat = normalize_seat_type(seat_type)
    if not seat:
        return None
    if "SEBC" in seat:
        return "SEBC"
    if "OPEN" in seat:
        return "OPEN"
    if "OBC" in seat:
        return "OBC"
    if "EWS" in seat:
        return "EWS"
    if "TFWS" in seat:
        return "TFWS"
    if "PWD" in seat:
        return "PWD"
    if "DEF" in seat:
        return "DEFENCE"
    if "SC" in seat:
        return "SC"
    if re.search(r"\bST\b|GST|LST", seat):
        return "ST"
    if "VJ" in seat:
        return "VJ"
    if "NT" in seat:
        return "NT"
    return None


def infer_gender(seat_type: Optional[str], explicit_gender: Optional[object]) -> Optional[str]:
    gender = normalize_spaces(explicit_gender)
    if gender:
        upper = gender.upper()
        if upper.startswith("F") or upper.startswith("L"):
            return "F"
        if upper.startswith("M") or upper.startswith("G"):
            return "G"
    seat = normalize_seat_type(seat_type)
    if not seat:
        return None
    if seat.startswith("L"):
        return "F"
    if seat.startswith("G"):
        return "G"
    return None


def missing_required_fields(payload: dict) -> List[str]:
    required = [
        "institute_code",
        "college_name",
        "choice_code",
        "branch_name",
        "seat_type",
        "category",
        "cutoff_percentage",
        "cap_round",
        "academic_year",
    ]
    return [field for field in required if payload.get(field) in (None, "")]


def validate_cutoff_row(row: RawCutoffRow) -> Tuple[Optional[ValidatedCutoffRecord], Optional[RowRejection]]:
    seat_type = normalize_seat_type(row.seat_type)
    choice_code = normalize_spaces(row.choice_code)
    payload = {
        "source_file": normalize_spaces(row.source_file) or "unknown",
        "source_page": row.source_page,
        "institute_code": normalize_spaces(row.institute_code),
        "college_name": normalize_spaces(row.college_name),
        "choice_code": choice_code,
        "branch_name": normalize_branch_name(row.branch_name, choice_code),
        "seat_type": seat_type,
        "category": infer_category(seat_type, row.category),
        "gender": infer_gender(seat_type, row.gender),
        "rank": parse_rank(row.rank),
        "cutoff_percentage": parse_cutoff_percentage(row.cutoff_percentage),
        "cap_round": row.cap_round,
        "academic_year": normalize_academic_year(row.academic_year),
        "status": normalize_spaces(row.status),
        "district": normalize_spaces(row.district),
        "city": normalize_spaces(row.city),
        "university": normalize_spaces(row.university),
    }

    missing = missing_required_fields(payload)
    if missing:
        return None, RowRejection(
            source_file=payload["source_file"],
            source_page=row.source_page,
            raw_text=row.raw_text,
            reason="Missing required parser fields",
            missing_fields=missing,
        )

    try:
        return ValidatedCutoffRecord(**payload), None
    except ValidationError as exc:
        return None, RowRejection(
            source_file=payload["source_file"],
            source_page=row.source_page,
            raw_text=row.raw_text,
            reason=str(exc),
            missing_fields=[],
        )


def validate_cutoff_rows(
    rows: Iterable[RawCutoffRow],
    source_file: str,
    total_pages: int = 0,
    academic_year: Optional[str] = None,
) -> Tuple[List[ValidatedCutoffRecord], ParserReport]:
    valid_records: List[ValidatedCutoffRecord] = []
    rejections: List[RowRejection] = []
    seen = set()
    duplicate_records = 0
    row_count = 0

    for row in rows:
        row_count += 1
        record, rejection = validate_cutoff_row(row)
        if rejection:
            rejections.append(rejection)
            continue

        assert record is not None
        identity = (
            record.academic_year,
            record.cap_round,
            record.institute_code,
            record.choice_code,
            record.seat_type,
            record.category,
            record.gender,
        )
        if identity in seen:
            duplicate_records += 1
            rejections.append(RowRejection(
                source_file=record.source_file,
                source_page=record.source_page,
                reason="Duplicate cutoff record",
                missing_fields=[],
            ))
            continue
        seen.add(identity)
        valid_records.append(record)

    report = ParserReport.from_validation(
        source_file=source_file,
        rows_found=row_count,
        valid_records=valid_records,
        rejections=rejections,
        total_pages=total_pages,
        duplicate_records=duplicate_records,
        academic_year=normalize_academic_year(academic_year),
    )
    return valid_records, report
