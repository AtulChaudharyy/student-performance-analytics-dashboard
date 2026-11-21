"""
Student Performance Analytics Dashboard (SPAD)
Flask Backend Application
"""

import os
import csv
import io
import datetime
from flask import Flask, render_template, request, jsonify, Response
from data.database import (
    init_db,
    get_all_students,
    get_student_by_id,
    add_student,
    update_student,
    delete_student,
    get_analytics_summary,
    seed_default_students
)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Initialize the database on application startup
with app.app_context():
    init_db()


@app.route("/")
def index():
    """Renders the main analytics dashboard."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint for Docker container and Cloud monitoring."""
    try:
        summary = get_analytics_summary()
        return jsonify({
            "status": "healthy",
            "service": "Student Performance Analytics Dashboard",
            "version": "1.0.0",
            "database": "connected",
            "students_recorded": summary["total_students"],
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }), 500


@app.route("/api/students", methods=["GET"])
def api_get_students():
    """Returns all student records."""
    try:
        students = get_all_students()
        return jsonify({"success": True, "data": students, "count": len(students)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/students", methods=["POST"])
def api_add_student():
    """Creates a new student record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body must be JSON."}), 400

        required_fields = [
            "roll_number", "name", "department", "semester",
            "math_marks", "science_marks", "english_marks", "history_marks",
            "cs_marks", "attendance"
        ]
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                return jsonify({"success": False, "error": f"Missing required field: '{field}'."}), 400

        # Validate score ranges
        score_fields = ["math_marks", "science_marks", "english_marks", "history_marks", "cs_marks"]
        for sf in score_fields:
            val = float(data[sf])
            if val < 0 or val > 100:
                return jsonify({"success": False, "error": f"{sf} must be between 0 and 100."}), 400

        att = float(data["attendance"])
        if att < 0 or att > 100:
            return jsonify({"success": False, "error": "Attendance must be between 0 and 100."}), 400

        created = add_student(data)
        return jsonify({"success": True, "message": "Student created successfully.", "data": created}), 201

    except Exception as e:
        err_msg = str(e)
        if "UNIQUE constraint failed" in err_msg:
            return jsonify({"success": False, "error": "A student with this Roll Number already exists."}), 409
        return jsonify({"success": False, "error": err_msg}), 500


@app.route("/api/students/<int:student_id>", methods=["GET"])
def api_get_student(student_id):
    """Retrieves a single student by ID."""
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"success": False, "error": f"Student with ID {student_id} not found."}), 404
    return jsonify({"success": True, "data": student}), 200


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def api_update_student(student_id):
    """Updates an existing student by ID."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body must be JSON."}), 400

        updated = update_student(student_id, data)
        if not updated:
            return jsonify({"success": False, "error": f"Student with ID {student_id} not found."}), 404
        return jsonify({"success": True, "message": "Student updated successfully.", "data": updated}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def api_delete_student(student_id):
    """Deletes a student by ID."""
    try:
        deleted = delete_student(student_id)
        if not deleted:
            return jsonify({"success": False, "error": f"Student with ID {student_id} not found."}), 404
        return jsonify({"success": True, "message": "Student deleted successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    """Returns analytics data for the dashboard charts and counters."""
    try:
        summary = get_analytics_summary()
        return jsonify({"success": True, "data": summary}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export", methods=["GET"])
def api_export_csv():
    """Exports all student records as a downloadable CSV."""
    students = get_all_students()
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Roll Number", "Name", "Department", "Semester",
        "Mathematics", "Science", "English", "History", "Computer Science",
        "Attendance (%)", "Total Marks", "Percentage (%)", "Grade", "Status"
    ])

    for s in students:
        writer.writerow([
            s["id"], s["roll_number"], s["name"], s["department"], s["semester"],
            s["math_marks"], s["science_marks"], s["english_marks"], s["history_marks"], s["cs_marks"],
            s["attendance"], s["total_marks"], s["percentage"], s["grade"], s["status"]
        ])

    output.seek(0)
    filename = f"student_analytics_{datetime.date.today().strftime('%Y%m%d')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@app.route("/api/reset-data", methods=["POST"])
def api_reset_data():
    """Resets and re-seeds default student data."""
    try:
        # Re-seed default
        seed_default_students()
        return jsonify({"success": True, "message": "Default sample data restored successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
