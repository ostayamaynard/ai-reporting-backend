from pydantic import BaseModel
from datetime import date
from typing import List, Optional
class KPIIn(BaseModel):
    name: str
    unit: Optional[str] = None
    aggregation: str = "sum"
class KPIOut(BaseModel):
    id: int
    name: str
    unit: Optional[str]
    aggregation: str
    class Config: from_attributes = True
class GoalItem(BaseModel):
    kpi: str
    target_value: float
    unit: str | None = None
    aggregation: str | None = None
class GoalCreate(BaseModel):
    period_type: str
    period_start: date
    period_end: date
    items: List[GoalItem]
class AnalyzeIn(BaseModel):
    report_id: str
    goal_period: str
class AnalyzeOut(BaseModel):
    summary_md: str
    kpi_table: list
    anomalies: list
    trend: dict
    suggestions: Optional[List[str]] = []

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatIn(BaseModel):
    report_id: str
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatOut(BaseModel):
    message: str
    role: str = "assistant"
