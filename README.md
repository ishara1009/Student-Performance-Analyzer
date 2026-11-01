# Student Performance Analyzer

A beginner-friendly Python 3.11+ command-line portfolio project for practising the fundamentals used in an AI/Python internship. It stores students, calculates results and class statistics, imports CSV data, and exports reports. It uses only the Python standard library—there are no packages to install.

## Features

- Add, list, search, update, and delete students
- Exact normalized-ID search or case-insensitive partial-name search
- Validated integer/decimal marks for Python, Mathematics, and English
- Safe JSON persistence using a temporary file and atomic replacement
- Validated CSV import with BOM support, row errors, and duplicate detection
- Class statistics, tied highest/lowest students, grades, and pass/fail results
- Unique timestamped CSV and TXT reports
- `unittest` test suite using temporary directories

## Install and run

Install Python 3.11 or newer, clone/download this folder, and open a terminal in it. No virtual environment or third-party dependency is required.

Windows PowerShell:

```powershell
python main.py
python -m unittest discover -s tests
```

macOS/Linux:

```bash
python3 main.py
python3 -m unittest discover -s tests
```

## Project structure

```text
student-performance-analyzer/
├── main.py
├── README.md
├── .gitignore
├── student_analyzer/
│   ├── __init__.py
│   ├── models.py
│   ├── manager.py
│   ├── calculations.py
│   ├── validators.py
│   ├── storage.py
│   ├── reports.py
│   ├── cli.py
│   └── config.py
├── data/
│   └── sample_students.csv
├── reports/
│   └── .gitkeep
└── tests/
    ├── __init__.py
    ├── test_calculations.py
    ├── test_validators.py
    └── test_storage.py
```

`data/students.json` is created after the first successful change and is ignored by Git. A missing file represents a new, empty collection.

## CSV import

Columns must appear in this exact order:

```csv
student_id,name,python,mathematics,english
ST001,Demo Student 01,85,72,68
ST002,Demo Student 02,92,88,91
```

Choose menu option `6`, then press Enter to import `data/sample_students.csv`, or enter another CSV path. Invalid rows are skipped with line-numbered reasons. Existing IDs and repeated IDs are skipped; the first valid occurrence wins. Import is staged and saved once. Reimporting the sample adds zero duplicates.

The 20 supplied sample records are synthetic demonstration records, not real student data.

## Calculations

Total is the sum of three marks (maximum 300), and average is total divided by three. Displayed numbers have two decimal places, while grade and status use the unrounded average.

| Average | Grade |
|---:|:---|
| 75 or higher | A |
| 65 to below 75 | B |
| 55 to below 65 | C |
| 40 to below 55 | S |
| Below 40 | F |

A student passes only when **every subject is at least 40 and the overall average is at least 50**. Grade and pass/fail are separate: a high average-based grade can still have `Failed` status when one subject is below 40.

Class statistics include the student count, mean of student averages, each subject average, highest/lowest average with all ties, and passed/failed counts. An empty class reports `No student data available`.

## Persistence and reports

JSON is stored as an array of student dictionaries in `data/students.json`. Loading rejects malformed JSON, a wrong top-level type, invalid records, and duplicate IDs. It never silently replaces damaged data. Writes use a temporary file beside the destination followed by atomic replacement.

Choose option `8` to export CSV results, a TXT class report, or both. Files are written under `reports/` with unique timestamps. Empty data is not exported. CSV includes identity, marks, total, average, grade, and status; TXT also includes generation time, statistics, results, and rules.

## Example session

```text
Student Performance Analyzer
1. Add a student
...
6. Import students from CSV
...
Choose an option: 6
CSV path [.../data/sample_students.csv]:
Imported: 20, skipped: 0, blank rows ignored: 0.
```

## Python fundamentals used

| Topic | Where it is used |
|---|---|
| Classes and objects | `Student` and `StudentManager` |
| Lists | Ordered student collection |
| Dictionaries | Marks, JSON records, calculated results |
| Tuples | Fixed subject names and grade thresholds |
| Sets | Duplicate-ID detection during import/load |
| Functions | Pure calculations and validators |
| Loops and conditions | Menu, searches, grade and import rules |
| Exceptions | Clear validation, storage, import, and report failures |
| File handling | JSON, CSV, and TXT files with `pathlib` |
| Type hints | Public functions and methods |
| Unit testing | Boundaries, invalid inputs, corruption, and round trips |

## Design and limitations

`main.py` starts `cli.py`. The CLI coordinates `StudentManager`, storage, calculations, and reports. The model calls shared validators; calculations and reports reuse the same configured rules. `config.py` is the single source for paths, subjects, and thresholds, avoiding circular imports and duplicated settings.

This is a local CLI for one process at a time. It has three fixed subjects, no concurrent-write locking, no web interface, database, AI prediction, or production deployment. All supplied data is synthetic.
