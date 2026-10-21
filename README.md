# CampusFlow

CampusFlow is an enterprise-grade campus service request and complaint management platform designed for university infrastructure maintenance. It delivers an end-to-end audit lifecycle for facility operations—including electrical, plumbing, HVAC, and network infrastructure—enforcing role-based access control (RBAC), finite-state machine workflows, dynamic SLA deadline calculations, real-time analytics, and asynchronous task scheduling.

---

## Architecture Overview

CampusFlow is architected with a decoupled service pattern:
- **Client Layer**: Single-Page Application (SPA) built with React, TypeScript, Vite, and Tailwind CSS. State synchronization handled via TanStack Query.
- **API Services Layer**: High-performance RESTful backend built with FastAPI, utilizing Pydantic v2 schemas for strict contract validation and JWT bearer authentication.
- **Persistence Layer**: Relational data store managed through SQLAlchemy ORM and MySQL 8.0, supporting Alembic schema migrations.
- **Asynchronous Task Queue**: Celery distributed task queue backed by Redis for SLA monitoring and automated escalation jobs.

---

## Key Features

### Role-Based Access Control (RBAC)
- **Student**: Submit service requests, track lifecycle status, participate in resolution comment threads, attach verification media, reopen disputed tickets, and submit service ratings.
- **Staff (Departmental Maintenance)**: View assigned departmental tickets, accept tasks, log state updates, append resolution notes, and submit evidence.
- **Admin**: System-wide oversight, manual ticket dispatch and reassignment, SLA configuration, location and category administration, and real-time operational KPI dashboards.
- **Super Admin**: User account governance, system configuration, and administrative rights management.

### Deterministic State Machine Workflow
All tickets follow strict state machine transitions with persistent audit logging in `complaint_status_history`:
- Primary Path: `OPEN` -> `ASSIGNED` -> `IN_PROGRESS` -> `RESOLVED` -> `CLOSED`
- Exception Paths: `OPEN` -> `REJECTED`, `RESOLVED` -> `REOPENED`

### Dynamic SLA Engine & Background Workers
- Priority-driven resolution thresholds:
  - Critical: 4 hours
  - High: 24 hours
  - Medium: 48 hours
  - Low: 72 hours
- Celery worker periodically evaluates active tickets, dynamically flagging breaches and sending system alerts.

### Hierarchical Campus Location Modeling
Relational location schema supporting nested spatial resolution: `Campus` -> `Building` -> `Floor` -> `Room`.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, React Router v6, TanStack Query, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic |
| **Database** | MySQL 8.0, PyMySQL, aiomysql |
| **Distributed Systems** | Redis, Celery |
| **DevOps & Containers** | Docker, Docker Compose |
| **Testing** | Pytest, HTTPX |

---

## Default Test Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| Student | `student@campusflow.edu` | `Password123!` |
| Maintenance Staff (Electrical) | `staff.electrical@campusflow.edu` | `Password123!` |
| Maintenance Staff (Plumbing) | `staff.plumbing@campusflow.edu` | `Password123!` |
| Maintenance Staff (Wi-Fi) | `staff.wifi@campusflow.edu` | `Password123!` |
| Admin | `admin@campusflow.edu` | `Password123!` |
| Super Admin | `superadmin@campusflow.edu` | `Password123!` |

*(The login interface also provides quick-fill options for testing each role immediately.)*

---

## Repository Structure

```text
CampusFlow/
├── backend/
│   ├── alembic/              # Database migration configurations
│   ├── app/
│   │   ├── api/v1/           # Modular REST API route handlers
│   │   ├── core/             # Configuration, database engine, security
│   │   ├── db/               # Initial seed data script
│   │   ├── models/           # SQLAlchemy ORM entity models
│   │   ├── schemas/          # Pydantic v2 data validation schemas
│   │   ├── services/         # Business logic layer
│   │   ├── workers/          # Celery worker application and background tasks
│   │   └── main.py           # FastAPI application entry point
│   ├── tests/                # Automated Pytest suite
│   ├── Dockerfile            # Container definition for backend services
│   └── requirements.txt      # Python package dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI, layout, and domain components
│   │   ├── context/          # Authentication and application context
│   │   ├── pages/            # View pages for Student, Staff, and Admin
│   │   ├── services/         # Axios API client integrations
│   │   └── types/            # TypeScript interface definitions
│   ├── package.json          # Node.js dependencies and scripts
│   └── vite.config.ts        # Vite configuration
├── docker-compose.yml        # Multi-service composition definition
├── .env.example              # Sample environment configuration template
└── README.md                 # Project documentation
```

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL Server or Docker

### 1. Database & Cache Services
Using Docker Compose to launch MySQL and Redis:
```bash
docker-compose up -d db redis
```

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend development server (automatically seeds demo data on initial launch)
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Frontend Setup
```bash
cd frontend

# Install package dependencies
npm install

# Start development server
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## Docker Deployment

To launch the complete application stack (MySQL 8.0, Redis, FastAPI Backend, and Celery Worker):

```bash
docker-compose up --build
```

---

## Testing

Run the automated test suite with Pytest:

```bash
cd backend
pytest -v
```
