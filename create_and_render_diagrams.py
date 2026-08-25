"""
Script to write all Mermaid diagram source files (.mmd) and render them to PNG images using mermaid.ink API.
"""
import os
import base64
import urllib.request
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MMD_DIR = os.path.join(BASE_DIR, "mermaid-diagrams")
PNG_DIR = os.path.join(BASE_DIR, "rendered-diagrams")

os.makedirs(MMD_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

DIAGRAMS = {
    "figure-4-1-system-architecture": """flowchart TD
    subgraph Client_Tier ["Client Tier (Presentation Layer)"]
        UI_Student["Student Interface<br/>(HTML5 / Vanilla JS SPA / Custom CSS)"]
        UI_Supervisor["Supervisor Interface<br/>(Review Queue / Feedback Form)"]
        UI_Admin["Admin Interface<br/>(Chart.js Analytics / System Settings)"]
    end

    subgraph API_Tier ["Application & Service Tier (FastAPI Framework)"]
        ASGI["Uvicorn ASGI Web Server"]
        Router["RESTful API Routers<br/>(Auth, Projects, Submissions, Supervision, Admin)"]
        AuthGuard["Security & Middleware<br/>(PyJWT Bearer Token Guard, Bcrypt Passwords)"]
        Extractor["Document Extractor Service<br/>(PyMuPDF / Python-Docx / UTF-8)"]
        Engine["Plagiarism Detection Engine<br/>(Scikit-Learn TF-IDF, Winnowing Fingerprinter)"]
    end

    subgraph Data_Tier ["Data & Persistence Tier"]
        ORM["SQLAlchemy 2.0 ORM Engine"]
        DB[(SQLite Database<br/>academic_integrity.db)]
        FS["File Storage System<br/>(/uploads directory)"]
    end

    UI_Student -->|HTTP / REST API| ASGI
    UI_Supervisor -->|HTTP / REST API| ASGI
    UI_Admin -->|HTTP / REST API| ASGI

    ASGI --> Router
    Router --> AuthGuard
    Router --> Extractor
    Router --> Engine

    Extractor -->|Save Extracted Text| ORM
    Extractor -->|Store File| FS
    Engine -->|Compute TF-IDF & Fingerprints| ORM
    AuthGuard -->|Verify User & Role| ORM
    ORM -->|ACID Database Queries| DB
""",

    "figure-4-2-main-menu-control-center": """flowchart TD
    Start([User Login]) --> Authenticate{Role Authentication}

    Authenticate -->|Role: Student| StudentMenu["Student Control Center"]
    StudentMenu --> S1["Dashboard Stats & Alerts"]
    StudentMenu --> S2["Project Topic Registration"]
    StudentMenu --> S3["Document Upload (.pdf, .docx, .txt)"]
    StudentMenu --> S4["Interactive Similarity Report"]
    StudentMenu --> S5["Supervisory Feedback History"]

    Authenticate -->|Role: Supervisor| SupervisorMenu["Supervisor Control Center"]
    SupervisorMenu --> V1["Supervision Queue & Stats"]
    SupervisorMenu --> V2["Submission & Similarity Review"]
    SupervisorMenu --> V3["Feedback & Status Assignment<br/>(Approved / Revision / Rejected)"]
    SupervisorMenu --> V4["Assigned Student Roster"]

    Authenticate -->|Role: Administrator| AdminMenu["Institutional Admin Control Center"]
    AdminMenu --> A1["System Analytics (Chart.js Graphs)"]
    AdminMenu --> A2["User CRUD Management"]
    AdminMenu --> A3["Supervisor Allocation Matrix"]
    AdminMenu --> A4["Global Master Explorer"]
    AdminMenu --> A5["Bulk Plagiarism Re-check Engine"]
    AdminMenu --> A6["Audit Log Inspector"]
    AdminMenu --> A7["System Settings Configuration"]
""",

    "figure-4-3-subsystem-structure": """flowchart TD
    AcadGuard["AcadGuard Central System"]

    AcadGuard --> AuthSub["1. Authentication & Security Subsystem"]
    AuthSub --> Auth1["Login & Credential Verification"]
    AuthSub --> Auth2["Bcrypt Password Hashing"]
    AuthSub --> Auth3["PyJWT Token Issuance & Verification"]
    AuthSub --> Auth4["Role-Based Route Guards"]

    AcadGuard --> ProjSub["2. Student & Project Subsystem"]
    ProjSub --> Proj1["Project Registration & Metadata"]
    ProjSub --> Proj2["Versioned Document Upload"]
    ProjSub --> Proj3["Text Extraction Engine"]
    ProjSub --> Proj4["Student Notification Feed"]

    AcadGuard --> SupSub["3. Supervisory Review Subsystem"]
    SupSub --> Sup1["Review Queue Management"]
    SupSub --> Sup2["Plagiarism Report Inspector"]
    SupSub --> Sup3["Timestamped Feedback Logging"]
    SupSub --> Sup4["Project Approval Workflow"]

    AcadGuard --> PlagSub["4. Plagiarism Engine & Admin Subsystem"]
    PlagSub --> Plag1["TF-IDF Vectorizer & Cosine Similarity"]
    PlagSub --> Plag2["Winnowing K-Gram Fingerprinter"]
    PlagSub --> Plag3["Hybrid Score & Overlap Snippet Extractor"]
    PlagSub --> Plag4["Admin Analytics & System Settings"]
""",

    "figure-4-4-database-erd": """erDiagram
    users ||--o| supervisors : "has profile"
    users ||--o{ projects : "owns (student)"
    users ||--o{ submissions : "submits"
    users ||--o{ notifications : "receives"
    users ||--o{ audit_logs : "triggers"

    supervisors ||--o{ projects : "supervises"
    supervisors ||--o{ feedback : "provides"

    projects ||--o{ submissions : "contains"
    projects ||--o{ feedback : "receives"

    submissions ||--o| plagiarism_reports : "generates"
    submissions ||--o{ similarity_matches : "matched_in"

    plagiarism_reports ||--o{ similarity_matches : "contains"

    users {
        int id PK
        string full_name
        string email UK
        string password_hash
        string role
        string department
        string matric_number UK
        boolean is_active
        datetime created_at
    }

    supervisors {
        int id PK
        int user_id FK
        string staff_id UK
        string department
        string specialization
        int max_students
    }

    projects {
        int id PK
        string title
        string category
        string department
        string academic_session
        int student_id FK
        int supervisor_id FK
        string status
    }

    submissions {
        int id PK
        int project_id FK
        int version
        string original_filename
        string file_path
        string file_type
        bigint file_size
        text extracted_text
        int submitted_by FK
        string submission_status
    }

    plagiarism_reports {
        int id PK
        int submission_id FK
        float similarity_score
        string result
        int matched_documents_count
        float processing_time
        int total_words
        string review_status
    }

    similarity_matches {
        int id PK
        int report_id FK
        int matched_submission_id FK
        float similarity_score
        text matched_text
    }

    feedback {
        int id PK
        int project_id FK
        int supervisor_id FK
        text comments
        string status_assigned
        datetime created_at
    }

    audit_logs {
        int id PK
        int user_id FK
        string action
        text description
        string ip_address
        datetime created_at
    }

    settings {
        int id PK
        string key UK
        text value
        text description
    }
""",

    "figure-4-5-uml-class-diagram": """classDiagram
    class User {
        +int id
        +string full_name
        +string email
        +string password_hash
        +string role
        +string department
        +string matric_number
        +boolean is_active
        +datetime created_at
    }

    class Supervisor {
        +int id
        +int user_id
        +string staff_id
        +string department
        +string specialization
        +int max_students
    }

    class Project {
        +int id
        +string title
        +string description
        +string category
        +string department
        +string academic_session
        +int student_id
        +int supervisor_id
        +string status
    }

    class Submission {
        +int id
        +int project_id
        +int version
        +string original_filename
        +string stored_filename
        +string file_path
        +string file_type
        +bigint file_size
        +text extracted_text
        +string submission_status
    }

    class PlagiarismReport {
        +int id
        +int submission_id
        +float similarity_score
        +string result
        +int matched_documents_count
        +float processing_time
        +int total_words
        +int total_unique_words
        +string review_status
    }

    class SimilarityMatch {
        +int id
        +int report_id
        +int matched_submission_id
        +float similarity_score
        +text matched_text
    }

    class PlagiarismEngine {
        +classify_similarity(score: float) string
        +run_check(submission_id: int, db: Session) PlagiarismReport
    }

    class DocumentExtractor {
        +extract_text_from_file(file_path: string, filename: string) Tuple
    }

    User "1" -- "0..1" Supervisor : profile
    User "1" -- "0..*" Project : student_projects
    Supervisor "1" -- "0..*" Project : supervised_projects
    Project "1" -- "0..*" Submission : submissions
    Submission "1" -- "0..1" PlagiarismReport : report
    PlagiarismReport "1" -- "0..*" SimilarityMatch : matches
    PlagiarismEngine ..> Submission : evaluates
    PlagiarismEngine ..> DocumentExtractor : uses
""",

    "figure-4-6-system-flowchart": """flowchart TD
    A([Start: Student Log In]) --> B[Input Email & Password]
    B --> C{Valid Credentials?}
    C -->|No| D[Display Auth Error Alert] --> B
    C -->|Yes| E[Generate JWT & Load Dashboard]
    E --> F[Select Create Project / Upload Draft]
    F --> G[Upload Document File .pdf/.docx/.txt]
    G --> H{File Size <= 25MB & Valid Format?}
    H -->|No| I[Return 400 Validation Error] --> G
    H -->|Yes| J[Save File to /uploads & Create Submission DB Record]
    J --> K[Document Extractor: Parse Raw Text]
    K --> L[Plagiarism Engine Pipeline: TF-IDF & Winnowing Fingerprints]
    L --> M[Compute Hybrid Score & Extract Overlapping Snippets]
    M --> N[Save Plagiarism Report & Trigger Student/Supervisor Notifications]
    N --> O[Supervisor Reviews Submission & Plagiarism Report]
    O --> P{Supervisor Approval Status}
    P -->|Approved| Q[Set Project Status: Approved]
    P -->|Revision Required| R[Set Status: Revision Required & Log Comments]
    P -->|Rejected| S[Set Status: Rejected]
    Q --> T([End Workflow])
    R --> T
    S --> T
""",

    "figure-4-7-authentication-flowchart": """flowchart TD
    A([Client HTTP Request]) --> B[Extract Authorization Header]
    B --> C{Bearer Token Present?}
    C -->|No| D[Return 401 Unauthorized Response]
    C -->|Yes| E[Decode PyJWT Token with Secret Key]
    E --> F{Token Valid & Not Expired?}
    F -->|No| D
    F -->|Yes| G[Extract User ID & Query Database User]
    G --> H{User Exists & is_active == True?}
    H -->|No| D
    H -->|Yes| I{Check Endpoint Role Requirements}
    I -->|Failed Role Match| J[Return 403 Forbidden Response]
    I -->|Passed Role Match| K[Inject User into FastAPI Dependency Context]
    K --> L([Execute Endpoint Route Handler])
""",

    "figure-4-8-algorithm-flowchart": """flowchart TD
    A([Input: Target Submission ID]) --> B[Query Target Submission & Extract Raw Text]
    B --> C[Clean & Normalize Text: Lowercase, Strip Punctuation]
    C --> D[Tokenize Words & Remove Academic Stopwords]
    D --> E[Query Database Corpus Submissions]
    E --> F{Corpus Submissions Exist?}
    F -->|No| G[Set Score = 0.0, Result = Original] --> M
    F -->|Yes| H[Compute Unigram/Bigram TF-IDF Vectors & Cosine Similarities]
    H --> I[Generate Winnowing K-Gram Fingerprints k=5, w=4]
    I --> J[Compute Jaccard Fingerprint Overlap Coefficient]
    J --> K[Calculate Weighted Hybrid Similarity Score]
    K --> L[Extract Overlapping Sentence Snippets]
    L --> M[Classify Result: Original, Low, Needs Review, Potential Plagiarism]
    M --> N[Persist PlagiarismReport & SimilarityMatch Records in DB]
    N --> O([Return Generated Plagiarism Report])
""",

    "figure-4-9-control-structure-diagram": """flowchart TD
    A([Compute TF-IDF Score S_tfidf & Jaccard Score S_jaccard]) --> B{S_jaccard > 0.60?}
    
    B -->|True: Verbatim Copy Priority| C["Hybrid Score = (0.35 * S_tfidf) + (0.65 * S_jaccard)"]
    B -->|False: Conceptual Priority| D["Hybrid Score = (0.70 * S_tfidf) + (0.30 * S_jaccard)"]
    
    C --> E["Scale Score to Percentage (0.0 - 100.0%)"]
    D --> E
    
    E --> F{Has Multiple Matching Corpus Docs?}
    F -->|Yes| G["Aggregate Score = min(100.0, Top_Score + 0.10 * Sum(Secondary_Scores))"]
    F -->|No| H["Overall Score = Top_Score"]
    
    G --> I{Overall Similarity Score Category}
    H --> I
    
    I -->|0.0% to 19.9%| J["Category: Original"]
    I -->|20.0% to 39.9%| K["Category: Low Similarity"]
    I -->|40.0% to 59.9%| L["Category: Needs Review"]
    I -->|60.0% to 100.0%| M["Category: Potential Plagiarism"]
""",

    "figure-4-10-user-system-interaction": """sequenceDiagram
    autonumber
    actor Student
    participant Frontend as Vanilla JS SPA
    participant API as FastAPI Backend
    participant Extractor as Document Extractor
    participant Engine as Plagiarism Engine
    participant DB as SQLite Database
    actor Supervisor

    Student->>Frontend: Select File & Submit Project Draft
    Frontend->>API: POST /api/projects/{id}/submissions (Multipart Form)
    API->>DB: Save Submission Record (Status: Processing)
    API->>Extractor: extract_text_from_file(file_path)
    Extractor-->>API: Extracted Text String
    API->>Engine: run_check(submission_id, db)
    Engine->>DB: Query Database Corpus Submissions
    DB-->>Engine: Return Corpus Documents
    Engine->>Engine: Calculate TF-IDF Cosine & Winnowing Fingerprints
    Engine->>DB: Persist PlagiarismReport & SimilarityMatch
    Engine->>DB: Insert Student & Supervisor Notifications
    Engine-->>API: Return PlagiarismReport Object
    API-->>Frontend: 201 Created (Submission & Report JSON)
    Frontend-->>Student: Render Circular Meter & Report View
    
    Supervisor->>Frontend: Open Supervision Queue
    Frontend->>API: GET /api/supervision/submissions
    API-->>Frontend: Return Pending Submissions List
    Supervisor->>Frontend: Inspect Draft & Plagiarism Score
    Supervisor->>Frontend: Submit Review (Status: Approved, Feedback text)
    Frontend->>API: POST /api/supervision/projects/{id}/feedback
    API->>DB: Insert Feedback & Update Project Status (Approved)
    API-->>Frontend: 200 OK Response
    Frontend-->>Supervisor: Toast Notification "Review Submitted"
"""
}

def render_mermaid(name, content):
    mmd_path = os.path.join(MMD_DIR, f"{name}.mmd")
    png_path = os.path.join(PNG_DIR, f"{name}.png")
    
    # Save .mmd file
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {mmd_path}")

    # Render to PNG via mermaid.ink
    try:
        graphbytes = content.encode("utf-8")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("utf-8")
        url = f"https://mermaid.ink/img/{base64_string}"
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            img_data = response.read()
            with open(png_path, "wb") as f_img:
                f_img.write(img_data)
        print(f"Rendered PNG ({len(img_data)} bytes): {png_path}")
    except Exception as e:
        print(f"Error rendering {name}: {e}")

if __name__ == "__main__":
    for name, content in DIAGRAMS.items():
        render_mermaid(name, content)
        time.sleep(1)
