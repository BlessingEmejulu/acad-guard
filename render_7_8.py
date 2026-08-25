"""
Render figure-4-7 and figure-4-8 using urlsafe_b64encode.
"""
import os
import base64
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MMD_DIR = os.path.join(BASE_DIR, "mermaid-diagrams")
PNG_DIR = os.path.join(BASE_DIR, "rendered-diagrams")

DIAGRAMS = {
    "figure-4-7-authentication-flowchart": """graph TD
    A[Client HTTP Request] --> B[Extract Bearer Token]
    B --> C{Token Present?}
    C -->|No| D[401 Unauthorized]
    C -->|Yes| E[Verify PyJWT Token]
    E --> F{Token Valid?}
    F -->|No| D
    F -->|Yes| G[Fetch User from DB]
    G --> H{User Active?}
    H -->|No| D
    H -->|Yes| I{Check Role Requirement}
    I -->|No| J[403 Forbidden]
    I -->|Yes| K[Inject Security Context]
    K --> L[Execute API Route]
""",

    "figure-4-8-algorithm-flowchart": """graph TD
    A[Target Submission ID] --> B[Extract Document Text]
    B --> C[Clean and Normalize Text]
    C --> D[Tokenize and Remove Stopwords]
    D --> E[Query Database Corpus]
    E --> F{Corpus Empty?}
    F -->|Yes| G[Score 0.0 Result Original]
    F -->|No| H[Compute TF-IDF Cosine Similarities]
    H --> I[Generate Winnowing Fingerprints]
    I --> J[Compute Jaccard Overlap]
    J --> K[Calculate Hybrid Similarity Score]
    K --> L[Extract Overlapping Snippets]
    L --> M[Classify Integrity Category]
    M --> N[Save Plagiarism Report in DB]
    N --> O[Return Report JSON]
"""
}

for name, content in DIAGRAMS.items():
    mmd_path = os.path.join(MMD_DIR, f"{name}.mmd")
    png_path = os.path.join(PNG_DIR, f"{name}.png")
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    b64 = base64.urlsafe_b64encode(content.encode("utf-8")).decode("utf-8")
    url = f"https://mermaid.ink/img/{b64}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = res.read()
        with open(png_path, "wb") as f_img:
            f_img.write(data)
        print(f"SUCCESS: Rendered {name}.png ({len(data)} bytes)")
