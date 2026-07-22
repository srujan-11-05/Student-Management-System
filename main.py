import sqlite3

from database import DATABASE_PATH, initialize_database


MENU_WIDTH = 54


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def prompt_non_empty(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("This field cannot be empty.")


def prompt_choice(message, valid_choices):
    while True:
        value = input(message).strip()
        if value in valid_choices:
            return value
        print(f"Please enter one of these options: {', '.join(valid_choices)}")


def prompt_semester(message):
    while True:
        value = input(message).strip()
        if value.isdigit():
            semester = int(value)
            if 1 <= semester <= 8:
                return semester
        print("Semester must be a number between 1 and 8.")


def prompt_phone(message):
    while True:
        value = input(message).strip()
        if value.isdigit() and 7 <= len(value) <= 15:
            return value
        print("Phone number must contain only digits and be 7 to 15 digits long.")


def print_header(title):
    print("\n" + "=" * MENU_WIDTH)
    print(title.center(MENU_WIDTH))
    print("=" * MENU_WIDTH)


def print_menu():
    print_header("STUDENT MANAGEMENT SYSTEM")
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Student by USN")
    print("4. Search Student by Name")
    print("5. Update Student")
    print("6. Delete Student")
    print("7. Exit")


def print_student_card(student):
    print(f"ID       : {student[0]}")
    print(f"Name     : {student[1]}")
    print(f"USN      : {student[2]}")
    print(f"Branch   : {student[3]}")
    print(f"Semester : {student[4]}")
    print(f"Phone    : {student[5]}")


def print_student_table(students):
    headers = ("ID", "Name", "USN", "Branch", "Sem", "Phone")
    widths = [4, 20, 16, 12, 5, 14]

    def trim(text, width):
        text = str(text)
        return text if len(text) <= width else text[: width - 3] + "..."

    def format_row(values):
        return " | ".join(trim(value, width).ljust(width) for value, width in zip(values, widths))

    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for student in students:
        print(format_row((student[0], student[1], student[2], student[3], student[4], student[5])))


def print_student(student):
    print_student_card(student)


def add_student():
    name = prompt_non_empty("Enter Student Name: ")
    usn = prompt_non_empty("Enter USN: ")
    branch = prompt_non_empty("Enter Branch: ")
    semester = prompt_semester("Enter Semester: ")
    phone = prompt_phone("Enter Phone Number: ")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM students WHERE usn = ?", (usn,))
    existing_student = cursor.fetchone()

    if existing_student:
        print("\n❌ A student with this USN already exists!")
        connection.close()
        return

    cursor.execute(
        "INSERT INTO students(name, usn, branch, semester, phone) VALUES (?, ?, ?, ?, ?)",
        (name, usn, branch, semester, phone)
    )

    connection.commit()
    connection.close()

    print("\n✅ Student Added Successfully!")


def view_students():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students ORDER BY id")
    students = cursor.fetchall()

    print_header("STUDENT LIST")

    if len(students) == 0:
        print("No students found.")
    else:
        print_student_table(students)

    connection.close()


def search_student():
    usn = prompt_non_empty("Enter USN to search: ")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students WHERE usn = ?", (usn,))
    student = cursor.fetchone()

    if student:
        print_header("STUDENT FOUND")
        print_student(student)
    else:
        print("\n❌ Student not found!")

    connection.close()


def search_student_by_name():
    name = prompt_non_empty("Enter Student Name to search: ")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE LOWER(name) LIKE ? ORDER BY name",
        (f"%{name.lower()}%",)
    )
    students = cursor.fetchall()

    print_header("SEARCH RESULTS")

    if students:
        print_student_table(students)
    else:
        print("No students matched that name.")

    connection.close()


def update_student():
    usn = prompt_non_empty("Enter USN of student to update: ")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students WHERE usn = ?", (usn,))
    student = cursor.fetchone()

    if not student:
        print("\n❌ Student not found!")
        connection.close()
        return

    print_header("CURRENT DETAILS")
    print_student(student)
    print("\nEnter new details. Press Enter only if you want to keep the current value.")

    name = input(f"Enter Student Name [{student[1]}]: ").strip() or student[1]
    branch = input(f"Enter Branch [{student[3]}]: ").strip() or student[3]

    while True:
        semester_input = input(f"Enter Semester [{student[4]}]: ").strip()
        if not semester_input:
            semester = student[4]
            break
        if semester_input.isdigit():
            semester = int(semester_input)
            break
        print("Semester must be a number.")

    while True:
        phone_input = input(f"Enter Phone Number [{student[5]}]: ").strip()
        if not phone_input:
            phone = student[5]
            break
        if phone_input.isdigit() and 7 <= len(phone_input) <= 15:
            phone = phone_input
            break
        print("Phone number must contain only digits and be 7 to 15 digits long.")

    cursor.execute(
        """
        UPDATE students
        SET name = ?, branch = ?, semester = ?, phone = ?
        WHERE usn = ?
        """,
        (name, branch, semester, phone, usn)
    )

    connection.commit()
    connection.close()

    print("\n✅ Student Updated Successfully!")


def delete_student():
    usn = prompt_non_empty("Enter USN of student to delete: ")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students WHERE usn = ?", (usn,))
    student = cursor.fetchone()

    if not student:
        print("\n❌ Student not found!")
        connection.close()
        return

    print_header("STUDENT DETAILS")
    print_student(student)

    confirm = prompt_choice("\nAre you sure you want to delete this student? (y/n): ", {"y", "n"})
    if confirm != "y":
        print("\nDelete cancelled.")
        connection.close()
        return

    cursor.execute("DELETE FROM students WHERE usn = ?", (usn,))
    connection.commit()
    connection.close()

    print("\n✅ Student Deleted Successfully!")


def main():
    initialize_database()

    while True:
        print_menu()
        choice = prompt_choice("Enter your choice: ", {"1", "2", "3", "4", "5", "6", "7"})

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            search_student_by_name()
        elif choice == "5":
            update_student()
        elif choice == "6":
            delete_student()
        elif choice == "7":
            print("\nThank You!")
            break


if __name__ == "__main__":
    main()