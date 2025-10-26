from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas import GoalCreate
from ..models import KPI, Goal, Aggregation
from ..database import get_db
from ..deps import api_key_guard
router = APIRouter(dependencies=[Depends(api_key_guard)])
@router.post("/goals")
def create_goals(payload: GoalCreate, db: Session = Depends(get_db)):
    created = []
    for item in payload.items:
        kpi = db.query(KPI).filter_by(name=item.kpi).first()
        if not kpi:
            kpi = KPI(name=item.kpi, unit=item.unit, aggregation=Aggregation(item.aggregation or "sum"))
            db.add(kpi); db.flush()
        g = Goal(kpi_id=kpi.id, period_type=payload.period_type,
                 period_start=payload.period_start, period_end=payload.period_end,
                 target_value=item.target_value)
        db.add(g); created.append(kpi.name)
    db.commit(); return {"status":"ok","kpis":created}
@router.get("/goals")
def list_goals(period_type: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Goal, KPI).join(KPI, KPI.id==Goal.kpi_id)
    if period_type: q = q.filter(Goal.period_type==period_type)
    return [{"id": g.id, "kpi": k.name, "period_type": g.period_type,
             "period_start": str(g.period_start), "period_end": str(g.period_end),
             "target_value": float(g.target_value)} for g,k in q.all()]
