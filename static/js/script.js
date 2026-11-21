/**
 * Student Performance Analytics Dashboard (SPAD)
 * Client-Side JavaScript Application
 */

let allStudents = [];
let filteredStudents = [];
let chartInstances = {};
let currentSortColumn = -1;
let sortAscending = true;

// DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
    calcPreview();
});

/**
 * Fetch students and analytics from Flask backend
 */
async function loadDashboardData() {
    try {
        const [studentsRes, analyticsRes] = await Promise.all([
            fetch("/api/students"),
            fetch("/api/analytics")
        ]);

        const studentsData = await studentsRes.json();
        const analyticsData = await analyticsRes.json();

        if (studentsData.success && analyticsData.success) {
            allStudents = studentsData.data;
            filteredStudents = [...allStudents];
            renderKPIs(analyticsData.data);
            try {
                renderCharts(analyticsData.data);
            } catch (chartErr) {
                console.warn("Chart rendering warning:", chartErr);
            }
            renderTable(filteredStudents);
        } else {
            showAlert("Failed to load dashboard data.", true);
        }
    } catch (err) {
        console.error("Error loading dashboard data:", err);
        showAlert("Error connecting to server. Is the backend running?", true);
    }
}

/**
 * Update KPI cards with aggregate metrics
 */
function renderKPIs(analytics) {
    document.getElementById("kpiTotalStudents").textContent = analytics.total_students;
    document.getElementById("kpiAvgScore").textContent = `${analytics.average_percentage}%`;
    document.getElementById("kpiPassRate").textContent = `${analytics.pass_percentage}%`;
    document.getElementById("kpiAttendance").textContent = `${analytics.average_attendance}%`;
    document.getElementById("kpiNeedsImprovement").textContent = analytics.needs_improvement_count;

    if (analytics.top_performer) {
        document.getElementById("kpiTopName").textContent = analytics.top_performer.name;
        document.getElementById("kpiTopDetails").innerHTML = 
            `<i class="fa-solid fa-trophy"></i> ${analytics.top_performer.percentage}% (${analytics.top_performer.grade}) • ${analytics.top_performer.department}`;
    } else {
        document.getElementById("kpiTopName").textContent = "N/A";
        document.getElementById("kpiTopDetails").textContent = "No data recorded";
    }
}

/**
 * Render or update Chart.js visualizations
 */
function renderCharts(analytics) {
    if (typeof Chart === "undefined") {
        console.warn("Chart.js is not loaded.");
        return;
    }

    // 1. Grade Distribution Chart
    try {
        const gradeCanvas = document.getElementById("gradeChart");
        if (gradeCanvas) {
            const gradeCtx = gradeCanvas.getContext("2d");
            if (chartInstances.gradeChart) chartInstances.gradeChart.destroy();
            
            const gradeLabels = Object.keys(analytics.grade_distribution || {});
            const gradeCounts = Object.values(analytics.grade_distribution || {});
            
            chartInstances.gradeChart = new Chart(gradeCtx, {
                type: "doughnut",
                data: {
                    labels: gradeLabels,
                    datasets: [{
                        data: gradeCounts,
                        backgroundColor: [
                            "#10b981", // A+ Emerald
                            "#3b82f6", // A Blue
                            "#8b5cf6", // B Purple
                            "#f59e0b", // C Amber
                            "#f97316", // D Orange
                            "#ef4444"  // F Red
                        ],
                        borderWidth: 2,
                        borderColor: "#ffffff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } }
                    },
                    cutout: "65%"
                }
            });
        }
    } catch (e) {
        console.error("Error creating gradeChart:", e);
    }

    // 2. Subject-Wise Average Scores
    try {
        const subjectCanvas = document.getElementById("subjectChart");
        if (subjectCanvas) {
            const subjectCtx = subjectCanvas.getContext("2d");
            if (chartInstances.subjectChart) chartInstances.subjectChart.destroy();

            const subjectLabels = Object.keys(analytics.subject_averages || {});
            const subjectVals = Object.values(analytics.subject_averages || {});

            chartInstances.subjectChart = new Chart(subjectCtx, {
                type: "bar",
                data: {
                    labels: subjectLabels,
                    datasets: [{
                        label: "Average Score",
                        data: subjectVals,
                        backgroundColor: [
                            "rgba(79, 70, 229, 0.8)",
                            "rgba(6, 182, 212, 0.8)",
                            "rgba(16, 185, 129, 0.8)",
                            "rgba(245, 158, 11, 0.8)",
                            "rgba(139, 92, 246, 0.8)"
                        ],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { min: 0, max: 100, ticks: { stepSize: 20 } }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Error creating subjectChart:", e);
    }

    // 3. Department Performance Comparison
    try {
        const deptCanvas = document.getElementById("deptChart");
        if (deptCanvas) {
            const deptCtx = deptCanvas.getContext("2d");
            if (chartInstances.deptChart) chartInstances.deptChart.destroy();

            const deptLabels = Object.keys(analytics.department_averages || {});
            const deptVals = Object.values(analytics.department_averages || {});

            chartInstances.deptChart = new Chart(deptCtx, {
                type: "bar",
                data: {
                    labels: deptLabels,
                    datasets: [{
                        label: "Dept Average %",
                        data: deptVals,
                        backgroundColor: "rgba(59, 130, 246, 0.75)",
                        borderColor: "#3b82f6",
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: "y",
                    scales: {
                        x: { min: 0, max: 100 }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Error creating deptChart:", e);
    }

    // 4. Academic Standing Distribution
    try {
        const statusCanvas = document.getElementById("statusChart");
        if (statusCanvas) {
            const statusCtx = statusCanvas.getContext("2d");
            if (chartInstances.statusChart) chartInstances.statusChart.destroy();

            const statusLabels = Object.keys(analytics.status_distribution || {});
            const statusCounts = Object.values(analytics.status_distribution || {});

            chartInstances.statusChart = new Chart(statusCtx, {
                type: "polarArea",
                data: {
                    labels: statusLabels,
                    datasets: [{
                        data: statusCounts,
                        backgroundColor: [
                            "rgba(16, 185, 129, 0.75)", // Distinction
                            "rgba(59, 130, 246, 0.75)",  // Good Standing
                            "rgba(239, 68, 68, 0.75)"    // Needs Improvement
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Error creating statusChart:", e);
    }
}

/**
 * Render rows in student records table
 */
function renderTable(students) {
    const tbody = document.getElementById("studentTableBody");
    const countInfo = document.getElementById("recordCountInfo");

    if (!students || students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="14" class="text-center py-4" style="color:#64748b;">No student records found matching criteria.</td></tr>`;
        countInfo.textContent = `Showing 0 of ${allStudents.length} students`;
        return;
    }

    countInfo.textContent = `Showing ${students.length} of ${allStudents.length} students`;

    let html = "";
    students.forEach(s => {
        const gradeClass = getGradeClass(s.grade);
        const statusClass = getStatusClass(s.status);
        const statusIcon = s.status === "Needs Improvement" 
            ? '<i class="fa-solid fa-triangle-exclamation"></i>' 
            : (s.status === "Distinction" ? '<i class="fa-solid fa-star"></i>' : '<i class="fa-solid fa-check"></i>');

        html += `
            <tr>
                <td><strong>${escapeHtml(s.roll_number)}</strong></td>
                <td>
                    <a href="javascript:void(0)" onclick="openDetailModal(${s.id})" style="font-weight:600; color:#1e293b; text-decoration:none;">
                        ${escapeHtml(s.name)}
                    </a>
                </td>
                <td>${escapeHtml(s.department)}</td>
                <td>${s.math_marks}</td>
                <td>${s.science_marks}</td>
                <td>${s.english_marks}</td>
                <td>${s.history_marks}</td>
                <td>${s.cs_marks}</td>
                <td><strong>${s.total_marks}</strong></td>
                <td><strong>${s.percentage}%</strong></td>
                <td>
                    <span style="color:${s.attendance < 75 ? '#dc2626; font-weight:700;' : 'inherit'};">
                        ${s.attendance}%
                    </span>
                </td>
                <td><span class="grade-badge ${gradeClass}">${s.grade}</span></td>
                <td><span class="status-badge ${statusClass}">${statusIcon} ${escapeHtml(s.status)}</span></td>
                <td class="text-center">
                    <div class="row-actions">
                        <button class="action-btn" title="View Report" onclick="openDetailModal(${s.id})">
                            <i class="fa-solid fa-eye"></i>
                        </button>
                        <button class="action-btn" title="Edit Student" onclick="openEditModal(${s.id})">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="action-btn delete-btn" title="Delete Student" onclick="deleteStudent(${s.id}, '${escapeHtml(s.name)}')">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

/**
 * Filter table by search text, department, and status
 */
function filterTable() {
    const searchText = document.getElementById("searchInput").value.toLowerCase().trim();
    const deptFilter = document.getElementById("filterDepartment").value;
    const statusFilter = document.getElementById("filterStatus").value;

    filteredStudents = allStudents.filter(s => {
        const matchesSearch = 
            s.name.toLowerCase().includes(searchText) ||
            s.roll_number.toLowerCase().includes(searchText) ||
            s.department.toLowerCase().includes(searchText);

        const matchesDept = !deptFilter || s.department === deptFilter;
        const matchesStatus = !statusFilter || s.status === statusFilter;

        return matchesSearch && matchesDept && matchesStatus;
    });

    renderTable(filteredStudents);
}

/**
 * Sort table on column click
 */
function sortTable(columnIndex) {
    if (currentSortColumn === columnIndex) {
        sortAscending = !sortAscending;
    } else {
        currentSortColumn = columnIndex;
        sortAscending = true;
    }

    filteredStudents.sort((a, b) => {
        let valA, valB;
        switch(columnIndex) {
            case 0: valA = a.roll_number; valB = b.roll_number; break;
            case 1: valA = a.name.toLowerCase(); valB = b.name.toLowerCase(); break;
            case 8: valA = a.total_marks; valB = b.total_marks; break;
            case 9: valA = a.percentage; valB = b.percentage; break;
            case 10: valA = a.attendance; valB = b.attendance; break;
            default: return 0;
        }

        if (valA < valB) return sortAscending ? -1 : 1;
        if (valA > valB) return sortAscending ? 1 : -1;
        return 0;
    });

    renderTable(filteredStudents);
}

/**
 * Live auto-calculation in modal form
 */
function calcPreview() {
    const math = parseFloat(document.getElementById("mathMarks").value) || 0;
    const sci = parseFloat(document.getElementById("scienceMarks").value) || 0;
    const eng = parseFloat(document.getElementById("englishMarks").value) || 0;
    const hist = parseFloat(document.getElementById("historyMarks").value) || 0;
    const cs = parseFloat(document.getElementById("csMarks").value) || 0;
    const att = parseFloat(document.getElementById("attendance").value) || 0;

    const total = Math.round((math + sci + eng + hist + cs) * 100) / 100;
    const pct = Math.round((total / 500) * 10000) / 100;

    let grade = "F";
    if (pct >= 90) grade = "A+";
    else if (pct >= 80) grade = "A";
    else if (pct >= 70) grade = "B";
    else if (pct >= 60) grade = "C";
    else if (pct >= 50) grade = "D";

    const failedSubject = [math, sci, eng, hist, cs].some(m => m < 40);
    let status = "Good Standing";
    let statusClass = "status-good";
    if (pct < 50 || att < 75 || failedSubject) {
        status = "Needs Improvement";
        statusClass = "status-needs-imp";
    } else if (pct >= 85 && att >= 85) {
        status = "Distinction";
        statusClass = "status-distinction";
    }

    document.getElementById("previewTotal").textContent = `${total} / 500`;
    document.getElementById("previewPercentage").textContent = `${pct.toFixed(1)}%`;
    
    const gradeBadge = document.getElementById("previewGrade");
    gradeBadge.textContent = grade;
    gradeBadge.className = `grade-badge ${getGradeClass(grade)}`;

    const statusBadge = document.getElementById("previewStatus");
    statusBadge.textContent = status;
    statusBadge.className = `status-badge ${statusClass}`;
}

/**
 * Open Add Student Modal
 */
function openAddModal() {
    document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-user-plus"></i> Add New Student';
    document.getElementById("studentForm").reset();
    document.getElementById("studentId").value = "";
    document.getElementById("rollNumber").disabled = false;
    clearModalAlert();

    const saveBtn = document.getElementById("saveStudentBtn");
    saveBtn.disabled = false;
    saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save Student Record';

    calcPreview();
    document.getElementById("studentModal").classList.add("active");
}

/**
 * Open Edit Student Modal
 */
function openEditModal(studentId) {
    const student = allStudents.find(s => s.id === studentId);
    if (!student) return;

    document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-user-pen"></i> Edit Student Record';
    document.getElementById("studentId").value = student.id;
    document.getElementById("rollNumber").value = student.roll_number;
    document.getElementById("rollNumber").disabled = true; // Roll number is unique key
    document.getElementById("studentName").value = student.name;
    document.getElementById("department").value = student.department;
    document.getElementById("semester").value = student.semester;
    document.getElementById("mathMarks").value = student.math_marks;
    document.getElementById("scienceMarks").value = student.science_marks;
    document.getElementById("englishMarks").value = student.english_marks;
    document.getElementById("historyMarks").value = student.history_marks;
    document.getElementById("csMarks").value = student.cs_marks;
    document.getElementById("attendance").value = student.attendance;
    clearModalAlert();

    const saveBtn = document.getElementById("saveStudentBtn");
    saveBtn.disabled = false;
    saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Update Student Record';

    calcPreview();
    document.getElementById("studentModal").classList.add("active");
}

function closeModal() {
    clearModalAlert();
    document.getElementById("studentModal").classList.remove("active");
}

function showModalAlert(message) {
    const box = document.getElementById("modalAlert");
    if (box) {
        box.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> <span>${escapeHtml(message)}</span>`;
        box.style.display = "flex";
    }
}

function clearModalAlert() {
    const box = document.getElementById("modalAlert");
    if (box) {
        box.style.display = "none";
        box.innerHTML = "";
    }
}

/**
 * Handle Add/Edit Form Submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    clearModalAlert();

    const saveBtn = document.getElementById("saveStudentBtn");
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

    const studentId = document.getElementById("studentId").value;
    const isEdit = Boolean(studentId);

    const rollNumber = document.getElementById("rollNumber").value.trim();
    const studentName = document.getElementById("studentName").value.trim();

    if (!rollNumber || !studentName) {
        showModalAlert("Please fill in both Roll Number and Student Name.");
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
        return;
    }

    const payload = {
        roll_number: rollNumber,
        name: studentName,
        department: document.getElementById("department").value,
        semester: parseInt(document.getElementById("semester").value) || 1,
        math_marks: isNaN(parseFloat(document.getElementById("mathMarks").value)) ? 0 : parseFloat(document.getElementById("mathMarks").value),
        science_marks: isNaN(parseFloat(document.getElementById("scienceMarks").value)) ? 0 : parseFloat(document.getElementById("scienceMarks").value),
        english_marks: isNaN(parseFloat(document.getElementById("englishMarks").value)) ? 0 : parseFloat(document.getElementById("englishMarks").value),
        history_marks: isNaN(parseFloat(document.getElementById("historyMarks").value)) ? 0 : parseFloat(document.getElementById("historyMarks").value),
        cs_marks: isNaN(parseFloat(document.getElementById("csMarks").value)) ? 0 : parseFloat(document.getElementById("csMarks").value),
        attendance: isNaN(parseFloat(document.getElementById("attendance").value)) ? 0 : parseFloat(document.getElementById("attendance").value)
    };

    try {
        const url = isEdit ? `/api/students/${studentId}` : "/api/students";
        const method = isEdit ? "PUT" : "POST";

        const res = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        let result;
        try {
            result = await res.json();
        } catch (jsonErr) {
            result = { success: false, error: `Server error (${res.status} ${res.statusText})` };
        }

        if (result.success) {
            closeModal();
            showAlert(result.message || "Student record saved successfully!");
            await loadDashboardData();
        } else {
            const errorMsg = result.error || "Failed to save student record.";
            showModalAlert(errorMsg);
            showAlert(errorMsg, true);
        }
    } catch (err) {
        console.error("Save error:", err);
        const networkError = "Network error connecting to server. Please check your connection.";
        showModalAlert(networkError);
        showAlert(networkError, true);
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    }
}

/**
 * Delete student record
 */
async function deleteStudent(studentId, studentName) {
    if (!confirm(`Are you sure you want to delete the record for ${studentName}?`)) {
        return;
    }

    try {
        const res = await fetch(`/api/students/${studentId}`, { method: "DELETE" });
        const result = await res.json();
        if (result.success) {
            showAlert(`Student ${studentName} removed.`);
            await loadDashboardData();
        } else {
            showAlert(result.error || "Failed to delete student.", true);
        }
    } catch (err) {
        console.error("Delete error:", err);
        showAlert("Server error during deletion.", true);
    }
}

/**
 * Open Detailed Report Card Modal
 */
function openDetailModal(studentId) {
    const student = allStudents.find(s => s.id === studentId);
    if (!student) return;

    const detailBox = document.getElementById("detailContent");
    const isAtRisk = student.status === "Needs Improvement";

    detailBox.innerHTML = `
        <div class="report-card-header">
            <div class="report-student-info">
                <h4>${escapeHtml(student.name)}</h4>
                <p>Roll No: <strong>${escapeHtml(student.roll_number)}</strong> • Department: <strong>${escapeHtml(student.department)}</strong> (Sem ${student.semester})</p>
            </div>
            <div>
                <span class="status-badge ${getStatusClass(student.status)}">${escapeHtml(student.status)}</span>
            </div>
        </div>

        <div class="report-marks-grid">
            <div class="mark-box">
                <span>Mathematics</span>
                <strong>${student.math_marks} / 100</strong>
            </div>
            <div class="mark-box">
                <span>Science</span>
                <strong>${student.science_marks} / 100</strong>
            </div>
            <div class="mark-box">
                <span>English</span>
                <strong>${student.english_marks} / 100</strong>
            </div>
            <div class="mark-box">
                <span>History</span>
                <strong>${student.history_marks} / 100</strong>
            </div>
            <div class="mark-box">
                <span>Computer Science</span>
                <strong>${student.cs_marks} / 100</strong>
            </div>
        </div>

        <div class="report-summary-box">
            <div>
                <span>Total Marks</span>
                <strong>${student.total_marks} / 500</strong>
            </div>
            <div>
                <span>Aggregate Percentage</span>
                <strong>${student.percentage}%</strong>
            </div>
            <div>
                <span>Final Grade</span>
                <strong><span class="grade-badge ${getGradeClass(student.grade)}">${student.grade}</span></strong>
            </div>
            <div>
                <span>Attendance Track</span>
                <strong style="color:${student.attendance < 75 ? '#dc2626' : '#16a34a'};">${student.attendance}%</strong>
            </div>
        </div>

        ${isAtRisk ? `
            <div class="remedial-box">
                <h5><i class="fa-solid fa-triangle-exclamation"></i> Academic Support Recommendation</h5>
                <p>Student is identified as <strong>Needs Improvement</strong> due to ${student.attendance < 75 ? 'low attendance (<75%)' : 'low percentage (<50%) or subject score failure'}. Recommendation: Schedule academic counseling, enroll in peer-tutoring sessions, and notify faculty advisor.</p>
            </div>
        ` : `
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:0.85rem 1rem; color:#166534; font-size:0.82rem;">
                <strong><i class="fa-solid fa-circle-check"></i> Satisfactory Academic Standing:</strong> Student meets and exceeds baseline progression criteria.
            </div>
        `}
    `;

    document.getElementById("detailModal").classList.add("active");
}

function closeDetailModal() {
    document.getElementById("detailModal").classList.remove("active");
}

/**
 * Re-seed default sample data
 */
async function resetDefaultData() {
    if (!confirm("This will re-seed default demo records into the database. Continue?")) {
        return;
    }
    try {
        const res = await fetch("/api/reset-data", { method: "POST" });
        const data = await res.json();
        showAlert(data.message || "Data restored.");
        await loadDashboardData();
    } catch (err) {
        showAlert("Failed to restore default records.", true);
    }
}

/**
 * Toast / Alert Notification (Floating top-right)
 */
function showAlert(message, isError = false) {
    const banner = document.getElementById("alertBanner");
    const msg = document.getElementById("alertMessage");
    msg.textContent = message;
    banner.className = isError ? "alert-banner alert-error" : "alert-banner";
    banner.style.display = "flex";

    setTimeout(() => {
        banner.style.display = "none";
    }, 4500);
}

function hideAlert() {
    document.getElementById("alertBanner").style.display = "none";
}

/**
 * Helper style mappings
 */
function getGradeClass(grade) {
    switch(grade) {
        case "A+": return "grade-aplus";
        case "A": return "grade-a";
        case "B": return "grade-b";
        case "C": return "grade-c";
        case "D": return "grade-d";
        default: return "grade-f";
    }
}

function getStatusClass(status) {
    switch(status) {
        case "Distinction": return "status-distinction";
        case "Needs Improvement": return "status-needs-imp";
        default: return "status-good";
    }
}

function escapeHtml(text) {
    if (!text) return "";
    return text.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
