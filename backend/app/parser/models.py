from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class RawCutoffRow(BaseModel):
    source_file: str
    source_page: Optional[int] = None
    raw_text: Optional[str] = None
    institute_code: Optional[str] = None
    college_name: Optional[str] = None
    choice_code: Optional[str] = None
    branch_name: Optional[str] = None
    seat_type: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    rank: Optional[object] = None
    cutoff_percentage: Optional[object] = None
    cap_round: Optional[int] = None
    academic_year: Optional[str] = None
    status: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    university: Optional[str] = None


class ValidatedCutoffRecord(BaseModel):
    source_file: str
    source_page: Optional[int] = None
    institute_code: str
    college_name: str
    choice_code: str
    branch_name: str
    seat_type: str
    category: str
    gender: Optional[str] = None
    rank: Optional[int] = None
    cutoff_percentage: float = Field(ge=0, le=100)
    cap_round: int = Field(ge=1, le=10)
    academic_year: str
    status: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    university: Optional[str] = None

    @validator("institute_code")
    def institute_code_must_be_four_digits(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 4:
            raise ValueError("institute_code must be exactly 4 digits")
        return value

    @validator("choice_code")
    def choice_code_must_be_nine_digits(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 9:
            raise ValueError("choice_code must be exactly 9 digits")
        return value


class RowRejection(BaseModel):
    source_file: str
    source_page: Optional[int] = None
    raw_text: Optional[str] = None
    reason: str
    missing_fields: List[str] = Field(default_factory=list)


class ParserReport(BaseModel):
    source_file: str
    academic_year: Optional[str] = None
    total_pages: int = 0
    rows_found: int = 0
    rows_valid: int = 0
    rows_rejected: int = 0
    missing_values: Dict[str, int] = Field(default_factory=dict)
    duplicate_records: int = 0
    parser_accuracy: float = 0.0
    rejections: List[RowRejection] = Field(default_factory=list)

    @classmethod
    def from_validation(
        cls,
        source_file: str,
        rows_found: int,
        valid_records: List[ValidatedCutoffRecord],
        rejections: List[RowRejection],
        total_pages: int = 0,
        duplicate_records: int = 0,
        academic_year: Optional[str] = None,
    ) -> "ParserReport":
        missing_values: Dict[str, int] = {}
        for rejection in rejections:
            for field in rejection.missing_fields:
                missing_values[field] = missing_values.get(field, 0) + 1

        valid_count = len(valid_records)
        accuracy = round(valid_count / rows_found, 4) if rows_found else 0.0
        return cls(
            source_file=source_file,
            academic_year=academic_year,
            total_pages=total_pages,
            rows_found=rows_found,
            rows_valid=valid_count,
            rows_rejected=len(rejections),
            missing_values=missing_values,
            duplicate_records=duplicate_records,
            parser_accuracy=accuracy,
            rejections=rejections,
        )
