import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from student_analyzer.config import SAMPLE_CSV
from student_analyzer.models import Student
from student_analyzer.storage import CSVImportError, StorageError, load_students, read_csv_import, save_students


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_missing_json_loads_empty(self):
        self.assertEqual(load_students(self.directory / "missing.json"), [])

    def test_round_trip(self):
        path = self.directory / "students.json"
        original = [Student("st001", "Ada", {"python": 80, "mathematics": 70, "english": 60})]
        save_students(path, original)
        self.assertEqual(load_students(path)[0].to_dict(), original[0].to_dict())

    def test_corrupt_json_raises_and_is_unchanged(self):
        path = self.directory / "students.json"
        path.write_text("{broken", encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaises(StorageError):
            load_students(path)
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_and_duplicate_stored_records(self):
        path = self.directory / "students.json"
        path.write_text(json.dumps([{"student_id": "ST1", "name": "A", "marks": {"python": 101, "mathematics": 2, "english": 3}}]), encoding="utf-8")
        with self.assertRaises(StorageError):
            load_students(path)
        valid = Student("ST1", "A", {"python": 1, "mathematics": 2, "english": 3}).to_dict()
        path.write_text(json.dumps([valid, valid]), encoding="utf-8")
        with self.assertRaises(StorageError):
            load_students(path)

    def test_sample_import_and_reimport(self):
        first = read_csv_import(SAMPLE_CSV)
        self.assertEqual(len(first.students), 20)
        second = read_csv_import(SAMPLE_CSV, {student.student_id for student in first.students})
        self.assertEqual(len(second.students), 0)
        self.assertEqual(second.duplicate_count, 20)

    def test_invalid_rows_have_line_reasons(self):
        path = self.directory / "badrows.csv"
        path.write_text("student_id,name,python,mathematics,english\nST1,A,50,no,60\nST2,B,50,60,70\n", encoding="utf-8")
        result = read_csv_import(path)
        self.assertEqual(len(result.students), 1)
        self.assertIn("Line 2", result.errors[0])

    def test_bad_headers_rejected(self):
        path = self.directory / "headers.csv"
        path.write_text("name,student_id,python,mathematics,english\n", encoding="utf-8")
        with self.assertRaises(CSVImportError):
            read_csv_import(path)

    def test_utf8_bom(self):
        path = self.directory / "bom.csv"
        path.write_text("student_id,name,python,mathematics,english\nST1,Áda,1,2,3\n", encoding="utf-8-sig")
        self.assertEqual(read_csv_import(path).students[0].name, "Áda")

    def test_failed_save_preserves_previous_file(self):
        path = self.directory / "students.json"
        original = [Student("ST1", "A", {"python": 1, "mathematics": 2, "english": 3})]
        save_students(path, original)
        before = path.read_bytes()
        with patch("pathlib.Path.replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(StorageError):
                save_students(path, [Student("ST2", "B", {"python": 4, "mathematics": 5, "english": 6})])
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
