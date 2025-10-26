from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, DateTime, Numeric, ForeignKey, Enum, JSON, func
import enum
from .database import Base
class Aggregation(str, enum.Enum):
    sum = "sum"
    avg = "avg"
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
