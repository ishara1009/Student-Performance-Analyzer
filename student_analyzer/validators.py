"""Reusable validation and normalization helpers."""

import math
from collections.abc import Mapping
from numbers import Real

from .config import SUBJECTS


class ValidationError(ValueError):
    """Raised when student data does not satisfy the application rules."""


def normalize_student_id(value: object) -> str:
    """Return a trimmed, uppercase student ID."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Student ID must be a nonempty string.")
    return value.strip().upper()


def validate_name(value: object) -> str:
    """Return a trimmed, nonempty student name."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Name must be a nonempty string.")
    return value.strip()


def validate_mark(value: object, subject: str = "Mark") -> float:
    """Convert a finite numeric mark in the inclusive range 0-100."""
    if isinstance(value, bool) or value is None:
        raise ValidationError(f"{subject} must be a number from 0 to 100.")
    if isinstance(value, str):
        if not value.strip():
            raise ValidationError(f"{subject} must not be blank.")
        try:
            number = float(value.strip())
        except ValueError as error:
            raise ValidationError(f"{subject} must be numeric.") from error
    elif isinstance(value, Real):
        number = float(value)
    else:
        raise ValidationError(f"{subject} must be numeric.")
    if not math.isfinite(number):
        raise ValidationError(f"{subject} must be finite.")
    if not 0 <= number <= 100:
        raise ValidationError(f"{subject} must be from 0 to 100.")
    return number


def validate_marks(marks: object) -> dict[str, float]:
    """Validate an exact subject-to-mark mapping."""
    if not isinstance(marks, Mapping):
        raise ValidationError("Marks must be a subject dictionary.")
    actual = set(marks)
    expected = set(SUBJECTS)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise ValidationError("Subject keys are invalid (" + "; ".join(details) + ").")
    return {subject: validate_mark(marks[subject], subject.title()) for subject in SUBJECTS}
