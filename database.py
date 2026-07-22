import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "students.db")


def initialize_database():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        usn TEXT NOT NULL,
        branch TEXT NOT NULL,
        semester INTEGER NOT NULL,
        phone TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database Created Successfully!")