import uuid, os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Report, ReportMetric, KPI
from ..deps import api_key_guard
from ..config import settings
from ..services.parsing import parse_file
router = APIRouter(dependencies=[Depends(api_key_guard)])

@router.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    """List all uploaded reports"""
    reports = db.query(Report).order_by(Report.created_at.desc()).all()

    result = []
    for report in reports:
        # Get KPI count for this report
        kpi_count = db.query(func.count(func.distinct(ReportMetric.kpi_id)))\
            .filter(ReportMetric.report_id == report.id).scalar()

        # Get date range
        date_range = db.query(
            func.min(ReportMetric.date).label('start'),
            func.max(ReportMetric.date).label('end')
        ).filter(ReportMetric.report_id == report.id).first()

        result.append({
            "id": report.id,
            "status": report.status,
            "source": report.source,
            "created_at": str(report.created_at),
            "kpi_count": kpi_count or 0,
            "date_range": {
                "start": str(date_range.start) if date_range.start else None,
                "end": str(date_range.end) if date_range.end else None
            }
        })

    return result

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

@router.get("/reports/{report_id}/data")
def get_report_data(report_id: str, db: Session = Depends(get_db)):
    """Get the raw data from a report in table format"""
    report = db.query(Report).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Get all metrics for this report grouped by date
    rows = (db.query(ReportMetric.date, KPI.name, ReportMetric.value)
              .join(KPI, KPI.id == ReportMetric.kpi_id)
              .filter(ReportMetric.report_id == report_id)
              .order_by(ReportMetric.date.desc())
              .all())

    # Group by date
    data_by_date = {}
    kpis_set = set()
    for date, kpi, value in rows:
        date_str = str(date)
        if date_str not in data_by_date:
            data_by_date[date_str] = {"date": date_str}
        data_by_date[date_str][kpi] = float(value)
        kpis_set.add(kpi)

    # Convert to list and sort by date
    table_data = sorted(data_by_date.values(), key=lambda x: x["date"], reverse=True)

    return {
        "report_id": report_id,
        "kpis": sorted(list(kpis_set)),
        "data": table_data,
        "summary": {
            "total_rows": len(table_data),
            "date_range": {
                "start": str(min([row["date"] for row in table_data])) if table_data else None,
                "end": str(max([row["date"] for row in table_data])) if table_data else None
            }
        }
    }

@router.get("/reports/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get report metadata"""
    report = db.query(Report).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "status": report.status,
        "source": report.source,
        "created_at": str(report.created_at),
        "period_start": str(report.period_start) if report.period_start else None,
        "period_end": str(report.period_end) if report.period_end else None
    }
