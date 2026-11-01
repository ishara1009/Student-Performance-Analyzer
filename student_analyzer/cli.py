"""Interactive terminal interface and application coordination."""

from pathlib import Path

from .calculations import class_statistics, student_result
from .config import REPORTS_DIR, SAMPLE_CSV, STUDENTS_FILE, SUBJECTS
from .manager import StudentManager
from .models import Student
from .reports import ReportError, export_csv, export_txt
from .storage import CSVImportError, StorageError, load_students, read_csv_import, save_students
from .validators import ValidationError, normalize_student_id, validate_mark, validate_name


class CLI:
    """Prompt users and coordinate application modules."""

    def __init__(self, manager: StudentManager, data_path: Path = STUDENTS_FILE) -> None:
        self.manager = manager
        self.data_path = data_path

    def run(self) -> None:
        """Display the menu repeatedly until exit."""
        while True:
            print("\nStudent Performance Analyzer")
            self._show_menu()
            choice = input("Choose an option: ").strip()

            # A simple if/elif menu is longer than a function dictionary, but
            # it is easier to understand while learning Python fundamentals.
            if choice == "0":
                print("Goodbye!")
                return
            elif choice == "1":
                self.add_student()
            elif choice == "2":
                self.view_all()
            elif choice == "3":
                self.search()
            elif choice == "4":
                self.update()
            elif choice == "5":
                self.delete()
            elif choice == "6":
                self.import_csv()
            elif choice == "7":
                self.view_statistics()
            elif choice == "8":
                self.export_reports()
            else:
                print("Invalid choice. Enter a number from 0 to 8.")

    @staticmethod
    def _show_menu() -> None:
        """Print all available menu options."""
        print("1. Add a student")
        print("2. View all students")
        print("3. Search for a student")
        print("4. Update student marks")
        print("5. Delete a student")
        print("6. Import students from CSV")
        print("7. View class statistics")
        print("8. Export reports")
        print("0. Exit")

    def _commit(self, students: list[Student]) -> bool:
        """Save a new list, then use it as the current student list."""
        try:
            save_students(self.data_path, students)
        except StorageError as error:
            print(f"Change was not saved: {error}")
            return False
        self.manager = StudentManager(students)
        return True

    @staticmethod
    def _identity() -> tuple[str, str]:
        while True:
            try:
                student_id = normalize_student_id(input("Student ID: "))
                break
            except ValidationError as error:
                print(error)
        while True:
            try:
                name = validate_name(input("Name: "))
                break
            except ValidationError as error:
                print(error)
        return student_id, name

    @staticmethod
    def _mark(subject: str, current: float | None = None) -> float:
        while True:
            suffix = f" [{current:g}]" if current is not None else ""
            raw = input(f"{subject.title()}{suffix}: ")
            if current is not None and not raw.strip():
                return current
            try:
                return validate_mark(raw, subject.title())
            except ValidationError as error:
                print(error)

    @staticmethod
    def _display(students: list[Student]) -> None:
        if not students:
            print("No student data available.")
            return
        print(f"{'ID':<10} {'Name':<24} {'Python':>8} {'Math':>8} {'English':>8} {'Total':>8} {'Average':>8} {'Grade':>6} {'Status':>8}")
        for student in students:
            result = student_result(student)
            print(f"{student.student_id:<10} {student.name[:24]:<24} {student.marks['python']:>8.2f} {student.marks['mathematics']:>8.2f} {student.marks['english']:>8.2f} {result['total']:>8.2f} {result['average']:>8.2f} {result['grade']:>6} {result['status']:>8}")

    def add_student(self) -> None:
        student_id, name = self._identity()
        if self.manager.get_by_id(student_id):
            print(f"Student ID {student_id} already exists.")
            return
        marks = {}
        for subject in SUBJECTS:
            marks[subject] = self._mark(subject)

        student = Student(student_id, name, marks)
        students_after_add = self.manager.students
        students_after_add.append(student)

        if self._commit(students_after_add):
            print(f"Student {student_id} added and saved.")

    def view_all(self) -> None:
        self._display(self.manager.students)

    def search(self) -> None:
        query = input("Exact ID or part of a name: ")
        matches = self.manager.search(query)
        self._display(matches)
        if not matches:
            print("Search uses exact ID or case-insensitive partial name.")

    def update(self) -> None:
        raw_id = input("Student ID to update: ")
        try:
            student = self.manager.get_by_id(raw_id)
        except ValidationError as error:
            print(error)
            return
        if student is None:
            print("Student was not found.")
            return
        new_marks = {}
        for subject in SUBJECTS:
            old_mark = student.marks[subject]
            new_marks[subject] = self._mark(subject, old_mark)

        replacement = Student(student.student_id, student.name, new_marks)

        staged = []
        for item in self.manager.students:
            if item.student_id == student.student_id:
                staged.append(replacement)
            else:
                staged.append(item)

        if self._commit(staged):
            print(f"Marks for {student.student_id} updated and saved.")

    def delete(self) -> None:
        raw_id = input("Student ID to delete: ")
        try:
            student = self.manager.get_by_id(raw_id)
        except ValidationError as error:
            print(error)
            return
        if student is None:
            print("Student was not found.")
            return
        self._display([student])
        answer = input("Delete this student? (y/n): ").strip().lower()
        if answer != "y":
            print("Deletion cancelled.")
            return
        staged = []
        for item in self.manager.students:
            if item.student_id != student.student_id:
                staged.append(item)

        if self._commit(staged):
            print(f"Student {student.student_id} deleted and saved.")

    def import_csv(self) -> None:
        raw_path = input(f"CSV path [{SAMPLE_CSV}]: ").strip()
        if raw_path:
            path = Path(raw_path).expanduser()
        else:
            path = SAMPLE_CSV

        existing_ids = set()
        for student in self.manager.students:
            existing_ids.add(student.student_id)

        try:
            result = read_csv_import(path, existing_ids)
        except CSVImportError as error:
            print(f"Import failed: {error}")
            return
        for error in result.errors:
            print(error)
        if result.students:
            students_after_import = self.manager.students + result.students
            if not self._commit(students_after_import):
                return
        print(f"Imported: {len(result.students)}, skipped: {result.skipped_count}, blank rows ignored: {result.blank_count}.")

    def view_statistics(self) -> None:
        stats = class_statistics(self.manager.students)
        if stats is None:
            print("No student data available.")
            return
        print(f"Students: {stats['student_count']}\nClass average: {stats['class_average']:.2f}")
        subject_averages = stats["subject_averages"]
        assert isinstance(subject_averages, dict)
        for subject in SUBJECTS:
            print(f"{subject.title()} average: {subject_averages[subject]:.2f}")
        print(f"Highest: {stats['highest_average']:.2f} ({', '.join(s.student_id for s in stats['highest_students'])})")
        print(f"Lowest: {stats['lowest_average']:.2f} ({', '.join(s.student_id for s in stats['lowest_students'])})")
        print(f"Passed: {stats['passed_count']} | Failed: {stats['failed_count']}")

    def export_reports(self) -> None:
        print("1. CSV student results\n2. TXT class report\n3. Both")
        choice = input("Choose report type: ").strip()
        if choice not in {"1", "2", "3"}:
            print("Invalid report choice.")
            return
        if choice == "1":
            exporters = [export_csv]
        elif choice == "2":
            exporters = [export_txt]
        else:
            exporters = [export_csv, export_txt]
        for exporter in exporters:
            try:
                print(f"Created: {exporter(self.manager.students, REPORTS_DIR)}")
            except ReportError as error:
                print(error)


def run() -> None:
    """Load stored data and run the CLI with clean boundary handling."""
    try:
        students = load_students(STUDENTS_FILE)
    except StorageError as error:
        print(f"Storage error: {error}")
        print("Correct the existing file, or back it up and remove it before restarting.")
        return
    try:
        CLI(StudentManager(students)).run()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting safely. Goodbye!")
