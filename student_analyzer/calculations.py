"""Pure functions for individual results and class statistics."""

from typing import TypedDict

from .config import GRADE_THRESHOLDS, OVERALL_PASS_AVERAGE, SUBJECT_PASS_MARK, SUBJECTS
from .models import Student


class StudentResult(TypedDict):
    total: float
    average: float
    grade: str
    passed: bool
    status: str


def total_marks(student: Student) -> float:
    """Return the sum of all three marks (maximum 300)."""
    return sum(student.marks[subject] for subject in SUBJECTS)


def average_mark(student: Student) -> float:
    """Return the unrounded mean mark."""
    return total_marks(student) / len(SUBJECTS)


def grade_for_average(average: float) -> str:
    """Return the grade defined by the configured average boundaries."""
    for minimum, grade in GRADE_THRESHOLDS:
        if average >= minimum:
            return grade
    return "F"


def has_passed(student: Student) -> bool:
    """Require every subject >=40 and overall average >=50."""
    return all(student.marks[s] >= SUBJECT_PASS_MARK for s in SUBJECTS) and average_mark(student) >= OVERALL_PASS_AVERAGE


def student_result(student: Student) -> StudentResult:
    """Calculate all derived fields using unrounded values."""
    average = average_mark(student)
    passed = has_passed(student)
    return {"total": total_marks(student), "average": average, "grade": grade_for_average(average), "passed": passed, "status": "Passed" if passed else "Failed"}


def class_statistics(students: list[Student]) -> dict[str, object] | None:
    """Return class aggregates, or None when no students exist."""
    if not students:
        return None
    averages = [average_mark(student) for student in students]
    highest = max(averages)
    lowest = min(averages)
    passed_count = sum(has_passed(student) for student in students)
    return {
        "student_count": len(students),
        "class_average": sum(averages) / len(averages),
        "subject_averages": {s: sum(student.marks[s] for student in students) / len(students) for s in SUBJECTS},
        "highest_average": highest,
        "lowest_average": lowest,
        "highest_students": [student for student, avg in zip(students, averages) if avg == highest],
        "lowest_students": [student for student, avg in zip(students, averages) if avg == lowest],
        "passed_count": passed_count,
        "failed_count": len(students) - passed_count,
    }
