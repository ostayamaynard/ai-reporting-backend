from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import kpis, goals, reports, analyze, finance, marketing
from .scheduler import start_scheduler, shutdown_scheduler, get_scheduled_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()


app = FastAPI(
    title="AI Reporting Agent - Finance & Marketing",
    description="AI-powered agents for automated finance and marketing reporting with Zoho integration",
    version="1.0.0",
    lifespan=lifespan
)

# Legacy routers
app.include_router(kpis.router, prefix="", tags=["KPIs"])
app.include_router(goals.router, prefix="", tags=["Goals"])
app.include_router(reports.router, prefix="", tags=["Reports"])
app.include_router(analyze.router, prefix="", tags=["Analysis"])

# AI Agent routers
app.include_router(finance.router, prefix="/api/v1", tags=["Finance Agent"])
app.include_router(marketing.router, prefix="/api/v1", tags=["Marketing Agent"])


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "agents": ["finance", "marketing"]
    }


@app.get("/")
def root():
    return {
        "message": "AI Reporting Agent - Finance & Marketing",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/scheduled-jobs")
def scheduled_jobs():
    """
    Get information about all scheduled jobs.
    """
    return {
        "jobs": get_scheduled_jobs()
    }
