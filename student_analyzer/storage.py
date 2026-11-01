"""Safe JSON persistence and validated CSV import."""

import csv
import json
import os
import tempfile
from pathlib import Path

from .config import SUBJECTS
from .models import Student


class StorageError(Exception):
    """Raised for data loading or saving failures."""


class CSVImportError(Exception):
    """Raised when an entire CSV file cannot be imported."""


class ImportResult:
    """Describe staged CSV records and all skipped rows."""

    def __init__(self) -> None:
        self.students: list[Student] = []
        self.errors: list[str] = []
        self.duplicate_count = 0
        self.blank_count = 0

    @property
    def skipped_count(self) -> int:
        return len(self.errors) + self.duplicate_count


def load_students(path: Path) -> list[Student]:
    """Load and validate a JSON array; a missing file means no students."""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise StorageError(f"Could not load {path}: {error}") from error
    if not isinstance(data, list):
        raise StorageError("Stored data must be a JSON array.")
    students: list[Student] = []
    seen_ids: set[str] = set()

    # Validate every saved record instead of trusting the JSON file.
    for index, record in enumerate(data, start=1):
        try:
            student = Student.from_dict(record)
        except (TypeError, ValueError) as error:
            raise StorageError(f"Invalid stored student at record {index}: {error}") from error
        if student.student_id in seen_ids:
            raise StorageError(f"Duplicate stored student ID: {student.student_id}.")
        seen_ids.add(student.student_id)
        students.append(student)
    return students


def save_students(path: Path, students: list[Student]) -> None:
    """Atomically replace JSON data, leaving the previous file on failure."""
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write to a temporary file first.  Only a fully written file replaces
        # students.json, so an interrupted save cannot destroy the old data.
        descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        temporary = Path(name)

        student_records = []
        for student in students:
            student_records.append(student.to_dict())

        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            json.dump(
                student_records,
                file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())

        temporary.replace(path)
    except (OSError, TypeError, ValueError) as error:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise StorageError(f"Could not save {path}: {error}") from error


def read_csv_import(path: Path, existing_ids: set[str] | None = None) -> ImportResult:
    """Read, validate, and stage unique students without modifying the source."""
    expected = ["student_id", "name", *SUBJECTS]
    result = ImportResult()
    known_ids: set[str] = set()
    if existing_ids is not None:
        for value in existing_ids:
            known_ids.add(value.upper())

    seen_in_file: set[str] = set()
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != expected:
                raise CSVImportError("CSV headers must be exactly: " + ",".join(expected))

            for line_number, row in enumerate(reader, start=2):
                is_blank_row = True
                for value in row.values():
                    if value is not None and value.strip():
                        is_blank_row = False
                        break

                if is_blank_row:
                    result.blank_count += 1
                    continue

                try:
                    marks = {}
                    for subject in SUBJECTS:
                        marks[subject] = row[subject]

                    student = Student(row["student_id"], row["name"], marks)
                except (TypeError, ValueError) as error:
                    result.errors.append(f"Line {line_number}: {error}")
                    continue

                is_already_saved = student.student_id in known_ids
                is_repeated_in_csv = student.student_id in seen_in_file
                if is_already_saved or is_repeated_in_csv:
                    result.duplicate_count += 1
                    continue

                seen_in_file.add(student.student_id)
                result.students.append(student)
    except CSVImportError:
        raise
    except FileNotFoundError as error:
        raise CSVImportError(f"CSV file was not found: {path}") from error
    except (OSError, UnicodeError, csv.Error) as error:
        raise CSVImportError(f"Could not read CSV file: {error}") from error
    return result
