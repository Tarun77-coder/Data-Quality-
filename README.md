# Data Quality Auditor

A small full-stack application for uploading CSV/JSON datasets, running configurable data-quality checks, and exporting the resulting issue report.

## Checks

- Schema: missing and unexpected columns
- Nulls: null count and percentage per column
- Duplicates: fully duplicated rows
- Custom rule: numeric range or regular expression

## Stack

- Frontend: React + Vite
- Backend: FastAPI + Python 3.11
- Authentication: Supabase Auth
- Data processing: pandas
- Deployment: Vercel (frontend) and Render/Docker (backend)

## Local setup

### 1. Backend

```bash
cd backend
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` manually if `cp` is unavailable.

Fill in:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `SUPABASE_JWT_SECRET`
- `FRONTEND_URL`

Start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000 and Swagger at http://localhost:8000/docs.

### 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Copy `.env.example` to `.env` and set your Supabase URL/key.

Start Vite:

```bash
npm run dev
```

The frontend normally runs at http://localhost:5173.

## Tests

From the `backend` directory:

```bash
pytest -q
```

## Demo

Start the backend first, log in through the frontend or obtain a valid Supabase access token, then from the project root:

```bash
./run_demo.sh <SUPABASE_ACCESS_TOKEN>
```

On Windows Git Bash:

```bash
bash run_demo.sh <SUPABASE_ACCESS_TOKEN>
```

The sample dataset contains one null, one duplicate row, and two age-range violations.

## API

- `GET /health`
- `POST /upload`
- `POST /checks/run`
- `GET /results/{run_id}`
- `GET /results/{run_id}/export?format=csv`
- `GET /results/{run_id}/export?format=json`

All application endpoints except `/`, `/health`, and `/docs` require a Supabase access token.

## Important

The current MVP stores uploaded datasets and results in memory. Restarting the backend clears them. Supabase is currently used for authentication; persistent run storage is intentionally not implemented in this version.
