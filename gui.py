import tkinter as tk
from tkinter import messagebox, ttk

import sqlite3

from database import DATABASE_PATH, initialize_database


class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1024x680")
        self.root.minsize(960, 640)
        self.root.configure(bg="#f4f7fb")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.name_var = tk.StringVar()
        self.usn_var = tk.StringVar()
        self.branch_var = tk.StringVar()
        self.semester_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self._build_ui()
        self._load_students()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#1f3c88", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Student Management System",
            bg="#1f3c88",
            fg="white",
            font=("Segoe UI", 24, "bold"),
        )
        title.pack(pady=(16, 4))

        subtitle = tk.Label(
            header,
            text="Add, search, update, delete, and manage student records",
            bg="#1f3c88",
            fg="#dce7ff",
            font=("Segoe UI", 10),
        )
        subtitle.pack()

        body = tk.Frame(self.root, bg="#f4f7fb")
        body.pack(fill="both", expand=True, padx=18, pady=18)

        left_panel = tk.Frame(body, bg="white", bd=0, highlightthickness=1, highlightbackground="#dbe4f0")
        left_panel.pack(side="left", fill="y", padx=(0, 14))

        right_panel = tk.Frame(body, bg="white", bd=0, highlightthickness=1, highlightbackground="#dbe4f0")
        right_panel.pack(side="right", fill="both", expand=True)

        form_title = tk.Label(left_panel, text="Student Details", bg="white", fg="#1f2937", font=("Segoe UI", 15, "bold"))
        form_title.pack(anchor="w", padx=18, pady=(18, 8))

        self._add_label_entry(left_panel, "Name", self.name_var)
        self._add_label_entry(left_panel, "USN", self.usn_var)
        self._add_label_entry(left_panel, "Branch", self.branch_var)
        self._add_label_entry(left_panel, "Semester", self.semester_var)
        self._add_label_entry(left_panel, "Phone", self.phone_var)

        button_frame = tk.Frame(left_panel, bg="white")
        button_frame.pack(fill="x", padx=18, pady=(18, 10))

        self._button(button_frame, "Add", self.add_student, "#2563eb").grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))
        self._button(button_frame, "Update", self.update_student, "#0f766e").grid(row=0, column=1, sticky="ew", pady=(0, 8))
        self._button(button_frame, "Delete", self.delete_student, "#dc2626").grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))
        self._button(button_frame, "Clear", self.clear_form, "#64748b").grid(row=1, column=1, sticky="ew", pady=(0, 8))
        self._button(button_frame, "Show All", self._load_students, "#7c3aed").grid(row=2, column=0, sticky="ew", padx=(0, 8))
        self._button(button_frame, "Exit", self.root.destroy, "#334155").grid(row=2, column=1, sticky="ew")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        search_box = tk.Frame(right_panel, bg="white")
        search_box.pack(fill="x", padx=16, pady=(16, 10))

        search_title = tk.Label(search_box, text="Search", bg="white", fg="#1f2937", font=("Segoe UI", 15, "bold"))
        search_title.grid(row=0, column=0, sticky="w", columnspan=4, pady=(0, 10))

        search_label = tk.Label(search_box, text="Name or USN", bg="white", fg="#374151", font=("Segoe UI", 10))
        search_label.grid(row=1, column=0, sticky="w")

        search_entry = tk.Entry(search_box, textvariable=self.search_var, font=("Segoe UI", 11), bd=0, relief="flat", highlightthickness=1, highlightbackground="#cbd5e1", highlightcolor="#2563eb")
        search_entry.grid(row=1, column=1, sticky="ew", padx=(10, 10))

        self._button(search_box, "Search USN", self.search_by_usn, "#2563eb").grid(row=1, column=2, padx=(0, 8))
        self._button(search_box, "Search Name", self.search_by_name, "#0f766e").grid(row=1, column=3)

        search_box.columnconfigure(1, weight=1)

        table_frame = tk.Frame(right_panel, bg="white")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        columns = ("id", "name", "usn", "branch", "semester", "phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("usn", text="USN")
        self.tree.heading("branch", text="Branch")
        self.tree.heading("semester", text="Semester")
        self.tree.heading("phone", text="Phone")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=180)
        self.tree.column("usn", width=140)
        self.tree.column("branch", width=120)
        self.tree.column("semester", width=90, anchor="center")
        self.tree.column("phone", width=130)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def _add_label_entry(self, parent, label_text, variable):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=18, pady=6)

        label = tk.Label(frame, text=label_text, bg="white", fg="#374151", font=("Segoe UI", 10, "bold"))
        label.pack(anchor="w")

        entry = tk.Entry(frame, textvariable=variable, font=("Segoe UI", 11), bd=0, relief="flat", highlightthickness=1, highlightbackground="#cbd5e1", highlightcolor="#2563eb")
        entry.pack(fill="x", pady=(6, 0))

    def _button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=8,
            cursor="hand2",
        )

    def get_connection(self):
        return sqlite3.connect(DATABASE_PATH)

    def validate_form(self):
        name = self.name_var.get().strip()
        usn = self.usn_var.get().strip()
        branch = self.branch_var.get().strip()
        semester = self.semester_var.get().strip()
        phone = self.phone_var.get().strip()

        if not name or not usn or not branch or not semester or not phone:
            messagebox.showerror("Validation Error", "All fields are required.")
            return None

        if not semester.isdigit() or not (1 <= int(semester) <= 8):
            messagebox.showerror("Validation Error", "Semester must be a number between 1 and 8.")
            return None

        if not phone.isdigit() or not (7 <= len(phone) <= 15):
            messagebox.showerror("Validation Error", "Phone number must contain 7 to 15 digits.")
            return None

        return name, usn, branch, int(semester), phone

    def clear_form(self):
        self.name_var.set("")
        self.usn_var.set("")
        self.branch_var.set("")
        self.semester_var.set("")
        self.phone_var.set("")
        self.search_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def _load_students(self, rows=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if rows is None:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id")
            rows = cursor.fetchall()
            connection.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_student(self):
        values = self.validate_form()
        if values is None:
            return

        name, usn, branch, semester, phone = values

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM students WHERE usn = ?", (usn,))
        if cursor.fetchone():
            connection.close()
            messagebox.showerror("Duplicate USN", "A student with this USN already exists.")
            return

        cursor.execute(
            "INSERT INTO students(name, usn, branch, semester, phone) VALUES (?, ?, ?, ?, ?)",
            (name, usn, branch, semester, phone),
        )
        connection.commit()
        connection.close()

        self._load_students()
        self.clear_form()
        messagebox.showinfo("Success", "Student added successfully.")

    def search_by_usn(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showerror("Validation Error", "Enter a USN to search.")
            return

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE usn = ?", (query,))
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            messagebox.showinfo("No Match", "No student found for that USN.")
            return

        self._load_students(rows)

    def search_by_name(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showerror("Validation Error", "Enter a name to search.")
            return

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE LOWER(name) LIKE ? ORDER BY name",
            (f"%{query.lower()}%",),
        )
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            messagebox.showinfo("No Match", "No students matched that name.")
            return

        self._load_students(rows)

    def on_row_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        values = self.tree.item(selection[0], "values")
        self.name_var.set(values[1])
        self.usn_var.set(values[2])
        self.branch_var.set(values[3])
        self.semester_var.set(values[4])
        self.phone_var.set(values[5])

    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Required", "Select a student from the table first.")
            return

        values = self.validate_form()
        if values is None:
            return

        name, usn, branch, semester, phone = values
        current_values = self.tree.item(selected[0], "values")
        current_id = current_values[0]

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM students WHERE usn = ? AND id != ?", (usn, current_id))
        if cursor.fetchone():
            connection.close()
            messagebox.showerror("Duplicate USN", "Another student already uses that USN.")
            return

        cursor.execute(
            """
            UPDATE students
            SET name = ?, usn = ?, branch = ?, semester = ?, phone = ?
            WHERE id = ?
            """,
            (name, usn, branch, semester, phone, current_id),
        )
        connection.commit()
        connection.close()

        self._load_students()
        self.clear_form()
        messagebox.showinfo("Success", "Student updated successfully.")

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Required", "Select a student from the table first.")
            return

        values = self.tree.item(selected[0], "values")
        confirm = messagebox.askyesno("Confirm Delete", f"Delete student {values[1]} ({values[2]})?")
        if not confirm:
            return

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (values[0],))
        connection.commit()
        connection.close()

        self._load_students()
        self.clear_form()
        messagebox.showinfo("Deleted", "Student deleted successfully.")


def main():
    initialize_database()
    root = tk.Tk()
    StudentManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()