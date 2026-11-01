"""Validated student domain model."""

from dataclasses import dataclass

from .validators import normalize_student_id, validate_marks, validate_name


@dataclass
class Student:
    """Store one student's identity and fixed subject marks."""

    student_id: str
    name: str
    marks: dict[str, float]

    def __post_init__(self) -> None:
        self.student_id = normalize_student_id(self.student_id)
        self.name = validate_name(self.name)
        self.marks = validate_marks(self.marks)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable dictionary."""
        return {"student_id": self.student_id, "name": self.name, "marks": self.marks.copy()}

    @classmethod
    def from_dict(cls, data: object) -> "Student":
        """Construct and validate a student from stored data."""
        if not isinstance(data, dict):
            raise ValueError("Student record must be an object.")
        expected = {"student_id", "name", "marks"}
        if set(data) != expected:
            raise ValueError("Student record must contain only student_id, name, and marks.")
        return cls(data["student_id"], data["name"], data["marks"])  # type: ignore[arg-type]
