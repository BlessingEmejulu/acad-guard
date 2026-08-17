# AcadGuard - Project Management Database System for Plagiarism Detection and Academic Integrity

**AcadGuard** is a full-stack, centralized academic project management and automated plagiarism detection platform built for universities and higher institutions. The system empowers students to submit and track research projects, faculty supervisors to review submissions and provide guided feedback, and academic administrators to oversee institutional records, supervisor allocation, and academic integrity policies.

---

## Key Features

### 1. Student Portal
- **Dashboard & Project Tracking**: Live statistics tracking total projects, submissions under review, supervisor approvals, and revision alerts.
- **Academic Project Creation**: Register research topics with title, abstract, department, session, and category.
- **Versioned Document Submission**: Drag-and-drop file upload supporting `.pdf`, `.docx`, and `.txt` files (up to 25MB).
- **Automated Similarity Analysis**: Immediate background execution of the plagiarism detection engine upon upload.
- **Interactive Similarity Reports**: High-precision circular similarity meter, matched source breakdown, and highlighted matching sentence snippets.
- **Supervisor Feedback Stream**: View chronological supervisory comments, critique, and revision requests.

### 2. Supervisor Portal
- **Supervision Dashboard**: Real-time review queue with pending student submissions and approval statistics.
- **Project Review Workflow**: Inspect student drafts, review detailed plagiarism reports, and assign status (`Approved`, `Revision Required`, `Rejected`).
- **Comprehensive Feedback**: Add timestamped critique, literature suggestions, and corrections directly to project submissions.
- **Assigned Student Roster**: Monitor active research progress and student workloads.
- **Document Repository**: Download submitted student documents securely.

### 3. Institutional Administrator Portal
- **System Metrics & Visualizations**: Interactive Chart.js graphs displaying project status distribution, plagiarism similarity ranges, and departmental submission volumes.
- **User Management**: Full CRUD interface for students, faculty supervisors, and administrators with active status toggles.
- **Supervisor Allocation Matrix**: Monitor supervisor student loads and assign/re-assign supervisors to projects.
- **Master Project & Submission Explorer**: Global searchable repository of all student research.
- **Bulk Plagiarism Re-check Engine**: Re-calculate similarity vectors across the entire database corpus on demand.
- **Audit Logging**: Immutable security and administrative action audit trail with IP tracking.
- **Dynamic Institutional Settings**: Adjust upload size limits, active sessions, and similarity warning thresholds.

---

## Plagiarism Detection Architecture

AcadGuard implements an authentic multi-stage Natural Language Processing (NLP) pipeline:

```
[Uploaded Document (.pdf, .docx, .txt)]
               │
               ▼
[Safe Text Extraction (PyMuPDF / python-docx / UTF-8)]
               │
               ▼
[Text Normalization (Lowercasing, Punctuation Stripping, Whitespace Collapse)]
               │
               ▼
[Tokenization & Academic Stop-Word Removal]
               │
               ├────────────────────────────────────────┐
               ▼                                        ▼
[TF-IDF Vectorization & Cosine Similarity]   [Winnowing K-Gram Fingerprinting]
               │                                        │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
          [Hybrid Similarity Score Calculation (0.0 - 100.0%)]
                                   │
                                   ▼
 [Classification: Original (0-19%), Low (20-39%), Needs Review (40-59%), Potential Plagiarism (60-100%)]
                                   │
                                   ▼
    [Overlapping Phrase Extraction & Interactive Report Generation]
```

---

## Pre-Seeded Demo Accounts

For instant local testing and evaluation, the database is pre-seeded with sample accounts:

| Role | Name | Email Address | Password |
| :--- | :--- | :--- | :--- |
| **Administrator** | System Administrator | `admin@example.com` | `Admin@12345` |
| **Supervisor** | Prof. Ike Mgbeafulike | `supervisor@example.com` | `Supervisor@12345` |
| **Student** | Demo Student | `student@example.com` | `Student@12345` |

---

## Technology Stack

- **Backend**: Python 3.12+, FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic V2, SQLite
- **Security**: JWT (PyJWT), Bcrypt password hashing, Role-Based Route Guards
- **NLP & Similarity**: Scikit-Learn (TF-IDF Vectorizer, Cosine Similarity), Winnowing K-Gram Fingerprinting, PyMuPDF, Python-Docx
- **Frontend**: Responsive Component-Based Vanilla JavaScript (ES6+), Modern Custom CSS (Light Theme), Lucide Icons, Chart.js

---

## Installation & Quickstart

### 1. Clone & Install Dependencies
```bash
cd "acad-guard"
pip install -r requirements.txt
```

### 2. Initialize & Seed Database
```bash
python -m app.seed
```

### 3. Run Application Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open your browser and navigate to **`http://localhost:8000`**.

---

## Automated Testing

Run the comprehensive pytest suite covering authentication, extraction, similarity calculations, and API workflows:
```bash
pytest -v
```

---

## API Documentation

Once the server is running, explore the interactive Swagger documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc UI**: `http://localhost:8000/redoc`
