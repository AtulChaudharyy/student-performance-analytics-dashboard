"""
Database management module for Student Performance Analytics Dashboard (SPAD).
Handles SQLite operations, metric calculations, and default data seeding.
"""

import os
import sqlite3
import tempfile
from typing import Dict, Any, List, Optional, Tuple


def get_database_path() -> str:
    """Returns safe database path with fallback to writable directory if needed."""
    if "DATABASE_PATH" in os.environ:
        return os.environ["DATABASE_PATH"]

    target_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        os.makedirs(target_dir, exist_ok=True)
        test_file = os.path.join(target_dir, ".perm_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return os.path.join(target_dir, "students.db")
    except Exception:
        return os.path.join(tempfile.gettempdir(), "students.db")


DEFAULT_DB_PATH = get_database_path()


def calculate_metrics(
    math: float,
    science: float,
    english: float,
    history: float,
    cs: float,
    attendance: float
) -> Tuple[float, float, str, str]:
    """
    Calculate total marks, percentage, grade, and academic status.
    Returns: (total_marks, percentage, grade, status)
    """
    total_marks = round(math + science + english + history + cs, 2)
    percentage = round((total_marks / 500.0) * 100.0, 2)

    # Grade calculation
    if percentage >= 90.0:
        grade = "A+"
    elif percentage >= 80.0:
        grade = "A"
    elif percentage >= 70.0:
        grade = "B"
    elif percentage >= 60.0:
        grade = "C"
    elif percentage >= 50.0:
        grade = "D"
    else:
        grade = "F"

    # Status / Needs Improvement identification
    # A student needs improvement if overall percentage < 50% OR attendance < 75% OR failed in any subject (< 40)
    failed_subject = any(score < 40.0 for score in [math, science, english, history, cs])
    if percentage < 50.0 or attendance < 75.0 or failed_subject:
        status = "Needs Improvement"
    elif percentage >= 85.0 and attendance >= 85.0:
        status = "Distinction"
    else:
        status = "Good Standing"

    return total_marks, percentage, grade, status


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a database connection with concurrency safety and dict-like row access."""
    path = db_path or get_database_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
    except sqlite3.OperationalError:
        pass
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the students table if it doesn't already exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL,
            math_marks REAL NOT NULL,
            science_marks REAL NOT NULL,
            english_marks REAL NOT NULL,
            history_marks REAL NOT NULL,
            cs_marks REAL NOT NULL,
            attendance REAL NOT NULL,
            total_marks REAL NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Check if empty, seed default data
    cursor.execute("SELECT COUNT(*) as count FROM students")
    count = cursor.fetchone()["count"]
    if count == 0:
        seed_default_students(db_path)
    conn.close()


def seed_default_students(db_path: Optional[str] = None) -> None:
    """Seeds realistic student records for initial demonstration."""
    sample_students = [
        ("DS101", "Aarav Sharma", "Data Science", 5, 92, 88, 85, 90, 95, 94.5),
        ("DS102", "Priya Patel", "Data Science", 5, 78, 82, 80, 74, 88, 86.0),
        ("CS103", "Rohan Mehta", "Computer Science", 5, 45, 52, 48, 50, 42, 68.0),
        ("CS104", "Ananya Verma", "Computer Science", 5, 95, 98, 92, 94, 99, 97.0),
        ("AI105", "Kabir Singh", "AI & ML", 5, 62, 58, 65, 70, 60, 78.5),
        ("AI106", "Sneha Rao", "AI & ML", 5, 38, 42, 55, 48, 35, 62.0),
        ("IT107", "Vikram Malhotra", "Information Tech", 5, 84, 86, 79, 82, 90, 89.0),
        ("DS108", "Diya Nair", "Data Science", 5, 72, 75, 78, 80, 74, 83.5),
        ("CS109", "Arjun Reddy", "Computer Science", 5, 54, 48, 60, 52, 58, 71.0),
        ("AI110", "Ishita Joshi", "AI & ML", 5, 88, 91, 89, 85, 93, 92.0),
        ("IT111", "Karan Kapoor", "Information Tech", 5, 32, 38, 45, 40, 36, 58.0),
        ("DS112", "Riya Sen", "Data Science", 5, 89, 93, 87, 88, 94, 91.5)
    ]

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    for s in sample_students:
        roll, name, dept, sem, math, sci, eng, hist, cs, att = s
        tot, pct, grd, sts = calculate_metrics(math, sci, eng, hist, cs, att)
        cursor.execute("""
            INSERT OR IGNORE INTO students (
                roll_number, name, department, semester,
                math_marks, science_marks, english_marks, history_marks, cs_marks,
                attendance, total_marks, percentage, grade, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (roll, name, dept, sem, math, sci, eng, hist, cs, att, tot, pct, grd, sts))
    conn.commit()
    conn.close()


def get_all_students(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all student records."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY roll_number ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_student_by_id(student_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single student record by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_student(data: Dict[str, Any], db_path: Optional[str] = None) -> Dict[str, Any]:
    """Add a new student record."""
    roll = str(data["roll_number"]).strip().upper()
    name = str(data["name"]).strip()
    dept = str(data.get("department", "General")).strip()
    sem = int(data.get("semester", 1))

    math = float(data["math_marks"])
    sci = float(data["science_marks"])
    eng = float(data["english_marks"])
    hist = float(data["history_marks"])
    cs = float(data["cs_marks"])
    att = float(data["attendance"])

    total, pct, grade, status = calculate_metrics(math, sci, eng, hist, cs, att)

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (
            roll_number, name, department, semester,
            math_marks, science_marks, english_marks, history_marks, cs_marks,
            attendance, total_marks, percentage, grade, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        roll, name, dept, sem,
        math, sci, eng, hist, cs, att,
        total, pct, grade, status
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    if new_id is None:
        raise RuntimeError("Insert operation did not return an inserted row ID.")

    saved = get_student_by_id(new_id, db_path)
    if not saved:
        raise RuntimeError(f"Failed to retrieve student with ID {new_id} after creation.")
    return saved


def update_student(student_id: int, data: Dict[str, Any], db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Update an existing student record."""
    student = get_student_by_id(student_id, db_path)
    if not student:
        return None

    math = float(data.get("math_marks", student["math_marks"]))
    sci = float(data.get("science_marks", student["science_marks"]))
    eng = float(data.get("english_marks", student["english_marks"]))
    hist = float(data.get("history_marks", student["history_marks"]))
    cs = float(data.get("cs_marks", student["cs_marks"]))
    att = float(data.get("attendance", student["attendance"]))
    sem = int(data.get("semester", student["semester"]))

    total, pct, grade, status = calculate_metrics(math, sci, eng, hist, cs, att)

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students SET
            roll_number = ?,
            name = ?,
            department = ?,
            semester = ?,
            math_marks = ?,
            science_marks = ?,
            english_marks = ?,
            history_marks = ?,
            cs_marks = ?,
            attendance = ?,
            total_marks = ?,
            percentage = ?,
            grade = ?,
            status = ?
        WHERE id = ?
    """, (
        data.get("roll_number", student["roll_number"]).strip().upper(),
        data.get("name", student["name"]).strip(),
        data.get("department", student["department"]).strip(),
        sem,
        math, sci, eng, hist, cs, att,
        total, pct, grade, status,
        student_id
    ))
    conn.commit()
    conn.close()
    return get_student_by_id(student_id, db_path)


def delete_student(student_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a student record."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_analytics_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate aggregate analytics for dashboard visualizations."""
    students = get_all_students(db_path)
    total_count = len(students)

    if total_count == 0:
        return {
            "total_students": 0,
            "average_percentage": 0.0,
            "average_attendance": 0.0,
            "pass_percentage": 0.0,
            "needs_improvement_count": 0,
            "top_performer": None,
            "grade_distribution": {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
            "subject_averages": {"Math": 0, "Science": 0, "English": 0, "History": 0, "Computer Science": 0},
            "department_averages": {},
            "status_distribution": {"Distinction": 0, "Good Standing": 0, "Needs Improvement": 0}
        }

    total_pct = sum(s["percentage"] for s in students)
    total_att = sum(s["attendance"] for s in students)
    passed_count = sum(1 for s in students if s["percentage"] >= 50.0)
    needs_improvement_count = sum(1 for s in students if s["status"] == "Needs Improvement")

    # Top performer
    top_performer = max(students, key=lambda s: s["percentage"])

    # Grade distribution
    grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in students:
        grades[s["grade"]] = grades.get(s["grade"], 0) + 1

    # Subject averages
    math_avg = round(sum(s["math_marks"] for s in students) / total_count, 2)
    sci_avg = round(sum(s["science_marks"] for s in students) / total_count, 2)
    eng_avg = round(sum(s["english_marks"] for s in students) / total_count, 2)
    hist_avg = round(sum(s["history_marks"] for s in students) / total_count, 2)
    cs_avg = round(sum(s["cs_marks"] for s in students) / total_count, 2)

    # Department averages
    dept_totals: Dict[str, List[float]] = {}
    for s in students:
        dept = s["department"]
        dept_totals.setdefault(dept, []).append(s["percentage"])
    dept_averages = {d: round(sum(vals) / len(vals), 2) for d, vals in dept_totals.items()}

    # Status distribution
    status_dist = {"Distinction": 0, "Good Standing": 0, "Needs Improvement": 0}
    for s in students:
        status_dist[s["status"]] = status_dist.get(s["status"], 0) + 1

    return {
        "total_students": total_count,
        "average_percentage": round(total_pct / total_count, 2),
        "average_attendance": round(total_att / total_count, 2),
        "pass_percentage": round((passed_count / total_count) * 100.0, 2),
        "needs_improvement_count": needs_improvement_count,
        "top_performer": {
            "name": top_performer["name"],
            "roll_number": top_performer["roll_number"],
            "percentage": top_performer["percentage"],
            "grade": top_performer["grade"],
            "department": top_performer["department"]
        },
        "grade_distribution": grades,
        "subject_averages": {
            "Math": math_avg,
            "Science": sci_avg,
            "English": eng_avg,
            "History": hist_avg,
            "Computer Science": cs_avg
        },
        "department_averages": dept_averages,
        "status_distribution": status_dist
    }
