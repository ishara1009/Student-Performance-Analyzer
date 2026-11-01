import unittest

from student_analyzer.calculations import average_mark, class_statistics, grade_for_average, has_passed, total_marks
from student_analyzer.models import Student


def student(student_id="ST001", marks=None):
    return Student(student_id, "Test Student", marks or {"python": 75, "mathematics": 60, "english": 45})


class CalculationTests(unittest.TestCase):
    def test_total_and_average(self):
        item = student()
        self.assertEqual(total_marks(item), 180)
        self.assertEqual(average_mark(item), 60)

    def test_exact_grade_boundaries_and_just_below(self):
        cases = [(75, "A"), (74.999, "B"), (65, "B"), (64.999, "C"), (55, "C"), (54.999, "S"), (40, "S"), (39.999, "F")]
        for average, expected in cases:
            with self.subTest(average=average):
                self.assertEqual(grade_for_average(average), expected)

    def test_pass_at_exactly_50(self):
        self.assertTrue(has_passed(student(marks={"python": 40, "mathematics": 50, "english": 60})))

    def test_high_average_fails_when_one_subject_below_40(self):
        self.assertFalse(has_passed(student(marks={"python": 100, "mathematics": 100, "english": 39})))

    def test_all_40_fails_because_average_below_50(self):
        self.assertFalse(has_passed(student(marks={"python": 40, "mathematics": 40, "english": 40})))

    def test_empty_statistics(self):
        self.assertIsNone(class_statistics([]))

    def test_tied_highest_and_lowest(self):
        students = [student("ST001", {"python": 90, "mathematics": 90, "english": 90}), student("ST002", {"python": 90, "mathematics": 90, "english": 90}), student("ST003", {"python": 40, "mathematics": 40, "english": 40}), student("ST004", {"python": 40, "mathematics": 40, "english": 40})]
        stats = class_statistics(students)
        self.assertEqual([s.student_id for s in stats["highest_students"]], ["ST001", "ST002"])
        self.assertEqual([s.student_id for s in stats["lowest_students"]], ["ST003", "ST004"])


if __name__ == "__main__":
    unittest.main()
