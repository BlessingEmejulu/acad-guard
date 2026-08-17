"""
Integration tests for AcadGuard API endpoints.
"""
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_demo_admin():
    response = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@12345"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

def test_login_demo_student():
    response = client.post("/api/auth/login", json={
        "email": "student@example.com",
        "password": "Student@12345"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "student"

def test_student_project_submission_flow():
    # 1. Login as student
    login_res = client.post("/api/auth/login", json={
        "email": "student@example.com",
        "password": "Student@12345"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create project
    proj_res = client.post("/api/projects", headers=headers, json={
        "title": "Autonomous Drone Fleet Coordination Using Reinforcement Learning",
        "description": "Multi-agent reinforcement learning for UAV collision avoidance.",
        "category": "Artificial Intelligence",
        "department": "Computer Science",
        "academic_session": "2025/2026"
    })
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 3. Submit Document
    file_content = b"This academic research proposes a Q-learning policy for multi-agent autonomous drone swarm navigation in obstacle-dense urban canyons."
    file_tuple = ("uav_thesis.txt", io.BytesIO(file_content), "text/plain")

    sub_res = client.post(
        f"/api/projects/{project_id}/submissions",
        headers=headers,
        files={"file": file_tuple}
    )
    assert sub_res.status_code == 201
    sub_data = sub_res.json()
    assert sub_data["version"] == 1
    assert sub_data["similarity_score"] is not None
    assert sub_data["plagiarism_result"] in ["Original", "Low Similarity", "Needs Review", "Potential Plagiarism"]

    # 4. Check Plagiarism Report
    report_res = client.get(f"/api/submissions/{sub_data['id']}/report", headers=headers)
    assert report_res.status_code == 200
    report_data = report_res.json()
    assert report_data["project_title"] == "Autonomous Drone Fleet Coordination Using Reinforcement Learning"

def test_admin_dashboard_stats():
    login_res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "Admin@12345"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_res = client.get("/api/dashboard/admin", headers=headers)
    assert dash_res.status_code == 200
    stats = dash_res.json()
    assert stats["total_students"] >= 1
    assert stats["total_supervisors"] >= 1
    assert "status_distribution" in stats
    assert "similarity_distribution" in stats
