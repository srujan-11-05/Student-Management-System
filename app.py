import sqlite3

from flask import Flask, jsonify, request

from database import DATABASE_PATH, initialize_database


app = Flask(__name__, static_folder=".", static_url_path="")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def student_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "usn": row["usn"],
        "branch": row["branch"],
        "semester": row["semester"],
        "phone": row["phone"],
    }


def validate_payload(payload):
    name = str(payload.get("name", "")).strip()
    usn = str(payload.get("usn", "")).strip()
    branch = str(payload.get("branch", "")).strip()
    semester = str(payload.get("semester", "")).strip()
    phone = str(payload.get("phone", "")).strip()

    if not name or not usn or not branch or not semester or not phone:
        return None, "All fields are required."

    if not semester.isdigit() or not (1 <= int(semester) <= 8):
        return None, "Semester must be a number between 1 and 8."

    if not phone.isdigit() or not (7 <= len(phone) <= 15):
        return None, "Phone number must contain 7 to 15 digits."

    return {
        "name": name,
        "usn": usn,
        "branch": branch,
        "semester": int(semester),
        "phone": phone,
    }, None


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/students", methods=["GET"])
def list_students():
    query = request.args.get("query", "").strip().lower()

    connection = get_connection()
    cursor = connection.cursor()

    if query:
        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE LOWER(name) LIKE ? OR LOWER(usn) LIKE ?
            ORDER BY id
            """,
            (f"%{query}%", f"%{query}%"),
        )
    else:
        cursor.execute("SELECT * FROM students ORDER BY id")

    students = [student_to_dict(row) for row in cursor.fetchall()]
    connection.close()
    return jsonify({"students": students})


@app.route("/api/students", methods=["POST"])
def create_student():
    payload = request.get_json(silent=True) or {}
    student, error = validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM students WHERE usn = ?", (student["usn"],))
    if cursor.fetchone():
        connection.close()
        return jsonify({"error": "A student with this USN already exists."}), 409

    cursor.execute(
        "INSERT INTO students(name, usn, branch, semester, phone) VALUES (?, ?, ?, ?, ?)",
        (student["name"], student["usn"], student["branch"], student["semester"], student["phone"]),
    )
    connection.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM students WHERE id = ?", (new_id,))
    created = student_to_dict(cursor.fetchone())
    connection.close()

    return jsonify({"student": created}), 201


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    payload = request.get_json(silent=True) or {}
    student, error = validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
    if not cursor.fetchone():
        connection.close()
        return jsonify({"error": "Student not found."}), 404

    cursor.execute("SELECT id FROM students WHERE usn = ? AND id != ?", (student["usn"], student_id))
    if cursor.fetchone():
        connection.close()
        return jsonify({"error": "Another student already uses that USN."}), 409

    cursor.execute(
        """
        UPDATE students
        SET name = ?, usn = ?, branch = ?, semester = ?, phone = ?
        WHERE id = ?
        """,
        (student["name"], student["usn"], student["branch"], student["semester"], student["phone"], student_id),
    )
    connection.commit()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    updated = student_to_dict(cursor.fetchone())
    connection.close()

    return jsonify({"student": updated})


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
    if not cursor.fetchone():
        connection.close()
        return jsonify({"error": "Student not found."}), 404

    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    connection.commit()
    connection.close()
    return jsonify({"message": "Student deleted successfully."})


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
