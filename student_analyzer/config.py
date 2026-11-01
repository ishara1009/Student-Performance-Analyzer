"""Shared application settings and project-relative paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
STUDENTS_FILE = DATA_DIR / "students.json"
SAMPLE_CSV = DATA_DIR / "sample_students.csv"

SUBJECTS = ("python", "mathematics", "english")
GRADE_THRESHOLDS = ((75.0, "A"), (65.0, "B"), (55.0, "C"), (40.0, "S"))
SUBJECT_PASS_MARK = 40.0
OVERALL_PASS_AVERAGE = 50.0
