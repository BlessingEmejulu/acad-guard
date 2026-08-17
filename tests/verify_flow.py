"""
Full End-to-End Verification Script
"""
import io
import sys
import httpx

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

client = httpx.Client(base_url="http://127.0.0.1:8000")

def run_verification():
    print("==================================================")
    print("      ACADGUARD FULL WORKFLOW VERIFICATION        ")
    print("==================================================")

    # 1. HTML Pages
    print("\n--- 1. Testing Frontend HTML Pages ---")
    for path in ["/", "/login", "/register", "/app"]:
        r = client.get(path)
        print(f"GET {path:12}: HTTP {r.status_code} ({len(r.text)} bytes)")
        assert r.status_code == 200

    # 2. Authentication
    print("\n--- 2. Testing Authentication & Roles ---")
    roles = [
        ("student@example.com", "Student@12345", "student"),
        ("supervisor@example.com", "Supervisor@12345", "supervisor"),
        ("admin@example.com", "Admin@12345", "admin")
    ]
    tokens = {}
    for email, pwd, expected_role in roles:
        r = client.post("/api/auth/login", json={"email": email, "password": pwd})
        assert r.status_code == 200
        data = r.json()
        assert data["user"]["role"] == expected_role
        tokens[expected_role] = data["access_token"]
        print(f"Login {expected_role.upper():10}: SUCCESS -> User: {data['user']['full_name']} ({data['user']['email']})")

    # 3. Student Project & Plagiarism Check
    print("\n--- 3. Testing Student Project & NLP Similarity Pipeline ---")
    st_headers = {"Authorization": f"Bearer {tokens['student']}"}
    proj_res = client.post("/api/projects", headers=st_headers, json={
        "title": "Scalable Zero Trust Architecture for Hybrid Cloud Clusters",
        "description": "Implementing zero trust identity verification for container workloads in high-throughput cloud environments.",
        "category": "Cybersecurity",
        "department": "Computer Science",
        "academic_session": "2025/2026",
        "supervisor_id": 1
    })
    assert proj_res.status_code == 201
    p_data = proj_res.json()
    p_id = p_data["id"]
    print(f"Created Project #{p_id}: '{p_data['title']}' (Status: {p_data['status']})")

    # Submit Document containing overlapping phrases from seed corpus
    doc_content = b"Cloud computing infrastructures have become pivotal targets for sophisticated distributed cyber attacks. Traditional signature-based intrusion detection systems struggle to classify polymorphic network traffic anomalies. Our preprocessing pipeline normalizes network flow durations."
    file_tuple = ("zero_trust_research_v1.txt", io.BytesIO(doc_content), "text/plain")
    sub_res = client.post(f"/api/projects/{p_id}/submissions", headers=st_headers, files={"file": file_tuple})
    assert sub_res.status_code == 201
    s_data = sub_res.json()
    print(f"Uploaded Document: '{s_data['original_filename']}' (Version {s_data['version']})")
    print(f"Automated Plagiarism Check: {s_data['similarity_score']}% -> Classification: {s_data['plagiarism_result']}")

    # Get Plagiarism Report
    rep_res = client.get(f"/api/submissions/{s_data['id']}/report", headers=st_headers)
    assert rep_res.status_code == 200
    r_data = rep_res.json()
    print(f"Detailed Report #{r_data['id']}: Matched {r_data['matched_documents_count']} source(s), Processing Time: {r_data['processing_time']}s")
    for idx, match in enumerate(r_data["matches"], 1):
        print(f"   Match {idx}: '{match['matched_project_title']}' by {match['matched_student_name']} -> {match['similarity_score']}%")

    # 4. Supervisor Review Workflow
    print("\n--- 4. Testing Supervisor Review Workflow ---")
    sup_headers = {"Authorization": f"Bearer {tokens['supervisor']}"}
    rev_res = client.put(f"/api/projects/{p_id}/review", headers=sup_headers, json={
        "action": "Revision Required",
        "feedback_text": "Plagiarism check indicates substantial overlap with cloud IDS papers in repository. Please rewrite the abstract and expand literature citations."
    })
    assert rev_res.status_code == 200
    status_updated = rev_res.json()["status"]
    print(f"Supervisor Decision: Status updated to '{status_updated}'")

    # 5. Admin Dashboard & Metrics
    print("\n--- 5. Testing Institutional Administrator Metrics ---")
    adm_headers = {"Authorization": f"Bearer {tokens['admin']}"}
    dash_res = client.get("/api/dashboard/admin", headers=adm_headers)
    assert dash_res.status_code == 200
    adm_data = dash_res.json()
    print(f"Total Users: {adm_data['total_users']} (Students: {adm_data['total_students']}, Supervisors: {adm_data['total_supervisors']})")
    print(f"Total Academic Projects: {adm_data['total_projects']}, Total Submissions: {adm_data['total_submissions']}")
    print(f"Average Institutional Similarity: {adm_data['average_similarity']}%")
    print(f"Status Distribution Breakdown: {adm_data['status_distribution']}")
    print(f"Similarity Ranges Breakdown: {adm_data['similarity_distribution']}")

    # 6. Audit Trail
    audit_res = client.get("/api/admin/audit-logs", headers=adm_headers)
    assert audit_res.status_code == 200
    print(f"Audit Trail: {len(audit_res.json())} security and action events recorded.")

    print("\n==================================================")
    print("   ALL INTEGRATION & WORKFLOW TESTS PASSED 100%   ")
    print("==================================================")

if __name__ == "__main__":
    run_verification()
