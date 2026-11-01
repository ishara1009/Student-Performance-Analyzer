import math
import unittest

from student_analyzer.models import Student
from student_analyzer.validators import ValidationError, normalize_student_id, validate_mark, validate_name, validate_marks


class ValidatorTests(unittest.TestCase):
    def test_empty_id_and_name(self):
        for function in (normalize_student_id, validate_name):
            with self.assertRaises(ValidationError):
                function("   ")

    def test_trim_and_normalize(self):
        item = Student(" st001 ", "  Ada Lovelace ", {"python": 1, "mathematics": 2, "english": 3})
        self.assertEqual((item.student_id, item.name), ("ST001", "Ada Lovelace"))

    def test_boundaries_and_decimals(self):
        self.assertEqual(validate_mark(0), 0)
        self.assertEqual(validate_mark(100), 100)
        self.assertEqual(validate_mark("52.5"), 52.5)

    def test_out_of_range(self):
        for value in (-1, 100.01):
            with self.assertRaises(ValidationError):
                validate_mark(value)

    def test_invalid_mark_types_and_values(self):
        for value in ("word", "", " ", True, None, math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_mark(value)

    def test_subject_keys_must_be_exact(self):
        for marks in ({"python": 1, "mathematics": 2}, {"python": 1, "mathematics": 2, "english": 3, "science": 4}):
            with self.assertRaises(ValidationError):
                validate_marks(marks)


if __name__ == "__main__":
    unittest.main()
