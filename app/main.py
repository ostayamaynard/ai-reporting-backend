from fastapi import FastAPI
from .routers import kpis, goals, reports, analyze
app = FastAPI(title="AI Reporting Agent - Backend MVP")
app.include_router(kpis.router, prefix="", tags=["kpis"])
app.include_router(goals.router, prefix="", tags=["goals"])
app.include_router(reports.router, prefix="", tags=["reports"])
app.include_router(analyze.router, prefix="", tags=["analyze"])
@app.get("/health")
def health():
    return {"status":"ok"}
