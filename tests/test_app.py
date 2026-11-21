"""
Unit and Integration Tests for Student Performance Analytics Dashboard (SPAD)
Run with: pytest tests/
"""

import os
import tempfile
import pytest
from app import app
from data.database import (
    calculate_metrics,
    init_db,
    add_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
    get_analytics_summary
)


@pytest.fixture
def client():
    """Create a test client with an isolated temporary SQLite database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app.config["TESTING"] = True

    # Initialize schema and seed in temp db
    init_db(db_path)

    # Monkeypatch default db path for testing
    import data.database
    original_path = data.database.DEFAULT_DB_PATH
    data.database.DEFAULT_DB_PATH = db_path

    with app.test_client() as test_client:
        yield test_client

    # Cleanup
    data.database.DEFAULT_DB_PATH = original_path
    os.close(db_fd)
    import gc
    gc.collect()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass


class TestMetricsCalculation:
    """Test business logic and calculation rules."""

    def test_distinction_and_aplus(self):
        total, pct, grade, status = calculate_metrics(95, 92, 90, 94, 98, 95.0)
        assert total == 469.0
        assert pct == 93.8
        assert grade == "A+"
        assert status == "Distinction"

    def test_grade_b_and_good_standing(self):
        total, pct, grade, status = calculate_metrics(75, 70, 72, 78, 80, 85.0)
        assert total == 375.0
        assert pct == 75.0
        assert grade == "B"
        assert status == "Good Standing"

    def test_low_attendance_triggers_needs_improvement(self):
        # Good marks (80%) but attendance is 65% (< 75%)
        total, pct, grade, status = calculate_metrics(80, 80, 80, 80, 80, 65.0)
        assert pct == 80.0
        assert status == "Needs Improvement"

    def test_subject_failure_triggers_needs_improvement(self):
        # Score in one subject is 30 (< 40)
        total, pct, grade, status = calculate_metrics(30, 80, 80, 80, 80, 90.0)
        assert status == "Needs Improvement"

    def test_failing_grade_f(self):
        total, pct, grade, status = calculate_metrics(35, 30, 40, 32, 25, 55.0)
        assert pct < 50.0
        assert grade == "F"
        assert status == "Needs Improvement"


class TestDatabaseOperations:
    """Test data tier CRUD operations."""

    def test_add_and_retrieve_student(self, client):
        sample = {
            "roll_number": "TEST999",
            "name": "Integration Test Student",
            "department": "Data Science",
            "semester": 4,
            "math_marks": 85,
            "science_marks": 80,
            "english_marks": 90,
            "history_marks": 88,
            "cs_marks": 92,
            "attendance": 91.0
        }
        res = client.post("/api/students", json=sample)
        assert res.status_code == 201
        data = res.get_json()["data"]
        assert data["roll_number"] == "TEST999"
        assert data["grade"] == "A"
        assert data["status"] == "Distinction"

    def test_duplicate_roll_number_rejected(self, client):
        sample = {
            "roll_number": "DUP101",
            "name": "First Entry",
            "department": "Computer Science",
            "semester": 3,
            "math_marks": 70,
            "science_marks": 70,
            "english_marks": 70,
            "history_marks": 70,
            "cs_marks": 70,
            "attendance": 80.0
        }
        res1 = client.post("/api/students", json=sample)
        assert res1.status_code == 201

        # Second attempt with same roll number
        res2 = client.post("/api/students", json=sample)
        assert res2.status_code == 409
        assert "already exists" in res2.get_json()["error"]


class TestFlaskEndpoints:
    """Test HTTP API routes and responses."""

    def test_index_route(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert b"Student Performance Analytics Dashboard" in res.data

    def test_health_check_endpoint(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        payload = res.get_json()
        assert payload["status"] == "healthy"
        assert payload["database"] == "connected"
        assert "students_recorded" in payload

    def test_analytics_endpoint(self, client):
        res = client.get("/api/analytics")
        assert res.status_code == 200
        data = res.get_json()["data"]
        assert "total_students" in data
        assert "grade_distribution" in data
        assert "subject_averages" in data
        assert "status_distribution" in data
        assert data["total_students"] > 0

    def test_export_csv_endpoint(self, client):
        res = client.get("/api/export")
        assert res.status_code == 200
        assert res.content_type.startswith("text/csv")
        assert b"Roll Number,Name,Department" in res.data

    def test_invalid_input_validation(self, client):
        # Missing required fields
        res = client.post("/api/students", json={"name": "Incomplete"})
        assert res.status_code == 400

        # Out of bounds mark (>100)
        invalid_score = {
            "roll_number": "INV01",
            "name": "Invalid Score Student",
            "department": "AI & ML",
            "semester": 1,
            "math_marks": 150,  # Invalid
            "science_marks": 80,
            "english_marks": 80,
            "history_marks": 80,
            "cs_marks": 80,
            "attendance": 80
        }
        res2 = client.post("/api/students", json=invalid_score)
        assert res2.status_code == 400
