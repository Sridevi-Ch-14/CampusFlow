from app.models.complaint import ComplaintStatusEnum
from app.models.category import Category
from app.models.location import Campus, Building, Floor, Room

def test_complaint_workflow_and_authorization(client, db_session):
    # Seed minimal location and category into test DB
    campus = Campus(name="Test Campus", code="TEST-C")
    db_session.add(campus)
    db_session.flush()

    building = Building(campus_id=campus.id, name="Test Building", code="TB")
    db_session.add(building)
    db_session.flush()

    floor = Floor(building_id=building.id, floor_number=1, name="First Floor")
    db_session.add(floor)
    db_session.flush()

    room = Room(floor_id=floor.id, room_number="101", room_type="Classroom")
    db_session.add(room)
    db_session.flush()

    category = Category(name="Test Category", description="Testing", default_priority="HIGH")
    db_session.add(category)
    db_session.commit()

    # Setup Student 1
    client.post("/api/v1/auth/register", json={"email": "s1@campusflow.edu", "full_name": "S1", "password": "Password123!", "role": "STUDENT"})
    s1_token = client.post("/api/v1/auth/login", json={"email": "s1@campusflow.edu", "password": "Password123!"}).json()["access_token"]

    # Setup Student 2
    client.post("/api/v1/auth/register", json={"email": "s2@campusflow.edu", "full_name": "S2", "password": "Password123!", "role": "STUDENT"})
    s2_token = client.post("/api/v1/auth/login", json={"email": "s2@campusflow.edu", "password": "Password123!"}).json()["access_token"]

    from app.services.auth_service import register_user
    from app.schemas.user import UserCreate
    from app.models.user import UserRole
    register_user(db_session, UserCreate(email="admin1@campusflow.edu", full_name="A1", password="Password123!", role=UserRole.ADMIN))
    admin_token = client.post("/api/v1/auth/login", json={"email": "admin1@campusflow.edu", "password": "Password123!"}).json()["access_token"]

    # Student 1 creates complaint
    res = client.post(
        "/api/v1/complaints",
        headers={"Authorization": f"Bearer {s1_token}"},
        json={
            "title": "Broken Faucet in Restroom",
            "description": "Leaking constantly",
            "category_id": category.id,
            "location_id": room.id,
            "priority": "HIGH"
        }
    )
    assert res.status_code == 201
    complaint = res.json()
    c_id = complaint["id"]
    assert complaint["status"] == "OPEN"
    assert complaint["complaint_number"].startswith("CF-")

    # IDOR Check: Student 2 tries to access Student 1's complaint -> Expect 403 Forbidden
    idor_res = client.get(
        f"/api/v1/complaints/{c_id}",
        headers={"Authorization": f"Bearer {s2_token}"}
    )
    assert idor_res.status_code == 403

    # Illegal state transition test: Try OPEN -> RESOLVED directly without ASSIGNED/IN_PROGRESS -> Expect 400 Bad Request
    bad_trans = client.patch(
        f"/api/v1/complaints/{c_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"target_status": "RESOLVED"}
    )
    assert bad_trans.status_code == 400
