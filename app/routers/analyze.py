# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from datetime import date, timedelta
# from ..schemas import AnalyzeIn, AnalyzeOut
# from ..database import get_db
# from ..models import Report, ReportMetric, KPI, Goal, Analysis
# from ..deps import api_key_guard
# from ..services.ai import summarize
# router = APIRouter(dependencies=[Depends(api_key_guard)])

# def infer_period_bounds(goal_period: str):
#     today = date.today()
#     if goal_period == "monthly":
#         start = today.replace(day=1)
#         next_start = (date(start.year+1,1,1) if start.month==12 else date(start.year, start.month+1,1))
#         return start, next_start - timedelta(days=1)
#     if goal_period == "quarterly":
#         q = (today.month-1)//3 + 1
#         start_month = 3*(q-1)+1
#         start = date(today.year, start_month, 1)
#         next_start = date(today.year+1,1,1) if q==4 else date(today.year, start_month+3,1)
#         return start, next_start - timedelta(days=1)
#     raise ValueError("Invalid goal_period")

# @router.post("/analyze", response_model=AnalyzeOut)
# def analyze(payload: AnalyzeIn, db: Session = Depends(get_db)):
#     report = db.query(Report).filter_by(id=payload.report_id).first()
#     if not report: raise HTTPException(status_code=404, detail="Report not found")
#     start, end = infer_period_bounds(payload.goal_period)
#     rows = db.query(KPI.name, func.sum(ReportMetric.value).label("actual")
#         ).join(ReportMetric, ReportMetric.kpi_id==KPI.id
#         ).filter(ReportMetric.report_id==report.id
#         ).filter(ReportMetric.date>=start, ReportMetric.date<=end
#         ).group_by(KPI.name).all()
#     actuals = {name: float(val or 0) for name,val in rows}
#     goal_rows = db.query(Goal, KPI).join(KPI, KPI.id==Goal.kpi_id
#         ).filter(Goal.period_type==payload.goal_period
#         ).filter(Goal.period_start<=end, Goal.period_end>=start).all()
#     kpi_table, anomalies, trend = [], [], {}
#     for g,k in goal_rows:
#         actual = actuals.get(k.name, 0.0)
#         variance = actual - float(g.target_value)
#         status = "above" if variance >= 0 else "below"
#         kpi_table.append({"kpi": k.name, "target": float(g.target_value),
#                           "actual": actual, "variance": variance, "status": status})
#         if float(g.target_value) != 0 and abs(variance) > 0.2 * float(g.target_value):
#             anomalies.append({"kpi": k.name, "note": f"Variance {variance:.2f} exceeds 20% of target"})
#         trend[k.name] = "up" if variance > 0 else ("flat" if variance == 0 else "down")
#     summary_md = summarize(kpi_table, anomalies, trend)
#     analysis = Analysis(report_id=report.id, goal_period=payload.goal_period,
#                         summary_md=summary_md, comparisons_json=kpi_table)
#     db.add(analysis); db.commit()
#     return AnalyzeOut(summary_md=summary_md, kpi_table=kpi_table, anomalies=anomalies, trend=trend)
# app/routers/analyze.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from ..schemas import AnalyzeIn, AnalyzeOut
from ..database import get_db
from ..models import Report, ReportMetric, KPI, Goal, Analysis
from ..deps import api_key_guard
from ..services.ai import summarize_with_openai

router = APIRouter(dependencies=[Depends(api_key_guard)])

def infer_period_bounds(goal_period: str):
    today = date.today()
    if goal_period == "monthly":
        start = today.replace(day=1)
        next_start = (date(start.year+1,1,1) if start.month==12 else date(start.year, start.month+1,1))
        return start, next_start - timedelta(days=1)
    if goal_period == "quarterly":
        q = (today.month-1)//3 + 1
        start_month = 3*(q-1)+1
        start = date(today.year, start_month, 1)
        next_start = date(today.year+1,1,1) if q==4 else date(today.year, start_month+3,1)
        return start, next_start - timedelta(days=1)
    raise ValueError("Invalid goal_period")

def _sum_by_kpi_for_report(db: Session, report_id: str, start: date, end: date) -> dict:
    rows = (db.query(KPI.name, func.sum(ReportMetric.value).label("actual"))
              .join(ReportMetric, ReportMetric.kpi_id==KPI.id)
              .filter(ReportMetric.report_id==report_id)
              .filter(ReportMetric.date>=start, ReportMetric.date<=end)
              .group_by(KPI.name).all())
    return {name: float(val or 0) for name, val in rows}

def _previous_report(db: Session, report: Report) -> Report | None:
    return (db.query(Report)
              .filter(Report.created_at < report.created_at)
              .order_by(Report.created_at.desc())
              .first())

@router.post("/analyze", response_model=AnalyzeOut)
def analyze(payload: AnalyzeIn, db: Session = Depends(get_db)):
    # Extend the schema contract on-the-fly
    use_ai = getattr(payload, "use_ai", True)
    compare_to_last = getattr(payload, "compare_to_last", True)

    report = db.query(Report).filter_by(id=payload.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    start, end = infer_period_bounds(payload.goal_period)

    # Actuals for the current report
    actuals = _sum_by_kpi_for_report(db, report.id, start, end)

    # Goals for the period
    goal_rows = (db.query(Goal, KPI)
                  .join(KPI, KPI.id==Goal.kpi_id)
                  .filter(Goal.period_type==payload.goal_period)
                  .filter(Goal.period_start<=end, Goal.period_end>=start)
                  .all())

    kpi_table, anomalies, trend = [], [], {}
    for g, k in goal_rows:
        actual = actuals.get(k.name, 0.0)
        variance = actual - float(g.target_value)
        status = "above" if variance >= 0 else "below"
        kpi_table.append({
            "kpi": k.name,
            "target": float(g.target_value),
            "actual": actual,
            "variance": variance,
            "status": status
        })
        if float(g.target_value) != 0 and abs(variance) > 0.2 * float(g.target_value):
            anomalies.append({"kpi": k.name, "note": f"Variance {variance:.2f} exceeds 20% of target"})
        trend[k.name] = "up" if variance > 0 else ("flat" if variance == 0 else "down")

    # Compare to previous report (optional)
    prev_delta = None
    if compare_to_last:
        prev = _previous_report(db, report)
        if prev:
            prev_actuals = _sum_by_kpi_for_report(db, prev.id, start, end)
            prev_delta = []
            for row in kpi_table:
                name = row["kpi"]
                delta = row["actual"] - float(prev_actuals.get(name, 0))
                prev_delta.append({
                    "kpi": name,
                    "delta": delta,
                    "delta_sign": "▲" if delta > 0 else ("■" if delta == 0 else "▼")
                })

    # AI summary (or fallback)
    if use_ai:
        summary_md = summarize_with_openai(kpi_table, anomalies, trend, prev_delta)
    else:
        summary_md = summarize_with_openai(kpi_table, anomalies, trend, prev_delta=None)

    analysis = Analysis(report_id=report.id, goal_period=payload.goal_period,
                        summary_md=summary_md, comparisons_json=kpi_table)
    db.add(analysis); db.commit()

    # Extend the response contract on-the-fly with deltas
    out = AnalyzeOut(summary_md=summary_md, kpi_table=kpi_table, anomalies=anomalies, trend=trend)
    # You’ll still see summary + kpi table in the response; deltas are “baked into” the summary.
    return out
