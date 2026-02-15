from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
from openpyxl import Workbook

from database import SessionLocal, engine
from models import Base, Company
from schemas import CompanyCreate, CompanyOut, CompanyUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/companies", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()


@app.get("/companies/download/xlsx")
def download_companies_xlsx(db: Session = Depends(get_db)):
    companies = db.query(Company).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "companies"
    ws.append(["id", "name", "email", "website"])
    for c in companies:
        ws.append([c.id, c.name, c.email, c.website])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=companies.xlsx"
    }
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@app.get("/companies/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@app.post("/companies", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@app.put("/companies/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    for key, value in payload.model_dump().items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    return company


@app.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    db.delete(company)
    db.commit()
    return None


@app.post("/companies/upload-csv", status_code=status.HTTP_201_CREATED)
def upload_companies_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a CSV file")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    required = {"name", "email", "website"}
    if not reader.fieldnames or not required.issubset(set(map(str.lower, reader.fieldnames))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must include headers: name,email,website",
        )

    created = 0
    for row in reader:
        row_normalized = {k.lower(): v for k, v in row.items() if k}
        try:
            payload = CompanyCreate(**row_normalized)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        company = Company(**payload.model_dump())
        db.add(company)
        created += 1

    db.commit()
    return {"created": created}

