from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas import KPIIn, KPIOut
from ..models import KPI, Aggregation
from ..database import get_db
from ..deps import api_key_guard
router = APIRouter(dependencies=[Depends(api_key_guard)])
@router.post("/kpis", response_model=KPIOut)
def create_kpi(payload: KPIIn, db: Session = Depends(get_db)):
    kpi = KPI(name=payload.name, unit=payload.unit, aggregation=Aggregation(payload.aggregation))
    db.add(kpi)
    db.commit()
    db.refresh(kpi)
    return kpi
@router.get("/kpis", response_model=list[KPIOut])
def list_kpis(db: Session = Depends(get_db)):
    return db.query(KPI).all()
