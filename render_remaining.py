"""
Refined diagram script to render the remaining 4 diagrams cleanly.
"""
import os
import base64
import urllib.request
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MMD_DIR = os.path.join(BASE_DIR, "mermaid-diagrams")
PNG_DIR = os.path.join(BASE_DIR, "rendered-diagrams")

REFINED_DIAGRAMS = {
    "figure-4-1-system-architecture": """flowchart TD
    subgraph Client ["Client Tier (Presentation Layer)"]
        A1["Student Interface (Vanilla JS SPA / CSS3)"]
        A2["Supervisor Interface (Queue / Review)"]
        A3["Admin Interface (Chart.js / Analytics)"]
    end

    subgraph App ["Application Tier (FastAPI Framework)"]
        B1["Uvicorn ASGI Web Server"]
        B2["REST Routers (Auth, Projects, Submissions, Admin)"]
        B3["Security Guards (PyJWT Bearer Token, Bcrypt)"]
        B4["Document Extractor (PyMuPDF / Python-Docx)"]
        B5["Plagiarism Engine (TF-IDF & Winnowing)"]
    end

    subgraph Data ["Data & Storage Tier"]
        C1["SQLAlchemy 2.0 ORM Engine"]
        C2[("SQLite Database (academic_integrity.db)")]
        C3["File Storage (/uploads directory)"]
    end

    Client -->|HTTP REST Requests| App
    App -->|ORM Queries| Data
""",

    "figure-4-4-database-erd": """erDiagram
    users ||--o| supervisors : "has profile"
    users ||--o{ projects : "owns"
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
    }

    audit_logs {
        int id PK
        int user_id FK
        string action
        text description
        string ip_address
    }

    settings {
        int id PK
        string key UK
        text value
        text description
    }
""",

    "figure-4-7-authentication-flowchart": """flowchart TD
    A([Client HTTP Request]) --> B[Extract Authorization Header]
    B --> C{Bearer Token Present?}
    C -->|No| D[Return 401 Unauthorized]
    C -->|Yes| E[Decode PyJWT Token with Secret Key]
    E --> F{Token Valid and Not Expired?}
    F -->|No| D
    F -->|Yes| G[Extract User ID and Query DB User]
    G --> H{User Exists and Active?}
    H -->|No| D
    H -->|Yes| I{Check Endpoint Role Requirements}
    I -->|Failed Role Check| J[Return 403 Forbidden]
    I -->|Passed Role Check| K[Inject User into FastAPI Context]
    K --> L([Execute Endpoint Route Handler])
""",

    "figure-4-8-algorithm-flowchart": """flowchart TD
    A([Input: Target Submission ID]) --> B[Query Target Submission and Extract Raw Text]
    B --> C[Clean and Normalize Text: Lowercase and Strip Punctuation]
    C --> D[Tokenize Words and Remove Academic Stopwords]
    D --> E[Query Database Corpus Submissions]
    E --> F{Corpus Submissions Exist?}
    F -->|No| G[Set Score 0.0 Result Original] --> M
    F -->|Yes| H[Compute Unigram and Bigram TF-IDF Cosine Similarities]
    H --> I[Generate Winnowing K-Gram Fingerprints k=5 w=4]
    I --> J[Compute Jaccard Fingerprint Overlap Coefficient]
    J --> K[Calculate Weighted Hybrid Similarity Score]
    K --> L[Extract Overlapping Sentence Snippets]
    L --> M[Classify Result Category]
    M --> N[Persist PlagiarismReport and SimilarityMatch Records in DB]
    N --> O([Return Generated Plagiarism Report])
"""
}

def render_diagram(name, content):
    mmd_path = os.path.join(MMD_DIR, f"{name}.mmd")
    png_path = os.path.join(PNG_DIR, f"{name}.png")
    
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(content)
        
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
        print(f"SUCCESS: Rendered {name}.png ({len(img_data)} bytes)")
    except Exception as e:
        print(f"ERROR rendering {name}: {e}")

if __name__ == "__main__":
    for name, content in REFINED_DIAGRAMS.items():
        render_diagram(name, content)
        time.sleep(1)
