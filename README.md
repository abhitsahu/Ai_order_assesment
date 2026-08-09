# AI Order Supervisor

A long-running AI order supervisor POC that oversees e-commerce order lifecycles from creation until completion. Built using **Temporal**, **FastAPI**, **Google Gemini**, **PostgreSQL (Supabase)**, and **Next.js**.

---

## ⚡ Quick Summary

- **One Temporal Workflow per Order**: Maintains state, memory, and history across sleeps and restarts.
- **Event-Driven & Timer-Based Wakeups**: AI wakes up on workflow start, important signals (e.g. `shipment_delayed`), or scheduled timers.
- **Autonomous Actions**: Executes business tools (`message_fulfillment_team`, `message_customer`, `create_internal_note`, etc.) and stores timeline logs.
- **Human-in-the-Loop**: Supports adding run instructions mid-workflow, pause/resume, and manual termination.

```
Next.js (Frontend) ──► FastAPI (Backend) ──► Temporal Worker ──► Gemini AI Agent
                             │                    │
                             ▼                    ▼
                        PostgreSQL         Temporal Server
```

---

## 📋 Prerequisites

- **Python 3.12+** with `pip` or [`uv`](https://docs.astral.sh/uv/)
- **Node.js 18+** with `npm`
- **Temporal CLI** (`curl -sSf https://temporal.download/cli.sh | sh`)
- **Supabase PostgreSQL** database URI & **Gemini API Key**

---

## 🚀 Installation & Setup

### 1. Configure Environment Variables
Copy `backend/.env.example` to `backend/.env` and update your database URI and Gemini API key:

```bash
cp backend/.env.example backend/.env
```

Contents of `backend/.env.example`:
```env
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
TEMPORAL_HOST=localhost:7233
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DEFAULT_WAKEUP_SECONDS=30
APP_ENV=development
LOG_LEVEL=INFO
```

### 2. Install Dependencies

```bash
# Backend (Python via requirements.txt or uv)
cd backend
pip install -r requirements.txt
# or: uv sync

# Frontend (Next.js)
cd ../frontend
npm install
```

---

## 🖥️ Running the Application

Open 3 terminal windows to run the system:

| Terminal | Description | Command |
|----------|-------------|---------|
| **1. Temporal Server** | Start local Temporal engine | `temporal server start-dev`<br>*(or `~/.temporalio/bin/temporal server start-dev`)* |
| **2. Backend API & Worker** | Start FastAPI server & background worker | `cd backend && python -m uvicorn app.main:app --reload --port 8000`<br>*(or `uv run uvicorn app.main:app --reload --port 8000`)* |
| **3. Frontend** | Launch Next.js dashboard | `cd frontend && npm run dev` |

*(Optional)* Seed default supervisor templates (run once):
```bash
cd backend && python scripts/seed_data.py
# or
uv run python scripts/seed_data.py
```

---

## 🔗 Access Links

- **Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Temporal Web UI**: [http://localhost:8233](http://localhost:8233)
