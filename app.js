const state = {
  students: [],
  editingId: null,
};

const form = document.getElementById("studentForm");
const nameInput = document.getElementById("name");
const usnInput = document.getElementById("usn");
const branchInput = document.getElementById("branch");
const semesterInput = document.getElementById("semester");
const phoneInput = document.getElementById("phone");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const showAllBtn = document.getElementById("showAllBtn");
const clearBtn = document.getElementById("clearBtn");
const studentBody = document.getElementById("studentBody");
const totalCount = document.getElementById("totalCount");
const branchCount = document.getElementById("branchCount");
const selectedCount = document.getElementById("selectedCount");
const submitButton = form.querySelector('button[type="submit"]');
const toast = createToast();

function normalize(value) {
  return value.trim().toLowerCase();
}

function showToast(message, type = "success") {
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.className = "toast";
  }, 2400);
}

function createToast() {
  const node = document.createElement("div");
  node.className = "toast";
  document.body.appendChild(node);
  return node;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function validateForm() {
  const name = nameInput.value.trim();
  const usn = usnInput.value.trim();
  const branch = branchInput.value.trim();
  const semester = semesterInput.value.trim();
  const phone = phoneInput.value.trim();

  if (!name || !usn || !branch || !semester || !phone) {
    showToast("All fields are required.", "error");
    return null;
  }

  const semesterValue = Number(semester);
  if (!Number.isInteger(semesterValue) || semesterValue < 1 || semesterValue > 8) {
    showToast("Semester must be between 1 and 8.", "error");
    return null;
  }

  if (!/^[0-9]{7,15}$/.test(phone)) {
    showToast("Phone must contain 7 to 15 digits.", "error");
    return null;
  }

  return { name, usn, branch, semester: semesterValue, phone };
}

function clearForm() {
  form.reset();
  state.editingId = null;
  submitButton.textContent = "Save Student";
  selectedCount.textContent = "0";
}

function updateStats() {
  totalCount.textContent = String(state.students.length);
  branchCount.textContent = String(new Set(state.students.map((student) => student.branch.toLowerCase())).size);
  selectedCount.textContent = state.editingId ? "1" : "0";
}

function renderStudents(rows = state.students) {
  studentBody.innerHTML = "";

  if (!rows.length) {
    const template = document.getElementById("emptyStateTemplate");
    studentBody.appendChild(template.content.cloneNode(true));
    updateStats();
    return;
  }

  for (const student of rows) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td data-label="ID">${student.id}</td>
      <td data-label="Name">${escapeHtml(student.name)}</td>
      <td data-label="USN">${escapeHtml(student.usn)}</td>
      <td data-label="Branch">${escapeHtml(student.branch)}</td>
      <td data-label="Semester">${student.semester}</td>
      <td data-label="Phone">${escapeHtml(student.phone)}</td>
      <td data-label="Actions">
        <div class="row-actions">
          <button class="edit" type="button" data-action="edit" data-id="${student.id}">Edit</button>
          <button class="delete" type="button" data-action="delete" data-id="${student.id}">Delete</button>
        </div>
      </td>
    `;
    studentBody.appendChild(row);
  }

  updateStats();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }

  return data;
}

async function loadStudents(query = "") {
  const suffix = query ? `?query=${encodeURIComponent(query)}` : "";
  const data = await apiRequest(`/api/students${suffix}`);
  state.students = data.students;
  renderStudents();
}

async function saveStudent(payload) {
  if (state.editingId) {
    await apiRequest(`/api/students/${state.editingId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    showToast("Student updated successfully.");
  } else {
    await apiRequest("/api/students", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("Student added successfully.");
  }

  clearForm();
  await loadStudents(searchInput.value.trim());
}

function startEdit(studentId) {
  const student = state.students.find((item) => item.id === studentId);
  if (!student) return;

  state.editingId = studentId;
  nameInput.value = student.name;
  usnInput.value = student.usn;
  branchInput.value = student.branch;
  semesterInput.value = student.semester;
  phoneInput.value = student.phone;
  submitButton.textContent = "Update Student";
  selectedCount.textContent = "1";
  nameInput.focus();
}

async function removeStudent(studentId) {
  const student = state.students.find((item) => item.id === studentId);
  if (!student) return;

  const confirmed = window.confirm(`Delete ${student.name} (${student.usn})?`);
  if (!confirmed) return;

  await apiRequest(`/api/students/${studentId}`, { method: "DELETE" });
  showToast("Student deleted successfully.");
  if (state.editingId === studentId) clearForm();
  await loadStudents(searchInput.value.trim());
}

async function searchStudents() {
  const query = searchInput.value.trim();
  if (!query) {
    showToast("Enter a name or USN to search.", "error");
    return;
  }

  await loadStudents(query);
  if (!state.students.length) {
    showToast("No matching students found.", "error");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = validateForm();
  if (!payload) return;

  try {
    await saveStudent(payload);
  } catch (error) {
    showToast(error.message, "error");
  }
});

clearBtn.addEventListener("click", () => {
  clearForm();
  loadStudents(searchInput.value.trim()).catch((error) => showToast(error.message, "error"));
});

searchBtn.addEventListener("click", () => {
  searchStudents().catch((error) => showToast(error.message, "error"));
});

showAllBtn.addEventListener("click", () => {
  searchInput.value = "";
  loadStudents().catch((error) => showToast(error.message, "error"));
});

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    searchStudents().catch((error) => showToast(error.message, "error"));
  }
});

studentBody.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const studentId = Number(button.dataset.id);
  const action = button.dataset.action;

  try {
    if (action === "edit") {
      startEdit(studentId);
    }

    if (action === "delete") {
      await removeStudent(studentId);
    }
  } catch (error) {
    showToast(error.message, "error");
  }
});

loadStudents().catch((error) => showToast(error.message, "error"));
