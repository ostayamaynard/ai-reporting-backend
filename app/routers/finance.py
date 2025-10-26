"""
Finance Agent API Router

This module provides API endpoints for the Finance AI Agent.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import FinanceReport, ReportType
from ..deps import api_key_guard
from ..agents.finance_agent import FinanceAgent
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(api_key_guard)], prefix="/finance", tags=["Finance Agent"])


# Schemas
class FinanceReportResponse(BaseModel):
    id: str
    report_type: str
    period_start: date
    period_end: date
    revenue: Optional[float]
    expenses: Optional[float]
    cash_flow: Optional[float]
    overdue_invoices_count: int
    overdue_invoices_amount: Optional[float]
    summary_text: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class GenerateReportRequest(BaseModel):
    deliver: bool = True


@router.post("/reports/weekly", response_model=FinanceReportResponse)
def generate_weekly_report(
    request: GenerateReportRequest = GenerateReportRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate a weekly finance report.

    This endpoint triggers the Finance AI Agent to:
    1. Fetch financial data from Zoho for the past week
    2. Analyze the data and generate insights
    3. Create visualizations
    4. Optionally deliver the report via email/Slack
    """
    try:
        agent = FinanceAgent(db)
        report = agent.generate_weekly_report(deliver=request.deliver)

        return FinanceReportResponse(
            id=report.id,
            report_type=report.report_type.value,
            period_start=report.period_start,
            period_end=report.period_end,
            revenue=float(report.revenue) if report.revenue else None,
            expenses=float(report.expenses) if report.expenses else None,
            cash_flow=float(report.cash_flow) if report.cash_flow else None,
            overdue_invoices_count=report.overdue_invoices_count,
            overdue_invoices_amount=float(report.overdue_invoices_amount) if report.overdue_invoices_amount else None,
            summary_text=report.summary_text,
            created_at=report.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly report: {str(e)}")


@router.post("/reports/monthly", response_model=FinanceReportResponse)
def generate_monthly_report(
    request: GenerateReportRequest = GenerateReportRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate a monthly finance report.

    This endpoint triggers the Finance AI Agent to:
    1. Fetch financial data from Zoho for the past month
    2. Analyze the data and generate insights
    3. Create visualizations
    4. Optionally deliver the report via email/Slack
    """
    try:
        agent = FinanceAgent(db)
        report = agent.generate_monthly_report(deliver=request.deliver)

        return FinanceReportResponse(
            id=report.id,
            report_type=report.report_type.value,
            period_start=report.period_start,
            period_end=report.period_end,
            revenue=float(report.revenue) if report.revenue else None,
            expenses=float(report.expenses) if report.expenses else None,
            cash_flow=float(report.cash_flow) if report.cash_flow else None,
            overdue_invoices_count=report.overdue_invoices_count,
            overdue_invoices_amount=float(report.overdue_invoices_amount) if report.overdue_invoices_amount else None,
            summary_text=report.summary_text,
            created_at=report.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating monthly report: {str(e)}")


@router.get("/reports", response_model=List[FinanceReportResponse])
def list_finance_reports(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    report_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List finance reports.

    Query parameters:
    - limit: Number of reports to return (1-100, default: 10)
    - offset: Number of reports to skip (default: 0)
    - report_type: Filter by report type (finance_weekly or finance_monthly)
    """
    query = db.query(FinanceReport)

    if report_type:
        try:
            rt = ReportType(report_type)
            query = query.filter(FinanceReport.report_type == rt)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")

    reports = query.order_by(FinanceReport.created_at.desc()).offset(offset).limit(limit).all()

    return [
        FinanceReportResponse(
            id=r.id,
            report_type=r.report_type.value,
            period_start=r.period_start,
            period_end=r.period_end,
            revenue=float(r.revenue) if r.revenue else None,
            expenses=float(r.expenses) if r.expenses else None,
            cash_flow=float(r.cash_flow) if r.cash_flow else None,
            overdue_invoices_count=r.overdue_invoices_count,
            overdue_invoices_amount=float(r.overdue_invoices_amount) if r.overdue_invoices_amount else None,
            summary_text=r.summary_text,
            created_at=r.created_at.isoformat()
        )
        for r in reports
    ]


@router.get("/reports/{report_id}", response_model=FinanceReportResponse)
def get_finance_report(report_id: str, db: Session = Depends(get_db)):
    """
    Get a specific finance report by ID.
    """
    report = db.query(FinanceReport).filter(FinanceReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return FinanceReportResponse(
        id=report.id,
        report_type=report.report_type.value,
        period_start=report.period_start,
        period_end=report.period_end,
        revenue=float(report.revenue) if report.revenue else None,
        expenses=float(report.expenses) if report.expenses else None,
        cash_flow=float(report.cash_flow) if report.cash_flow else None,
        overdue_invoices_count=report.overdue_invoices_count,
        overdue_invoices_amount=float(report.overdue_invoices_amount) if report.overdue_invoices_amount else None,
        summary_text=report.summary_text,
        created_at=report.created_at.isoformat()
    )


@router.delete("/reports/{report_id}")
def delete_finance_report(report_id: str, db: Session = Depends(get_db)):
    """
    Delete a finance report.
    """
    report = db.query(FinanceReport).filter(FinanceReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()

    return {"message": "Report deleted successfully", "report_id": report_id}
