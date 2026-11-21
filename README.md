# Student Performance Analytics Dashboard (SPAD)
### Cloud-Based DevOps Application • Python Flask, Docker, CI/CD & Render Cloud

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Cloud](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)](https://render.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. Project Overview & Problem Statement

### Problem Statement
Educational institutions often face difficulties in tracking student academic performance, attendance, and identifying students who require academic support. This project provides a centralized web-based analytics dashboard that manages student records, calculates performance metrics, visualizes academic results, and identifies students needing improvement through an easy-to-use interface.

### Project Title
**Student Performance Analytics Dashboard – Cloud-Based DevOps Application**

---

## 🚀 2. Key Features

- **Executive KPI Dashboard:** Real-time visibility into total enrollment, class average percentage, overall pass rate, average attendance, and top performer.
- **Academic At-Risk Detection:** Automatically flags students with low attendance (<75%), failing aggregate marks (<50%), or individual subject failures with proactive remedial intervention alerts.
- **Dynamic Chart.js Visualizations:**
  - Grade Distribution Breakdown (A+, A, B, C, D, Fail)
  - Subject-Wise Average Benchmark (Math, Science, English, History, Computer Science)
  - Cross-Department Performance Comparisons
  - Academic Standing & Support Tier Polar Analytics
- **Live Calculation Engine:** Computes total marks, percentage, grade, and academic standing instantly in the frontend modal as marks are entered.
- **Full CRUD Management:** Create, view, update, and delete student records with relational SQLite storage.
- **Data Export:** Instant one-click CSV export of all student academic data.
- **Cloud-Native & Production-Ready:** Containerized with Docker, automated through GitHub Actions CI/CD, and deployed to Render Cloud.

---

## 🛠️ 3. Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) | Modern responsive interface, CSS variables, modal dialogs |
| **Data Visualization** | Chart.js 4.x & FontAwesome 6 | Interactive doughnut, bar, and polar area charts |
| **Backend Framework** | Python 3.11, Flask 3.0.2 | RESTful API endpoints and template rendering |
| **WSGI Server** | Gunicorn 21.2 | Multi-worker production HTTP server |
| **Database** | SQLite 3 | Embedded relational database with default seeding |
| **Testing** | PyTest 8.0 | Automated unit and integration test suite |
| **Containerization** | Docker (python:3.11-slim) | Container image with automated health check |
| **Version Control** | Git & GitHub | Trunk-based version control repository |
| **CI/CD Automation** | GitHub Actions | Automated linting, test suite execution, and Docker build verification |
| **Cloud Hosting** | Render Cloud Platform | Fully managed Web Service with auto-deploy and HTTPS |

---

## 🏗️ 4. Project Architecture

```text
                  +-----------------------------------+
                  |        End User / Faculty         |
                  +-----------------------------------+
                                    |
                                    v [HTTPS Request]
                  +-----------------------------------+
                  |     Modern Web Browser Client     |
                  |   HTML5 + Responsive CSS + JS     |
                  |     Interactive Chart.js          |
                  +-----------------------------------+
                                    |
                                    v [REST API / JSON]
                  +-----------------------------------+
                  |     Gunicorn WSGI / Flask Web     |
                  |         (Python Backend)          |
                  +-----------------------------------+
                        |                       |
                        v                       v
            +-----------------------+   +-------------------+
            |    Analytics Engine   |   |   SQLite Database |
            | (% / Grade / At-Risk) |   |    (students.db)  |
            +-----------------------+   +-------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |         Docker Container          |
                  |      python:3.11-slim Base        |
                  +-----------------------------------+
                                    |
                                    v [git push]
                  +-----------------------------------+
                  |         GitHub Repository         |
                  +-----------------------------------+
                                    |
                                    v [Automated Trigger]
                  +-----------------------------------+
                  |      GitHub Actions CI/CD         |
                  |  Lint -> PyTest -> Docker Build   |
                  +-----------------------------------+
                                    |
                                    v [Webhook / Auto Deploy]
                  +-----------------------------------+
                  |      Render Cloud Platform        |
                  |    Production Web Application     |
                  +-----------------------------------+
```

An interactive vector diagram is available in [`architecture/architecture_diagram.svg`](architecture/architecture_diagram.svg). To view the architecture interactively, open [`architecture/view_architecture.html`](architecture/view_architecture.html) in your browser.

---

## 📁 5. Repository Structure

```text
student-performance-analytics/
│
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions CI/CD Pipeline
│
├── architecture/
│   ├── architecture_diagram.svg # Architecture diagram vector
│   └── view_architecture.html  # Interactive architecture viewer
│
├── data/
│   ├── database.py             # SQLite CRUD operations & metrics logic
│   └── students.db             # Relational SQLite database
│
├── static/
│   ├── style.css               # Modern responsive stylesheet
│   └── script.js               # Dashboard charts & API interactivity
│
├── templates/
│   └── index.html              # Dashboard user interface
│
├── tests/
│   └── test_app.py             # PyTest automated unit test suite
│
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git tracking exclusions
├── Dockerfile                  # Container build instructions
├── pytest.ini                  # PyTest configuration
├── README.md                   # Complete documentation
├── render.yaml                 # Render Infrastructure-as-Code blueprint
└── requirements.txt            # Python dependencies
```

---

## 💻 6. Local Setup and Execution

### Prerequisites
- Python 3.11+
- Git

### Step-by-Step Run:
```bash
# 1. Clone repository
git clone https://github.com/AtulChaudharyy/student-performance-analytics-dashboard.git
cd student-performance-analytics-dashboard

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run automated unit tests
pytest -v

# 6. Start development server
python app.py
```
Open your browser at: `http://localhost:5000`

---

## 🐳 7. Docker Containerization

To run the application inside a container:

```bash
# 1. Build Docker image
docker build -t student-dashboard .

# 2. Run Docker container
docker run -d -p 5000:5000 --name student-app student-dashboard

# 3. Check container logs
docker logs -f student-app

# 4. Access application
# Open http://localhost:5000
```

To stop the container:
```bash
docker stop student-app && docker rm student-app
```

---

## 🔄 8. CI/CD Pipeline (GitHub Actions)

The workflow `.github/workflows/deploy.yml` triggers automatically on every push or pull request to the `main` branch.

### Automated Stages:
1. **Repository Checkout:** Clones latest commit.
2. **Python Setup:** Prepares Python 3.11 runtime environment.
3. **Dependency Installation:** Upgrades pip and installs packages from `requirements.txt`.
4. **Syntax Check:** Verifies python syntax across modules.
5. **Automated Testing:** Runs `pytest -v` across all unit and API tests.
6. **Docker Build:** Builds container image to guarantee container compatibility.
7. **Container Boot & Health Check:** Spins up the container and probes `GET /health`.
8. **Cloud Deployment:** Dispatches deployment to Render Cloud.

---

## ☁️ 9. Deployment to Render Cloud

### One-Click Blueprint Method:
1. Create a free account on [Render](https://render.com).
2. Connect your GitHub account.
3. Click **New +** -> **Blueprint**.
4. Select your `student-performance-analytics` repository.
5. Render detects `render.yaml` automatically and configures the web service.
6. Click **Apply**. Render builds the Docker image and publishes your live URL!

### Alternative Manual Web Service Method:
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Select **Docker** as the Environment.
4. Set Name: `student-performance-analytics`.
5. Click **Create Web Service**.
6. Deployment URL will be generated: `https://student-performance-analytics-xxxx.onrender.com`.

---

## 📋 10. Operational Runbook & Verification

### Health Probe Verification
Verify the service status and database connectivity:
```bash
curl -f https://<your-service-name>.onrender.com/health
```
Expected JSON Response:
```json
{
  "status": "healthy",
  "service": "Student Performance Analytics Dashboard",
  "version": "1.0.0",
  "database": "connected",
  "students_recorded": 12,
  "timestamp": "2026-11-21T15:46:14Z"
}
```

### Automated PyTest Verification
Run the 12 automated unit and integration tests locally or in CI:
```bash
pytest -v
```

### Docker Diagnostics
Inspect running container status and logs:
```bash
docker ps
docker logs --tail 50 -f student-app
```

---

## 📄 License
This project is licensed under the MIT License - open-source software.
