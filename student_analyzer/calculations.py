"""Functions that calculate student results and class statistics."""

from .config import GRADE_THRESHOLDS, OVERALL_PASS_AVERAGE, SUBJECT_PASS_MARK, SUBJECTS
from .models import Student


def total_marks(student: Student) -> float:
    """Return the sum of all three marks (maximum 300)."""
    total = 0.0
    for subject in SUBJECTS:
        total = total + student.marks[subject]
    return total


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
    # Failing one subject is enough to fail the complete result.
    for subject in SUBJECTS:
        if student.marks[subject] < SUBJECT_PASS_MARK:
            return False

    if average_mark(student) < OVERALL_PASS_AVERAGE:
        return False

    return True


def student_result(student: Student) -> dict[str, object]:
    """Calculate all derived fields using unrounded values."""
    average = average_mark(student)
    passed = has_passed(student)
    if passed:
        status = "Passed"
    else:
        status = "Failed"

    result = {
        "total": total_marks(student),
        "average": average,
        "grade": grade_for_average(average),
        "passed": passed,
        "status": status,
    }
    return result


def class_statistics(students: list[Student]) -> dict[str, object] | None:
    """Return class aggregates, or None when no students exist."""
    if not students:
        return None
    averages = []
    for student in students:
        averages.append(average_mark(student))

    highest = max(averages)
    lowest = min(averages)

    passed_count = 0
    highest_students = []
    lowest_students = []
    subject_totals = {subject: 0.0 for subject in SUBJECTS}

    for student in students:
        student_average = average_mark(student)

        if has_passed(student):
            passed_count = passed_count + 1
        if student_average == highest:
            highest_students.append(student)
        if student_average == lowest:
            lowest_students.append(student)

        for subject in SUBJECTS:
            subject_totals[subject] += student.marks[subject]

    subject_averages = {}
    for subject in SUBJECTS:
        subject_averages[subject] = subject_totals[subject] / len(students)

    return {
        "student_count": len(students),
        "class_average": sum(averages) / len(averages),
        "subject_averages": subject_averages,
        "highest_average": highest,
        "lowest_average": lowest,
        "highest_students": highest_students,
        "lowest_students": lowest_students,
        "passed_count": passed_count,
        "failed_count": len(students) - passed_count,
    }
