import uuid, os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Report, ReportMetric, KPI
from ..deps import api_key_guard
from ..config import settings
from ..services.parsing import parse_file
router = APIRouter(dependencies=[Depends(api_key_guard)])
@router.post("/reports/upload")
def upload_report(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv",".tsv",".xlsx",".xls",".pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    report_id = str(uuid.uuid4())
    os.makedirs(settings.upload_dir, exist_ok=True)
    dest = os.path.join(settings.upload_dir, f"{report_id}{ext}")
    with open(dest, "wb") as f: f.write(file.file.read())
    metrics = parse_file(dest)
    report = Report(id=report_id, file_uri=dest, status="parsed")
    db.add(report); db.flush()
    cache = {k.name: k for k in db.query(KPI).all()}
    for m in metrics:
        name = m["kpi"]
        if name not in cache:
            from ..models import Aggregation, KPI as KPIModel
            k = KPIModel(name=name, unit=None, aggregation=Aggregation.sum)
            db.add(k); db.flush(); cache[name] = k
        for d, v in m["values"].items():
            db.add(ReportMetric(report_id=report_id, kpi_id=cache[name].id, value=v, date=d))
    db.commit(); return {"report_id": report_id, "status":"uploaded"}
