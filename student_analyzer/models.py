"""The Student class used throughout the project."""

from .validators import normalize_student_id, validate_marks, validate_name


class Student:
    """Store one student's ID, name, and subject marks."""

    def __init__(self, student_id: str, name: str, marks: dict[str, object]) -> None:
        # Validate data before saving it inside the object.  This means every
        # Student object in the program can be trusted to contain valid data.
        self.student_id = normalize_student_id(student_id)
        self.name = validate_name(name)
        self.marks = validate_marks(marks)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable dictionary."""
        student_data = {
            "student_id": self.student_id,
            "name": self.name,
            "marks": self.marks.copy(),
        }
        return student_data

    @classmethod
    def from_dict(cls, data: object) -> "Student":
        """Construct and validate a student from stored data."""
        if not isinstance(data, dict):
            raise ValueError("Student record must be an object.")
        expected_keys = {"student_id", "name", "marks"}
        actual_keys = set(data.keys())

        if actual_keys != expected_keys:
            raise ValueError("Student record must contain only student_id, name, and marks.")

        student_id = data["student_id"]
        name = data["name"]
        marks = data["marks"]
        return cls(student_id, name, marks)  # type: ignore[arg-type]
