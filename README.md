# DB-API (FastAPI + PostgreSQL)

Minimal CRUD API for a `companies` table, plus CSV upload and XLSX download.

## Requirements
- Python 3.10+
- PostgreSQL

## Local Setup
Create database:
```bash
createdb app_db
```

Set connection string:
```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/app_db"
```

If your password has special chars (like `@`), URL-encode them (`@` -> `%40`).

Install deps:
```bash
pip install -r requirements.txt
```

Run:
```bash
uvicorn main:app --reload
```

## Endpoints
- GET `/companies`
- GET `/companies/{id}`
- POST `/companies`
- PUT `/companies/{id}`
- DELETE `/companies/{id}`
- POST `/companies/upload-csv`
- GET `/companies/download/xlsx`

## CSV Upload
CSV must include headers: `name,email,website`

```bash
curl -X POST "http://127.0.0.1:8000/companies/upload-csv" \
  -F "file=@companies.csv"
```

## XLSX Download
```bash
curl -o companies.xlsx "http://127.0.0.1:8000/companies/download/xlsx"
```

---

# Deploy on Render.com

## 1. Push to GitHub
Render deploys from a Git repo. Push this project to GitHub.

## 2. Create Postgres on Render
- In Render Dashboard → New → PostgreSQL
- Choose free plan
- After creation, copy the **Internal Database URL**

## 3. Create Web Service
- New → Web Service → Connect your GitHub repo
- Runtime: Python
- Build Command:
  ```
  pip install -r requirements.txt
  ```
- Start Command:
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

## 4. Set Environment Variables
In the Web Service settings:
- `DATABASE_URL` = Internal Database URL from Render Postgres

## 5. Deploy
Click **Deploy**. Wait until status is **Live**.

## 6. Test
```bash
curl -o companies.xlsx "https://YOUR-SERVICE.onrender.com/companies/download/xlsx"
```

If XLSX is empty, upload CSV to Render first:
```bash
curl -X POST "https://YOUR-SERVICE.onrender.com/companies/upload-csv" \
  -F "file=@companies.csv"
```

## Notes
- Tables are created automatically on startup.
- Keep `DATABASE_URL` secret.