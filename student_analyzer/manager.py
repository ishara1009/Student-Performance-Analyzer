"""Student collection operations with validation before mutation."""

from .models import Student
from .validators import normalize_student_id, validate_marks


class StudentManager:
    """Manage an in-memory list of unique students."""

    def __init__(self, students: list[Student] | None = None) -> None:
        if students is None:
            self._students = []
        else:
            self._students = list(students)

        # A set contains only unique values, so it is useful for finding
        # duplicate IDs while checking the starting student list.
        seen_ids: set[str] = set()
        for student in self._students:
            if student.student_id in seen_ids:
                raise ValueError("Duplicate student IDs are not allowed.")
            seen_ids.add(student.student_id)

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

        for student in self._students:
            if student.student_id == target:
                return student

        return None

    def search(self, query: str) -> list[Student]:
        """Search exact ID first, otherwise partial case-insensitive name."""
        text = query.strip()
        if not text:
            return []
        normalized_id = text.upper()

        # An ID search is exact.
        for student in self._students:
            if student.student_id == normalized_id:
                return [student]

        # A name search can return more than one matching student.
        matching_students = []
        search_text = text.casefold()
        for student in self._students:
            if search_text in student.name.casefold():
                matching_students.append(student)

        return matching_students

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
