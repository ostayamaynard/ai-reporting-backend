from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, DateTime, Numeric, ForeignKey, Enum, JSON, Text, func
import enum
from .database import Base

class Aggregation(str, enum.Enum):
    sum = "sum"
    avg = "avg"

class ReportType(str, enum.Enum):
    finance_weekly = "finance_weekly"
    finance_monthly = "finance_monthly"
    marketing_weekly = "marketing_weekly"
    marketing_monthly = "marketing_monthly"

class KPI(Base):
    __tablename__ = "kpis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=True)
    aggregation: Mapped[Aggregation] = mapped_column(Enum(Aggregation), nullable=False, default=Aggregation.sum)

class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kpi_id: Mapped[int] = mapped_column(ForeignKey("kpis.id"), nullable=False)
    period_type: Mapped[str] = mapped_column(String, nullable=False)
    period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    period_end: Mapped[Date] = mapped_column(Date, nullable=False)
    target_value: Mapped[Numeric] = mapped_column(Numeric(18,6), nullable=False)
    kpi = relationship("KPI")

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    file_uri: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, default="upload")
    period_start: Mapped[Date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String, default="uploaded")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ReportMetric(Base):
    __tablename__ = "report_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), nullable=False)
    kpi_id: Mapped[int] = mapped_column(ForeignKey("kpis.id"), nullable=False)
    value: Mapped[Numeric] = mapped_column(Numeric(18,6), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), nullable=False)
    goal_period: Mapped[str] = mapped_column(String, nullable=False)
    summary_md: Mapped[str] = mapped_column(String, nullable=True)
    comparisons_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# Finance Models
class FinanceReport(Base):
    __tablename__ = "finance_reports"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    period_end: Mapped[Date] = mapped_column(Date, nullable=False)
    revenue: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=True)
    expenses: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=True)
    cash_flow: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=True)
    overdue_invoices_count: Mapped[int] = mapped_column(Integer, default=0)
    overdue_invoices_amount: Mapped[Numeric] = mapped_column(Numeric(18,2), default=0)
    top_clients_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    metrics_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    summary_text: Mapped[str] = mapped_column(Text, nullable=True)
    visualizations_path: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    delivered_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# Marketing Models
class MarketingReport(Base):
    __tablename__ = "marketing_reports"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    period_end: Mapped[Date] = mapped_column(Date, nullable=False)
    leads_generated: Mapped[int] = mapped_column(Integer, default=0)
    ad_spend: Mapped[Numeric] = mapped_column(Numeric(18,2), default=0)
    ctr: Mapped[Numeric] = mapped_column(Numeric(5,2), nullable=True)  # Click-through rate
    roi: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=True)  # Return on investment
    traffic_growth: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=True)
    engagement_rate: Mapped[Numeric] = mapped_column(Numeric(5,2), nullable=True)
    top_campaigns_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    channel_performance_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    metrics_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    summary_text: Mapped[str] = mapped_column(Text, nullable=True)
    visualizations_path: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    delivered_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# Zoho Integration Tracking
class ZohoSyncLog(Base):
    __tablename__ = "zoho_sync_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_name: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "finance", "marketing"
    sync_type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "weekly", "monthly"
    status: Mapped[str] = mapped_column(String, nullable=False)  # "success", "failed", "in_progress"
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# Report Delivery Tracking
class ReportDelivery(Base):
    __tablename__ = "report_deliveries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[str] = mapped_column(String, nullable=False)
    report_table: Mapped[str] = mapped_column(String, nullable=False)  # "finance_reports" or "marketing_reports"
    delivery_method: Mapped[str] = mapped_column(String, nullable=False)  # "email", "slack"
    recipients: Mapped[JSON] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)  # "sent", "failed"
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
