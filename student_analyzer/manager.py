"""Student collection operations with validation before mutation."""

from .models import Student
from .validators import normalize_student_id, validate_marks


class StudentManager:
    """Manage an in-memory list of unique students."""

    def __init__(self, students: list[Student] | None = None) -> None:
        self._students = list(students or [])
        ids = [student.student_id for student in self._students]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate student IDs are not allowed.")

    @property
    def students(self) -> list[Student]:
        """Return a copy so callers cannot mutate the collection directly."""
        return list(self._students)

    def add(self, student: Student) -> None:
        """Add a student unless its normalized ID already exists."""
        if self.get_by_id(student.student_id):
            raise ValueError(f"Student ID {student.student_id} already exists.")
        self._students.append(student)

    def get_by_id(self, student_id: str) -> Student | None:
        """Find one student by exact normalized ID."""
        target = normalize_student_id(student_id)
        return next((student for student in self._students if student.student_id == target), None)

    def search(self, query: str) -> list[Student]:
        """Search exact ID first, otherwise partial case-insensitive name."""
        text = query.strip()
        if not text:
            return []
        normalized = text.upper()
        exact = [student for student in self._students if student.student_id == normalized]
        return exact or [student for student in self._students if text.casefold() in student.name.casefold()]

    def update_marks(self, student_id: str, marks: dict[str, object]) -> Student:
        """Validate all new marks before changing the student."""
        student = self.get_by_id(student_id)
        if student is None:
            raise KeyError(f"Student {normalize_student_id(student_id)} was not found.")
        validated = validate_marks(marks)
        student.marks = validated
        return student

    def delete(self, student_id: str) -> Student:
        """Remove and return a student by ID."""
        student = self.get_by_id(student_id)
        if student is None:
            raise KeyError(f"Student {normalize_student_id(student_id)} was not found.")
        self._students.remove(student)
        return student
