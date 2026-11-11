"""Flask application for the AI Student Record Manager."""
import json
import os
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from ai_helper import analyze_performance, generate_study_tips, AIConfigurationError, AIServiceError

load_dotenv()
app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("students.json")
DATA_LOCK = threading.Lock()


def load_students():
    """Load records from JSON; recover safely if the file is missing or invalid."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("The JSON root must be a list.")
        return data
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        app.logger.error("Could not load students.json: %s", exc)
        return []


def save_students(students):
    """Write records atomically so an interrupted save is less likely to corrupt data."""
    temp_file = DATA_FILE.with_suffix(".json.tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)
    temp_file.replace(DATA_FILE)


students = load_students()


def calculate_result(marks):
    total = sum(marks.values())
    average = round(total / len(marks), 2)
    if average >= 85:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"
    return total, average, grade


def validate_student(payload, existing_id=None):
    if not isinstance(payload, dict):
        raise ValueError("Please submit student information.")
    student_id = str(payload.get("id", "")).strip()
    name = str(payload.get("name", "")).strip()
    student_class = str(payload.get("class", "")).strip()
    subjects = payload.get("subjects", [])
    marks_input = payload.get("marks", [])

    if not student_id or not name or not student_class:
        raise ValueError("Student ID, name and class/semester are required.")
    if not isinstance(subjects, list) or not isinstance(marks_input, list):
        raise ValueError("Subjects and marks must be lists.")
    if not subjects or len(subjects) != len(marks_input):
        raise ValueError("Enter the same non-zero number of subjects and marks.")
    clean_subjects = [str(subject).strip() for subject in subjects]
    if any(not subject for subject in clean_subjects):
        raise ValueError("Subject names cannot be empty.")
    if len({subject.casefold() for subject in clean_subjects}) != len(clean_subjects):
        raise ValueError("Subject names must not be duplicated.")

    marks = {}
    for subject, raw_mark in zip(clean_subjects, marks_input):
        try:
            mark = float(raw_mark)
        except (TypeError, ValueError):
            raise ValueError(f"Marks for {subject} must be numeric.")
        if not 0 <= mark <= 100:
            raise ValueError(f"Marks for {subject} must be between 0 and 100.")
        marks[subject] = int(mark) if mark.is_integer() else mark

    total, average, grade = calculate_result(marks)
    return {
        "id": student_id,
        "name": name,
        "class": student_class,
        "marks": marks,
        "total": total,
        "average": average,
        "grade": grade,
    }


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/students")
def get_students():
    return jsonify(students)


@app.post("/api/students")
def add_student():
    try:
        record = validate_student(request.get_json(silent=True))
        with DATA_LOCK:
            if any(item.get("id", "").casefold() == record["id"].casefold() for item in students):
                return jsonify({"error": "That Student ID already exists."}), 409
            students.append(record)
            save_students(students)
        return jsonify({"message": "Student added successfully.", "student": record}), 201
    except (ValueError, OSError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.put("/api/students/<student_id>")
def update_student(student_id):
    try:
        payload = request.get_json(silent=True) or {}
        payload["id"] = student_id  # Student ID is fixed by the URL.
        record = validate_student(payload, existing_id=student_id)
        with DATA_LOCK:
            index = next((i for i, item in enumerate(students)
                          if item.get("id", "").casefold() == student_id.casefold()), None)
            if index is None:
                return jsonify({"error": "Student not found."}), 404
            record["id"] = students[index]["id"]
            students[index] = record
            save_students(students)
        return jsonify({"message": "Student updated successfully.", "student": record})
    except (ValueError, OSError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.delete("/api/students/<student_id>")
def delete_student(student_id):
    with DATA_LOCK:
        index = next((i for i, item in enumerate(students)
                      if item.get("id", "").casefold() == student_id.casefold()), None)
        if index is None:
            return jsonify({"error": "Student not found."}), 404
        del students[index]
        try:
            save_students(students)
        except OSError as exc:
            return jsonify({"error": f"Could not save changes: {exc}"}), 500
    return jsonify({"message": "Student deleted successfully."})


@app.post("/api/ai/<kind>/<student_id>")
def student_ai(kind, student_id):
    if kind not in ("analyze", "tips"):
        return jsonify({"error": "Unknown AI request. Use 'analyze' or 'tips'."}), 400
    student = next((item for item in students
                    if item.get("id", "").casefold() == student_id.casefold()), None)
    if student is None:
        return jsonify({"error": "Student not found."}), 404
    try:
        # The AI helper deliberately receives no student name or ID in its prompt.
        answer = analyze_performance(student) if kind == "analyze" else generate_study_tips(student)
        return jsonify({"response": answer})
    except AIConfigurationError as exc:
        return jsonify({"error": str(exc)}), 503
    except AIServiceError as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    print("\nAI Student Record Manager is running!")
    print(f"Open this link in Chrome: {url}")
    print("(Press Ctrl+C in this terminal to stop the app)\n")
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        pass
    else:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
