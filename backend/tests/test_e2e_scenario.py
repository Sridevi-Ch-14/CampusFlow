import io
import pytest
from app.models.user import UserRole
from app.services.auth_service import register_user
from app.schemas.user import UserCreate

def test_complete_20_step_e2e_scenario(client, db_session):
    # Setup base seed
    from app.models.location import Campus, Building, Floor, Room
    from app.models.category import Category

    campus = Campus(name="Central Campus", code="CC")
    db_session.add(campus)
    db_session.flush()

    building = Building(campus_id=campus.id, name="Engineering Building", code="EB")
    db_session.add(building)
    db_session.flush()

    floor = Floor(building_id=building.id, floor_number=3, name="Third Floor")
    db_session.add(floor)
    db_session.flush()

    room = Room(floor_id=floor.id, room_number="302", room_type="Classroom")
    db_session.add(room)
    db_session.flush()

    category = Category(name="HVAC", description="Heating, Ventilation, Air Conditioning", default_priority="HIGH")
    db_session.add(category)
    db_session.commit()

    # Step 1: Student logs in / registers
    client.post("/api/v1/auth/register", json={
        "email": "e2e_student@campusflow.edu", "full_name": "E2E Student", "password": "Password123!"
    })
    s_token = client.post("/api/v1/auth/login", json={
        "email": "e2e_student@campusflow.edu", "password": "Password123!"
    }).json()["access_token"]
    assert s_token is not None

    # Step 2: Student creates an HVAC complaint
    create_res = client.post("/api/v1/complaints", headers={"Authorization": f"Bearer {s_token}"}, json={
        "title": "HVAC Cooling Failure in EB-302",
        "description": "Temperature in room exceeds 30C during lectures.",
        "category_id": category.id,
        "location_id": room.id,
        "priority": "HIGH"
    })
    assert create_res.status_code == 201
    complaint = create_res.json()
    c_id = complaint["id"]

    # Step 3: Student attaches an image
    file_bytes = b"sample photo binary data"
    att_res = client.post(
        f"/api/v1/complaints/{c_id}/attachments",
        headers={"Authorization": f"Bearer {s_token}"},
        files={"file": ("hvac_unit.jpg", io.BytesIO(file_bytes), "image/jpeg")}
    )
    assert att_res.status_code == 201
    att_key = att_res.json()["storage_key"]

    # Step 4: Admin user setup
    register_user(db_session, UserCreate(email="e2e_admin@campusflow.edu", full_name="E2E Admin", password="Password123!", role=UserRole.ADMIN))
    a_token = client.post("/api/v1/auth/login", json={
        "email": "e2e_admin@campusflow.edu", "password": "Password123!"
    }).json()["access_token"]

    # Step 5: Admin sees the complaint in list
    c_list = client.get("/api/v1/complaints", headers={"Authorization": f"Bearer {a_token}"}).json()
    assert any(item["id"] == c_id for item in c_list["items"])

    # Step 6: Admin creates staff & assigns staff
    register_user(db_session, UserCreate(email="e2e_staff@campusflow.edu", full_name="E2E Staff Tech", password="Password123!", role=UserRole.STAFF))
    st_token = client.post("/api/v1/auth/login", json={
        "email": "e2e_staff@campusflow.edu", "password": "Password123!"
    }).json()["access_token"]
    staff_info = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {st_token}"}).json()

    assign_res = client.post(f"/api/v1/complaints/{c_id}/assign", headers={"Authorization": f"Bearer {a_token}"}, json={
        "staff_id": staff_info["id"],
        "notes": "Urgent repair requested."
    })
    assert assign_res.status_code == 200, f"Failed assign: {assign_res.text}"
    assert assign_res.json()["status"] == "ASSIGNED"

    # Step 7 & 8: Staff logs in and sees assignment
    staff_complaints = client.get("/api/v1/complaints", headers={"Authorization": f"Bearer {st_token}"}).json()
    assert any(item["id"] == c_id for item in staff_complaints["items"])

    # Step 9 & 10: Staff accepts / moves to IN_PROGRESS
    in_prog = client.patch(f"/api/v1/complaints/{c_id}/status", headers={"Authorization": f"Bearer {st_token}"}, json={
        "target_status": "IN_PROGRESS",
        "comment": "Diagnosing compressor issue."
    })
    assert in_prog.status_code == 200
    assert in_prog.json()["status"] == "IN_PROGRESS"

    # Step 11: Staff adds a comment
    comment_res = client.post(f"/api/v1/complaints/{c_id}/comments", headers={"Authorization": f"Bearer {st_token}"}, json={
        "content": "Replaced thermal fuse and recharged coolant.",
        "is_internal": False
    })
    assert comment_res.status_code == 201

    # Step 12: Student sees update & notifications
    notifs = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {s_token}"}).json()
    assert len(notifs) >= 1

    # Step 13: Staff resolves the complaint
    resolve_res = client.patch(f"/api/v1/complaints/{c_id}/status", headers={"Authorization": f"Bearer {st_token}"}, json={
        "target_status": "RESOLVED",
        "resolution_notes": "Unit cooling efficiently at 21C."
    })
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # Step 14: Student receives resolution notification
    notifs_after_res = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {s_token}"}).json()
    assert any("Resolved" in n["title"] or "RESOLVED" in n["message"] or n["notification_type"] == "STATUS_CHANGE" for n in notifs_after_res)

    # Step 15 & 16: Student reviews resolution and closes complaint
    close_res = client.patch(f"/api/v1/complaints/{c_id}/status", headers={"Authorization": f"Bearer {s_token}"}, json={
        "target_status": "CLOSED",
        "comment": "Verified temperature. Working perfectly."
    })
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "CLOSED"

    # Step 17 & 18: Admin verifies complete status & assignment history
    detail = client.get(f"/api/v1/complaints/{c_id}", headers={"Authorization": f"Bearer {a_token}"}).json()
    assert len(detail["status_history"]) >= 4
    assert len(detail["assignments"]) >= 1

    # Step 19: Admin verifies analytics
    analytics = client.get("/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {a_token}"}).json()
    assert analytics["kpi"]["total_complaints"] >= 1
    assert analytics["kpi"]["closed_complaints"] >= 1

    # Step 20: Verify notification unread count and read-all capability
    unread = client.get("/api/v1/notifications/unread-count", headers={"Authorization": f"Bearer {s_token}"}).json()
    assert unread["unread_count"] >= 1
    mark_res = client.post("/api/v1/notifications/read-all", headers={"Authorization": f"Bearer {s_token}"})
    assert mark_res.status_code == 200
