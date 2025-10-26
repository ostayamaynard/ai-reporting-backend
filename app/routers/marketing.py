"""
Marketing Agent API Router

This module provides API endpoints for the Marketing AI Agent.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import MarketingReport, ReportType
from ..deps import api_key_guard
from ..agents.marketing_agent import MarketingAgent
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(api_key_guard)], prefix="/marketing", tags=["Marketing Agent"])


# Schemas
class MarketingReportResponse(BaseModel):
    id: str
    report_type: str
    period_start: date
    period_end: date
    leads_generated: int
    ad_spend: Optional[float]
    ctr: Optional[float]
    roi: Optional[float]
    traffic_growth: Optional[float]
    engagement_rate: Optional[float]
    summary_text: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class GenerateReportRequest(BaseModel):
    deliver: bool = True


@router.post("/reports/weekly", response_model=MarketingReportResponse)
def generate_weekly_report(
    request: GenerateReportRequest = GenerateReportRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate a weekly marketing report.

    This endpoint triggers the Marketing AI Agent to:
    1. Fetch marketing data from Zoho for the past week
    2. Analyze campaign performance, leads, and engagement
    3. Create visualizations
    4. Optionally deliver the report via email/Slack
    """
    try:
        agent = MarketingAgent(db)
        report = agent.generate_weekly_report(deliver=request.deliver)

        return MarketingReportResponse(
            id=report.id,
            report_type=report.report_type.value,
            period_start=report.period_start,
            period_end=report.period_end,
            leads_generated=report.leads_generated,
            ad_spend=float(report.ad_spend) if report.ad_spend else None,
            ctr=float(report.ctr) if report.ctr else None,
            roi=float(report.roi) if report.roi else None,
            traffic_growth=float(report.traffic_growth) if report.traffic_growth else None,
            engagement_rate=float(report.engagement_rate) if report.engagement_rate else None,
            summary_text=report.summary_text,
            created_at=report.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly report: {str(e)}")


@router.post("/reports/monthly", response_model=MarketingReportResponse)
def generate_monthly_report(
    request: GenerateReportRequest = GenerateReportRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate a monthly marketing report.

    This endpoint triggers the Marketing AI Agent to:
    1. Fetch marketing data from Zoho for the past month
    2. Analyze campaign performance, leads, and engagement
    3. Create visualizations
    4. Optionally deliver the report via email/Slack
    """
    try:
        agent = MarketingAgent(db)
        report = agent.generate_monthly_report(deliver=request.deliver)

        return MarketingReportResponse(
            id=report.id,
            report_type=report.report_type.value,
            period_start=report.period_start,
            period_end=report.period_end,
            leads_generated=report.leads_generated,
            ad_spend=float(report.ad_spend) if report.ad_spend else None,
            ctr=float(report.ctr) if report.ctr else None,
            roi=float(report.roi) if report.roi else None,
            traffic_growth=float(report.traffic_growth) if report.traffic_growth else None,
            engagement_rate=float(report.engagement_rate) if report.engagement_rate else None,
            summary_text=report.summary_text,
            created_at=report.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating monthly report: {str(e)}")


@router.get("/reports", response_model=List[MarketingReportResponse])
def list_marketing_reports(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    report_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List marketing reports.

    Query parameters:
    - limit: Number of reports to return (1-100, default: 10)
    - offset: Number of reports to skip (default: 0)
    - report_type: Filter by report type (marketing_weekly or marketing_monthly)
    """
    query = db.query(MarketingReport)

    if report_type:
        try:
            rt = ReportType(report_type)
            query = query.filter(MarketingReport.report_type == rt)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")

    reports = query.order_by(MarketingReport.created_at.desc()).offset(offset).limit(limit).all()

    return [
        MarketingReportResponse(
            id=r.id,
            report_type=r.report_type.value,
            period_start=r.period_start,
            period_end=r.period_end,
            leads_generated=r.leads_generated,
            ad_spend=float(r.ad_spend) if r.ad_spend else None,
            ctr=float(r.ctr) if r.ctr else None,
            roi=float(r.roi) if r.roi else None,
            traffic_growth=float(r.traffic_growth) if r.traffic_growth else None,
            engagement_rate=float(r.engagement_rate) if r.engagement_rate else None,
            summary_text=r.summary_text,
            created_at=r.created_at.isoformat()
        )
        for r in reports
    ]


@router.get("/reports/{report_id}", response_model=MarketingReportResponse)
def get_marketing_report(report_id: str, db: Session = Depends(get_db)):
    """
    Get a specific marketing report by ID.
    """
    report = db.query(MarketingReport).filter(MarketingReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return MarketingReportResponse(
        id=report.id,
        report_type=report.report_type.value,
        period_start=report.period_start,
        period_end=report.period_end,
        leads_generated=report.leads_generated,
        ad_spend=float(report.ad_spend) if report.ad_spend else None,
        ctr=float(report.ctr) if report.ctr else None,
        roi=float(report.roi) if report.roi else None,
        traffic_growth=float(report.traffic_growth) if report.traffic_growth else None,
        engagement_rate=float(report.engagement_rate) if report.engagement_rate else None,
        summary_text=report.summary_text,
        created_at=report.created_at.isoformat()
    )


@router.delete("/reports/{report_id}")
def delete_marketing_report(report_id: str, db: Session = Depends(get_db)):
    """
    Delete a marketing report.
    """
    report = db.query(MarketingReport).filter(MarketingReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()

    return {"message": "Report deleted successfully", "report_id": report_id}
