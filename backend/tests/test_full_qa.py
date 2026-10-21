import io
import pytest
from app.models.user import UserRole
from app.models.complaint import ComplaintStatusEnum, PriorityEnum
from app.models.category import Category
from app.models.location import Campus, Building, Floor, Room
from app.models.sla_config import SLAConfig
from app.services.auth_service import register_user
from app.schemas.user import UserCreate

@pytest.fixture
def setup_seed(db_session):
    campus = Campus(name="Main Campus", code="MC")
    db_session.add(campus)
    db_session.flush()

    building = Building(campus_id=campus.id, name="Science Block", code="SB")
    db_session.add(building)
    db_session.flush()

    floor = Floor(building_id=building.id, floor_number=2, name="Second Floor")
    db_session.add(floor)
    db_session.flush()

    room = Room(floor_id=floor.id, room_number="204", room_type="Lab")
    db_session.add(room)
    db_session.flush()

    cat_hvac = Category(name="HVAC & Electrical", description="AC, Fans, Lights", default_priority="HIGH")
    cat_plumb = Category(name="Plumbing", description="Pipes & Faucets", default_priority="MEDIUM")
    db_session.add_all([cat_hvac, cat_plumb])

    sla_low = SLAConfig(priority="LOW", resolution_time_hours=72)
    sla_med = SLAConfig(priority="MEDIUM", resolution_time_hours=48)
    sla_high = SLAConfig(priority="HIGH", resolution_time_hours=24)
    sla_crit = SLAConfig(priority="CRITICAL", resolution_time_hours=4)
    db_session.add_all([sla_low, sla_med, sla_high, sla_crit])

    db_session.commit()

    return {
        "room_id": room.id,
        "cat_hvac_id": cat_hvac.id,
        "cat_plumb_id": cat_plumb.id
    }

def test_auth_edge_cases(client):
    # 1. Duplicate Registration
    r1 = client.post("/api/v1/auth/register", json={
        "email": "user1@campusflow.edu", "full_name": "User One", "password": "Password123!"
    })
    assert r1.status_code == 201
    assert r1.json()["role"] == "STUDENT"

    r1_dup = client.post("/api/v1/auth/register", json={
        "email": "user1@campusflow.edu", "full_name": "User One Dup", "password": "Password123!"
    })
    assert r1_dup.status_code == 400

    # 2. Login with non-existent user
    r_no_user = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@campusflow.edu", "password": "Password123!"
    })
    assert r_no_user.status_code == 401

    # 3. Refresh Token Flow
    login_res = client.post("/api/v1/auth/login", json={
        "email": "user1@campusflow.edu", "password": "Password123!"
    }).json()
    
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": login_res["refresh_token"]})
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()

    # 4. Invalid Refresh Token
    bad_ref = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.jwt.token"})
    assert bad_ref.status_code == 401

def test_full_complaint_lifecycle_and_rbac(client, db_session, setup_seed):
    # Register Student A, Student B via public API
    client.post("/api/v1/auth/register", json={"email": "student_a@campusflow.edu", "full_name": "Student A", "password": "Password123!"})
    client.post("/api/v1/auth/register", json={"email": "student_b@campusflow.edu", "full_name": "Student B", "password": "Password123!"})
    
    # Staff & Admin registered via admin DB helper
    register_user(db_session, UserCreate(email="staff_maint@campusflow.edu", full_name="Staff Worker", password="Password123!", role=UserRole.STAFF))
    register_user(db_session, UserCreate(email="admin_flow@campusflow.edu", full_name="Admin Flow", password="Password123!", role=UserRole.ADMIN))

    t_stud_a = client.post("/api/v1/auth/login", json={"email": "student_a@campusflow.edu", "password": "Password123!"}).json()["access_token"]
    t_stud_b = client.post("/api/v1/auth/login", json={"email": "student_b@campusflow.edu", "password": "Password123!"}).json()["access_token"]
    t_staff = client.post("/api/v1/auth/login", json={"email": "staff_maint@campusflow.edu", "password": "Password123!"}).json()["access_token"]
    t_admin = client.post("/api/v1/auth/login", json={"email": "admin_flow@campusflow.edu", "password": "Password123!"}).json()["access_token"]

    staff_user = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {t_staff}"}).json()
    staff_id = staff_user["id"]

    # Step 1: Student A creates complaint
    create_res = client.post("/api/v1/complaints", headers={"Authorization": f"Bearer {t_stud_a}"}, json={
        "title": "Air Conditioner Leaking",
        "description": "AC unit in Lab 204 is leaking water heavily onto desks.",
        "category_id": setup_seed["cat_hvac_id"],
        "location_id": setup_seed["room_id"],
        "priority": "HIGH"
    })
    assert create_res.status_code == 201
    complaint = create_res.json()
    c_id = complaint["id"]
    assert complaint["status"] == "OPEN"

    # Step 2: IDOR test - Student B cannot view Student A's complaint
    idor_get = client.get(f"/api/v1/complaints/{c_id}", headers={"Authorization": f"Bearer {t_stud_b}"})
    assert idor_get.status_code == 403

    # Step 3: Admin assigns complaint to Staff
    assign_res = client.post(f"/api/v1/complaints/{c_id}/assign", headers={"Authorization": f"Bearer {t_admin}"}, json={
        "staff_id": staff_id,
        "notes": "Please inspect immediately."
    })
    assert assign_res.status_code == 200
    assert assign_res.json()["status"] == "ASSIGNED"

    # Step 4: Staff moves status to IN_PROGRESS
    in_prog_res = client.patch(f"/api/v1/complaints/{c_id}/status", headers={"Authorization": f"Bearer {t_staff}"}, json={
        "target_status": "IN_PROGRESS",
        "comment": "Parts ordered, work started."
    })
    assert in_prog_res.status_code == 200
    assert in_prog_res.json()["status"] == "IN_PROGRESS"

    # Step 5: Staff adds a comment
    comment_res = client.post(f"/api/v1/complaints/{c_id}/comments", headers={"Authorization": f"Bearer {t_staff}"}, json={
        "content": "Replaced the drainage pipe gasket.",
        "is_internal": False
    })
    assert comment_res.status_code == 201

    # Step 6: Staff moves status to RESOLVED
    resolve_res = client.patch(f"/api/v1/complaints/{c_id}/status", headers={"Authorization": f"Bearer {t_staff}"}, json={
        "target_status": "RESOLVED",
        "resolution_notes": "AC unit fixed and tested for 30 minutes without leakage."
    })
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # Step 7: Student A closes complaint
    close_res = client.patch(f"/api/v1/complaints/{c_id}/status", headers={"Authorization": f"Bearer {t_stud_a}"}, json={
        "target_status": "CLOSED",
        "comment": "Confirmed fixed. Thank you!"
    })
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "CLOSED"

    # Step 8: Student A rates resolution
    rate_res = client.post(f"/api/v1/complaints/{c_id}/rating", headers={"Authorization": f"Bearer {t_stud_a}"}, json={
        "score": 5,
        "feedback": "Prompt service!"
    })
    assert rate_res.status_code == 201

def test_attachment_security(client, setup_seed):
    # Setup users
    client.post("/api/v1/auth/register", json={"email": "s_owner@campusflow.edu", "full_name": "S Owner", "password": "Password123!"})
    client.post("/api/v1/auth/register", json={"email": "s_other@campusflow.edu", "full_name": "S Other", "password": "Password123!"})

    t_owner = client.post("/api/v1/auth/login", json={"email": "s_owner@campusflow.edu", "password": "Password123!"}).json()["access_token"]
    t_other = client.post("/api/v1/auth/login", json={"email": "s_other@campusflow.edu", "password": "Password123!"}).json()["access_token"]

    # Create complaint
    c_res = client.post("/api/v1/complaints", headers={"Authorization": f"Bearer {t_owner}"}, json={
        "title": "Broken window", "description": "Glass cracked", "category_id": setup_seed["cat_hvac_id"], "location_id": setup_seed["room_id"]
    }).json()
    c_id = c_res["id"]

    # Upload attachment (valid image)
    file_content = b"fake image bytes content"
    upload_res = client.post(
        f"/api/v1/complaints/{c_id}/attachments",
        headers={"Authorization": f"Bearer {t_owner}"},
        files={"file": ("photo.jpg", io.BytesIO(file_content), "image/jpeg")}
    )
    assert upload_res.status_code == 201
    storage_key = upload_res.json()["storage_key"]

    # Download attachment by owner -> Should succeed (200)
    dl_owner = client.get(f"/api/v1/attachments/{storage_key}", headers={"Authorization": f"Bearer {t_owner}"})
    assert dl_owner.status_code == 200

    # IDOR check: Download attachment by other student -> Expect 403 Forbidden
    dl_other = client.get(f"/api/v1/attachments/{storage_key}", headers={"Authorization": f"Bearer {t_other}"})
    assert dl_other.status_code == 403

def test_analytics_and_notifications(client, db_session, setup_seed):
    register_user(db_session, UserCreate(email="admin_analytics@campusflow.edu", full_name="Admin Analytics", password="Password123!", role=UserRole.ADMIN))
    t_admin = client.post("/api/v1/auth/login", json={"email": "admin_analytics@campusflow.edu", "password": "Password123!"}).json()["access_token"]

    analytics_res = client.get("/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {t_admin}"})
    assert analytics_res.status_code == 200
    data = analytics_res.json()
    assert "kpi" in data
    assert "by_category" in data
    assert "by_location" in data
    assert "staff_workload" in data
