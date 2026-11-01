"""CSV student-result and text class-report generation."""

import csv
from datetime import datetime
from pathlib import Path

from .calculations import class_statistics, student_result
from .config import SUBJECTS
from .models import Student


class ReportError(Exception):
    """Raised when a report cannot be written."""


def _unique_path(directory: Path, stem: str, suffix: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return directory / f"{stem}_{timestamp}{suffix}"


def export_csv(students: list[Student], directory: Path) -> Path:
    """Export detailed student results to a unique CSV file."""
    if not students:
        raise ReportError("No student data available; no report was created.")
    path = _unique_path(directory, "student_results", ".csv")
    try:
        directory.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="") as file:
            fields = ["student_id", "name", *SUBJECTS, "total", "average", "grade", "status"]
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for student in students:
                result = student_result(student)
                writer.writerow({"student_id": student.student_id, "name": student.name, **student.marks, "total": f"{result['total']:.2f}", "average": f"{result['average']:.2f}", "grade": result["grade"], "status": result["status"]})
    except OSError as error:
        raise ReportError(f"Could not create CSV report: {error}") from error
    return path


def export_txt(students: list[Student], directory: Path) -> Path:
    """Export statistics, results, and rules to a unique text file."""
    stats = class_statistics(students)
    if stats is None:
        raise ReportError("No student data available; no report was created.")
    path = _unique_path(directory, "class_report", ".txt")
    subject_averages = stats["subject_averages"]
    assert isinstance(subject_averages, dict)
    lines = ["STUDENT PERFORMANCE ANALYZER - CLASS REPORT", f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}", "", "CLASS STATISTICS", f"Students: {stats['student_count']}", f"Class average: {stats['class_average']:.2f}"]
    lines.extend(f"{subject.title()} average: {subject_averages[subject]:.2f}" for subject in SUBJECTS)
    lines.extend([f"Highest average: {stats['highest_average']:.2f} ({', '.join(s.student_id for s in stats['highest_students'])})", f"Lowest average: {stats['lowest_average']:.2f} ({', '.join(s.student_id for s in stats['lowest_students'])})", f"Passed: {stats['passed_count']} | Failed: {stats['failed_count']}", "", "STUDENT RESULTS", f"{'ID':<10} {'Name':<24} {'Total':>8} {'Average':>8} {'Grade':>6} {'Status':>8}"])
    for student in students:
        result = student_result(student)
        lines.append(f"{student.student_id:<10} {student.name[:24]:<24} {result['total']:>8.2f} {result['average']:>8.2f} {result['grade']:>6} {result['status']:>8}")
    lines.extend(["", "GRADE BOUNDARIES", "A >= 75, B >= 65, C >= 55, S >= 40, F < 40", "", "PASS/FAIL RULES", "Passed requires every subject mark >= 40 AND overall average >= 50.", "Grade and pass/fail are separate results."])
    try:
        directory.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as error:
        raise ReportError(f"Could not create TXT report: {error}") from error
    return path
