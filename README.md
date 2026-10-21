# 🏫 CampusFlow - Campus Complaint & Service Request System

**CampusFlow** is a production-grade campus service-request and complaint management platform built for universities. It provides a complete, traceable lifecycle for facility problems (Wi-Fi, AC, plumbing, electrical, classroom equipment, etc.) with backend-enforced Role-Based Access Control (RBAC), controlled state machine workflows, dynamic SLA deadline calculations, in-app alert notifications, attachments, and real-time administrative analytics.

---

## 🚀 Key Features

1. **Role-Based Access Control (RBAC)**:
   - 🎓 **Student**: Submit complaints, track status, comment, attach photos/docs, reopen resolved complaints, rate completed service.
   - 🔧 **Staff**: View assigned tasks, accept assignments, update status, add resolution notes and evidence.
   - 📊 **Admin**: View all complaints, assign/reassign to staff, change priority, manage categories and locations, view live KPI analytics and SLA breaches.
   - 👑 **Super Admin**: Manage administrator accounts and system configurations.

2. **Controlled State Machine Workflow**:
   - Explicit transitions: `OPEN` → `ASSIGNED` → `IN_PROGRESS` → `RESOLVED` → `CLOSED`.
   - Alternative transitions: `OPEN` → `REJECTED`, `RESOLVED` → `REOPENED`.
   - Every status change logs an audit entry in `complaint_status_history`.

3. **Dynamic SLA Engine**:
   - Computes SLA deadlines based on priority (`CRITICAL`: 4h, `HIGH`: 24h, `MEDIUM`: 48h, `LOW`: 72h).
   - Periodic background worker (Celery + Redis) scans and flags SLA-breached complaints.

4. **Structured Relational Location Model**:
   - Campus → Building → Floor → Room hierarchy.

5. **Local & Object File Storage**:
   - Stores file metadata in MySQL and actual files on disk/S3 storage.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Vite, React Router v6, TanStack Query, Tailwind CSS, Lucide Icons.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic.
- **Database**: MySQL 8.0 with PyMySQL / aiomysql.
- **Background Processing**: Celery & Redis.

---

## 🔑 Demo Login Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| 🎓 **Student** | `student@campusflow.edu` | `Password123!` |
| 🔧 **Maintenance Staff (Electrical)** | `staff.electrical@campusflow.edu` | `Password123!` |
| 🔧 **Maintenance Staff (Plumbing)** | `staff.plumbing@campusflow.edu` | `Password123!` |
| 🔧 **Maintenance Staff (Wi-Fi)** | `staff.wifi@campusflow.edu` | `Password123!` |
| 📊 **Admin** | `admin@campusflow.edu` | `Password123!` |
| 👑 **Super Admin** | `superadmin@campusflow.edu` | `Password123!` |

*(Note: The sign-in page features one-click buttons to log in as any role instantly!)*

---

## 📦 Local Quickstart Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL Server or Docker

### 1. Backend Setup

Start MySQL container via Docker Compose (or start local MySQL service):
```bash
docker-compose up -d db
```

Run FastAPI Backend:
```bash
cd backend
python -m venv venv
# Activate virtual environment:
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt

# Run FastAPI backend (Auto-creates database & seeds demo data on startup!)
uvicorn app.main:app --reload --port 8000
```
- Interactive API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Web Application UI: [http://localhost:5173](http://localhost:5173)

---

## 🐳 Docker Deployment

To spin up MySQL 8.0, Redis, FastAPI Backend, and Celery Worker together:
```bash
docker-compose up --build
```

---

## 🧪 Automated Testing

Backend test suite with Pytest:
```bash
cd backend
pytest -v
```
