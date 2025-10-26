"""
Scheduled Task System for Automated Report Generation

This module sets up scheduled tasks for automatically generating
finance and marketing reports on a weekly and monthly basis.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from .database import SessionLocal
from .agents.finance_agent import FinanceAgent
from .agents.marketing_agent import MarketingAgent
from .config import settings

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()


def finance_weekly_job():
    """
    Scheduled job for generating weekly finance reports.
    """
    logger.info("Starting scheduled finance weekly report generation")

    db = SessionLocal()
    try:
        agent = FinanceAgent(db)
        report = agent.generate_weekly_report(deliver=True)
        logger.info(f"Finance weekly report generated successfully: {report.id}")
    except Exception as e:
        logger.error(f"Error in finance weekly job: {e}")
    finally:
        db.close()


def finance_monthly_job():
    """
    Scheduled job for generating monthly finance reports.
    """
    logger.info("Starting scheduled finance monthly report generation")

    db = SessionLocal()
    try:
        agent = FinanceAgent(db)
        report = agent.generate_monthly_report(deliver=True)
        logger.info(f"Finance monthly report generated successfully: {report.id}")
    except Exception as e:
        logger.error(f"Error in finance monthly job: {e}")
    finally:
        db.close()


def marketing_weekly_job():
    """
    Scheduled job for generating weekly marketing reports.
    """
    logger.info("Starting scheduled marketing weekly report generation")

    db = SessionLocal()
    try:
        agent = MarketingAgent(db)
        report = agent.generate_weekly_report(deliver=True)
        logger.info(f"Marketing weekly report generated successfully: {report.id}")
    except Exception as e:
        logger.error(f"Error in marketing weekly job: {e}")
    finally:
        db.close()


def marketing_monthly_job():
    """
    Scheduled job for generating monthly marketing reports.
    """
    logger.info("Starting scheduled marketing monthly report generation")

    db = SessionLocal()
    try:
        agent = MarketingAgent(db)
        report = agent.generate_monthly_report(deliver=True)
        logger.info(f"Marketing monthly report generated successfully: {report.id}")
    except Exception as e:
        logger.error(f"Error in marketing monthly job: {e}")
    finally:
        db.close()


def setup_scheduler():
    """
    Set up all scheduled jobs based on configuration.
    """
    logger.info("Setting up scheduled jobs")

    # Finance weekly report - runs based on cron expression from config
    scheduler.add_job(
        finance_weekly_job,
        trigger=CronTrigger.from_crontab(settings.finance_weekly_cron),
        id='finance_weekly',
        name='Finance Weekly Report',
        replace_existing=True
    )
    logger.info(f"Finance weekly job scheduled: {settings.finance_weekly_cron}")

    # Finance monthly report
    scheduler.add_job(
        finance_monthly_job,
        trigger=CronTrigger.from_crontab(settings.finance_monthly_cron),
        id='finance_monthly',
        name='Finance Monthly Report',
        replace_existing=True
    )
    logger.info(f"Finance monthly job scheduled: {settings.finance_monthly_cron}")

    # Marketing weekly report
    scheduler.add_job(
        marketing_weekly_job,
        trigger=CronTrigger.from_crontab(settings.marketing_weekly_cron),
        id='marketing_weekly',
        name='Marketing Weekly Report',
        replace_existing=True
    )
    logger.info(f"Marketing weekly job scheduled: {settings.marketing_weekly_cron}")

    # Marketing monthly report
    scheduler.add_job(
        marketing_monthly_job,
        trigger=CronTrigger.from_crontab(settings.marketing_monthly_cron),
        id='marketing_monthly',
        name='Marketing Monthly Report',
        replace_existing=True
    )
    logger.info(f"Marketing monthly job scheduled: {settings.marketing_monthly_cron}")


def start_scheduler():
    """
    Start the scheduler.
    """
    try:
        setup_scheduler()
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


def shutdown_scheduler():
    """
    Gracefully shutdown the scheduler.
    """
    try:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully")
    except Exception as e:
        logger.error(f"Error shutting down scheduler: {e}")


def get_scheduled_jobs():
    """
    Get information about all scheduled jobs.
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    return jobs
