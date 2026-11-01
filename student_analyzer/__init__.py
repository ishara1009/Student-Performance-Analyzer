"""Student Performance Analyzer package."""

from .models import Student
from .manager import StudentManager

__all__ = ["Student", "StudentManager"]
