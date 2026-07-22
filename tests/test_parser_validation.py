from backend.app.parser import RawCutoffRow, validate_cutoff_row, validate_cutoff_rows


def test_validate_cutoff_row_normalizes_valid_record():
    row = RawCutoffRow(
        source_file="23-24.pdf",
        source_page=12,
        institute_code="1002",
        college_name="  Government College of Engineering, Amravati  ",
        choice_code="100219110",
        branch_name="Choice Code : Course Name : Civil Engineering",
        seat_type="GOPEN",
        category=None,
        gender=None,
        rank="12345",
        cutoff_percentage="87.42%",
        cap_round=1,
        academic_year="23-24",
    )

    record, rejection = validate_cutoff_row(row)

    assert rejection is None
    assert record is not None
    assert record.academic_year == "2023-24"
    assert record.branch_name == "Civil Engineering"
    assert record.category == "OPEN"
    assert record.gender == "G"
    assert record.rank == 12345
    assert record.cutoff_percentage == 87.42


def test_validate_cutoff_row_rejects_missing_cutoff():
    row = RawCutoffRow(
        source_file="2025-26.pdf",
        institute_code="1002",
        college_name="Government College of Engineering, Amravati",
        choice_code="100219110",
        branch_name="Civil Engineering",
        seat_type="GOPEN",
        cap_round=1,
        academic_year="2025-26",
    )

    record, rejection = validate_cutoff_row(row)

    assert record is None
    assert rejection is not None
    assert "cutoff_percentage" in rejection.missing_fields


def test_validate_cutoff_rows_reports_duplicates_and_accuracy():
    rows = [
        RawCutoffRow(
            source_file="2025-26.pdf",
            institute_code="1002",
            college_name="Government College of Engineering, Amravati",
            choice_code="100219110",
            branch_name="Civil Engineering",
            seat_type="GOPEN",
            cutoff_percentage="88.00",
            cap_round=1,
            academic_year="2025-26",
        ),
        RawCutoffRow(
            source_file="2025-26.pdf",
            institute_code="1002",
            college_name="Government College of Engineering, Amravati",
            choice_code="100219110",
            branch_name="Civil Engineering",
            seat_type="GOPEN",
            cutoff_percentage="88.00",
            cap_round=1,
            academic_year="2025-26",
        ),
        RawCutoffRow(
            source_file="2025-26.pdf",
            institute_code="1002",
            college_name="Government College of Engineering, Amravati",
            choice_code="100219110",
            branch_name="Civil Engineering",
            seat_type="GOPEN",
            cap_round=1,
            academic_year="2025-26",
        ),
    ]

    records, report = validate_cutoff_rows(rows, source_file="2025-26.pdf", total_pages=2)

    assert len(records) == 1
    assert report.rows_found == 3
    assert report.rows_valid == 1
    assert report.rows_rejected == 2
    assert report.duplicate_records == 1
    assert report.missing_values["cutoff_percentage"] == 1
    assert report.parser_accuracy == 0.3333
