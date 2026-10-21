import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.location import Campus, Building, Floor, Room
from app.models.sla_config import SLAConfig
from app.models.complaint import Complaint, PriorityEnum, ComplaintStatusEnum
from app.models.status_history import ComplaintStatusHistory
from app.models.assignment import ComplaintAssignment
from app.models.comment import ComplaintComment
from app.models.notification import Notification

def seed_database(db: Session):
    print("🌱 Starting database seeding...")
    Base.metadata.create_all(bind=engine)

    # 1. SLA Configurations
    sla_data = [
        {"priority": "LOW", "resolution_time_hours": 72},
        {"priority": "MEDIUM", "resolution_time_hours": 48},
        {"priority": "HIGH", "resolution_time_hours": 24},
        {"priority": "CRITICAL", "resolution_time_hours": 4},
    ]
    for s in sla_data:
        if not db.query(SLAConfig).filter(SLAConfig.priority == s["priority"]).first():
            sla_config = SLAConfig(**s)
            db.add(sla_config)

    # 2. Categories
    categories_data = [
        {"name": "Electrical", "description": "Power outages, faulty wiring, broken light fixtures, short circuits", "default_priority": "HIGH"},
        {"name": "Plumbing", "description": "Water leaks, clogged pipes, broken faucets, flush issues", "default_priority": "HIGH"},
        {"name": "HVAC / Air Conditioning", "description": "AC cooling failure, heater malfunction, ventilation issues", "default_priority": "MEDIUM"},
        {"name": "Internet / Wi-Fi", "description": "Wi-Fi access point down, slow speeds, ethernet port non-functional", "default_priority": "MEDIUM"},
        {"name": "Furniture", "description": "Broken desks, chairs, whiteboards, door locks, cupboard damage", "default_priority": "LOW"},
        {"name": "Cleanliness & Sanitation", "description": "Trash overflow, uncleaned restrooms, spill cleanup required", "default_priority": "MEDIUM"},
        {"name": "Security & Access Control", "description": "CCTV camera issue, keycard reader non-functional, gate lock broken", "default_priority": "CRITICAL"},
        {"name": "Transport & Parking", "description": "Campus shuttle complaint, barrier gate issue", "default_priority": "LOW"},
        {"name": "Classroom Equipment", "description": "Projector not displaying, podium mic audio issues", "default_priority": "HIGH"},
        {"name": "Other Facility Issue", "description": "General campus maintenance issues", "default_priority": "LOW"}
    ]
    category_map = {}
    for cat in categories_data:
        existing = db.query(Category).filter(Category.name == cat["name"]).first()
        if not existing:
            existing = Category(**cat)
            db.add(existing)
            db.flush()
        category_map[cat["name"]] = existing.id

    # 3. Locations (Campus -> Building -> Floor -> Room)
    campus = db.query(Campus).filter(Campus.code == "MAIN-CAMPUS").first()
    if not campus:
        campus = Campus(name="Central University Campus", code="MAIN-CAMPUS")
        db.add(campus)
        db.flush()

    buildings_data = [
        {
            "name": "Science & Tech Building",
            "code": "STB",
            "floors": [
                {"number": 1, "name": "Ground Floor", "rooms": [("101", "Lab"), ("102", "Lecture Hall"), ("Restroom G-1", "Restroom")]},
                {"number": 2, "name": "Second Floor", "rooms": [("201", "Computer Lab"), ("202", "Faculty Office")]}
            ]
        },
        {
            "name": "Engineering Block B",
            "code": "ENG-B",
            "floors": [
                {"number": 1, "name": "Ground Floor", "rooms": [("B101", "Workshop"), ("B102", "Robotics Lab")]},
                {"number": 3, "name": "Third Floor", "rooms": [("B301", "Auditorium"), ("B305", "Classroom")]}
            ]
        },
        {
            "name": "Student Hostel Complex A",
            "code": "SHA",
            "floors": [
                {"number": 1, "name": "First Floor", "rooms": [("H-104", "Dorm Room"), ("H-108", "Common Room")]},
                {"number": 2, "name": "Second Floor", "rooms": [("H-210", "Dorm Room"), ("Restroom 2F", "Restroom")]}
            ]
        }
    ]

    room_ids = []
    for b_data in buildings_data:
        b_obj = db.query(Building).filter(Building.code == b_data["code"]).first()
        if not b_obj:
            b_obj = Building(campus_id=campus.id, name=b_data["name"], code=b_data["code"])
            db.add(b_obj)
            db.flush()
        for f_data in b_data["floors"]:
            f_obj = db.query(Floor).filter(Floor.building_id == b_obj.id, Floor.floor_number == f_data["number"]).first()
            if not f_obj:
                f_obj = Floor(building_id=b_obj.id, floor_number=f_data["number"], name=f_data["name"])
                db.add(f_obj)
                db.flush()
            for r_num, r_type in f_data["rooms"]:
                r_obj = db.query(Room).filter(Room.floor_id == f_obj.id, Room.room_number == r_num).first()
                if not r_obj:
                    r_obj = Room(floor_id=f_obj.id, room_number=r_num, room_type=r_type)
                    db.add(r_obj)
                    db.flush()
                room_ids.append(r_obj.id)

    # 4. Users (Student, Staff, Admin, Super Admin)
    password_hash = get_password_hash("Password123!")

    users_data = [
        {"email": "student@campusflow.edu", "full_name": "Alice Smith", "role": UserRole.STUDENT, "department": "Computer Science"},
        {"email": "student2@campusflow.edu", "full_name": "Bob Johnson", "role": UserRole.STUDENT, "department": "Electrical Eng"},
        {"email": "staff.electrical@campusflow.edu", "full_name": "Charlie Electrical Staff", "role": UserRole.STAFF, "department": "Electrical Maintenance"},
        {"email": "staff.plumbing@campusflow.edu", "full_name": "David Plumbing Staff", "role": UserRole.STAFF, "department": "Plumbing & Sanitation"},
        {"email": "staff.wifi@campusflow.edu", "full_name": "Eva IT Support Staff", "role": UserRole.STAFF, "department": "IT & Network Infrastructure"},
        {"email": "admin@campusflow.edu", "full_name": "Frank Admin Manager", "role": UserRole.ADMIN, "department": "Campus Operations"},
        {"email": "superadmin@campusflow.edu", "full_name": "Grace Super Admin", "role": UserRole.SUPER_ADMIN, "department": "University Executive Directorate"}
    ]

    user_map = {}
    for u in users_data:
        existing_u = db.query(User).filter(User.email == u["email"]).first()
        if not existing_u:
            existing_u = User(
                email=u["email"],
                full_name=u["full_name"],
                password_hash=password_hash,
                role=u["role"],
                department=u["department"]
            )
            db.add(existing_u)
            db.flush()
        user_map[u["email"]] = existing_u

    db.commit()

    # 5. Seed Demo Complaints
    student = user_map["student@campusflow.edu"]
    staff_elec = user_map["staff.electrical@campusflow.edu"]
    staff_wifi = user_map["staff.wifi@campusflow.edu"]
    admin = user_map["admin@campusflow.edu"]

    complaints_data = [
        {
            "complaint_number": "CF-10001",
            "title": "Air Conditioner Leaking Water in Room 201",
            "description": "The AC unit in CS Lab 201 is leaking water directly onto desk space. Requires urgent maintenance.",
            "category_id": category_map["HVAC / Air Conditioning"],
            "location_id": room_ids[0],
            "priority": PriorityEnum.HIGH,
            "status": ComplaintStatusEnum.IN_PROGRESS,
            "creator_id": student.id,
            "assigned_staff_id": staff_elec.id,
            "sla_deadline": datetime.utcnow() + timedelta(hours=18),
            "is_sla_breached": False
        },
        {
            "complaint_number": "CF-10002",
            "title": "Wi-Fi Router Unreachable in Hostel Block A Room H-104",
            "description": "Students cannot connect to Campus-Secure Wi-Fi. Access point lights are flashing red.",
            "category_id": category_map["Internet / Wi-Fi"],
            "location_id": room_ids[min(len(room_ids)-1, 5)],
            "priority": PriorityEnum.MEDIUM,
            "status": ComplaintStatusEnum.ASSIGNED,
            "creator_id": student.id,
            "assigned_staff_id": staff_wifi.id,
            "sla_deadline": datetime.utcnow() + timedelta(hours=36),
            "is_sla_breached": False
        },
        {
            "complaint_number": "CF-10003",
            "title": "Main Projector Bulb Blown in B301 Auditorium",
            "description": "Projector display turns black mid-lecture. Bulb indicator shows lamp replacement error.",
            "category_id": category_map["Classroom Equipment"],
            "location_id": room_ids[min(len(room_ids)-1, 4)],
            "priority": PriorityEnum.CRITICAL,
            "status": ComplaintStatusEnum.OPEN,
            "creator_id": student.id,
            "assigned_staff_id": None,
            "sla_deadline": datetime.utcnow() - timedelta(hours=2),  # SLA breached
            "is_sla_breached": True
        },
        {
            "complaint_number": "CF-10004",
            "title": "Restroom Faucet Leaking on 2nd Floor",
            "description": "Sink 2 faucet water flow does not shut off completely.",
            "category_id": category_map["Plumbing"],
            "location_id": room_ids[1],
            "priority": PriorityEnum.LOW,
            "status": ComplaintStatusEnum.RESOLVED,
            "creator_id": student.id,
            "assigned_staff_id": user_map["staff.plumbing@campusflow.edu"].id,
            "sla_deadline": datetime.utcnow() + timedelta(hours=48),
            "is_sla_breached": False,
            "resolution_notes": "Replaced faulty washer inside faucet valve assembly. Leak resolved and tested."
        }
    ]

    for c_data in complaints_data:
        existing_c = db.query(Complaint).filter(Complaint.complaint_number == c_data["complaint_number"]).first()
        if not existing_c:
            c_obj = Complaint(**c_data)
            db.add(c_obj)
            db.flush()

            # Status history
            hist = ComplaintStatusHistory(
                complaint_id=c_obj.id,
                previous_status=None,
                new_status=ComplaintStatusEnum.OPEN,
                changed_by_id=student.id,
                comment="Initial submission"
            )
            db.add(hist)

            if c_obj.status != ComplaintStatusEnum.OPEN:
                hist2 = ComplaintStatusHistory(
                    complaint_id=c_obj.id,
                    previous_status=ComplaintStatusEnum.OPEN,
                    new_status=c_obj.status,
                    changed_by_id=admin.id,
                    comment="Processed by administrator"
                )
                db.add(hist2)

            if c_obj.assigned_staff_id:
                assign = ComplaintAssignment(
                    complaint_id=c_obj.id,
                    staff_id=c_obj.assigned_staff_id,
                    assigned_by_id=admin.id,
                    notes="Assigned based on technician specialty"
                )
                db.add(assign)

            # Sample comment
            comment = ComplaintComment(
                complaint_id=c_obj.id,
                author_id=admin.id,
                content="Maintenance team notified. Technician will inspect shortly."
            )
            db.add(comment)

    db.commit()
    print("✅ Database successfully seeded!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
