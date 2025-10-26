"""
Finance AI Agent

This module implements the Finance AI Agent that automates financial reporting.
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import logging

from ..models import FinanceReport, ReportType, ZohoSyncLog
from ..integrations.zoho import zoho_client
from ..services.visualization import VisualizationService
from ..services.delivery import email_service, slack_service
from ..services.ai import summarize_with_openai
from ..config import settings

logger = logging.getLogger(__name__)


class FinanceAgent:
    """
    AI Agent for automating financial reports.
    """

    def __init__(self, db: Session):
        """
        Initialize the Finance Agent.

        Args:
            db: Database session
        """
        self.db = db
        self.zoho = zoho_client
        self.viz_service = VisualizationService(settings.report_output_dir)

    def _get_period_dates(self, report_type: str) -> tuple[date, date]:
        """
        Get the start and end dates for a report period.

        Args:
            report_type: "weekly" or "monthly"

        Returns:
            Tuple of (start_date, end_date)
        """
        today = date.today()

        if report_type == "weekly":
            # Last 7 days
            end_date = today - timedelta(days=1)  # Yesterday
            start_date = end_date - timedelta(days=6)  # 7 days ago
        elif report_type == "monthly":
            # Last month
            if today.month == 1:
                start_date = date(today.year - 1, 12, 1)
            else:
                start_date = date(today.year, today.month - 1, 1)

            # Last day of previous month
            end_date = start_date.replace(day=28) + timedelta(days=4)
            end_date = end_date - timedelta(days=end_date.day)
        else:
            raise ValueError(f"Invalid report type: {report_type}")

        return start_date, end_date

    def _fetch_financial_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Fetch financial data from Zoho for the specified period.

        Args:
            start_date: Start of the period
            end_date: End of the period

        Returns:
            Dictionary containing all financial data
        """
        logger.info(f"Fetching financial data from {start_date} to {end_date}")

        # Create sync log
        sync_log = ZohoSyncLog(
            module_name="finance",
            sync_type="data_fetch",
            status="in_progress"
        )
        self.db.add(sync_log)
        self.db.commit()

        try:
            # Fetch data from Zoho
            revenue_data = self.zoho.get_revenue_data(start_date, end_date)
            expenses_data = self.zoho.get_expenses_data(start_date, end_date)
            cash_flow_data = self.zoho.get_cash_flow_data(start_date, end_date)
            overdue_data = self.zoho.get_overdue_invoices()
            top_clients = self.zoho.get_top_clients(start_date, end_date, limit=10)

            # Update sync log
            sync_log.status = "success"
            sync_log.records_fetched = (
                len(revenue_data.get("invoices", [])) +
                len(expenses_data.get("expenses", [])) +
                len(overdue_data.get("invoices", []))
            )
            self.db.commit()

            return {
                "revenue": revenue_data["total_revenue"],
                "expenses": expenses_data["total_expenses"],
                "cash_flow": cash_flow_data["cash_flow"],
                "overdue_invoices_count": overdue_data["overdue_count"],
                "overdue_invoices_amount": overdue_data["overdue_amount"],
                "top_clients": top_clients,
                "revenue_details": revenue_data,
                "expense_details": expenses_data
            }

        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
            sync_log.status = "failed"
            sync_log.error_message = str(e)
            self.db.commit()
            raise

    def _generate_ai_summary(self, financial_data: Dict[str, Any], period_label: str) -> str:
        """
        Generate AI-powered summary of financial data.

        Args:
            financial_data: Financial data dictionary
            period_label: Label for the reporting period

        Returns:
            AI-generated summary text
        """
        # Prepare data for AI analysis
        kpi_data = [
            {
                "kpi": "Revenue",
                "value": financial_data["revenue"],
                "unit": "$"
            },
            {
                "kpi": "Expenses",
                "value": financial_data["expenses"],
                "unit": "$"
            },
            {
                "kpi": "Cash Flow",
                "value": financial_data["cash_flow"],
                "unit": "$"
            },
            {
                "kpi": "Overdue Invoices",
                "value": financial_data["overdue_invoices_amount"],
                "count": financial_data["overdue_invoices_count"],
                "unit": "$"
            }
        ]

        anomalies = []
        if financial_data["cash_flow"] < 0:
            anomalies.append({
                "kpi": "Cash Flow",
                "note": "Negative cash flow detected - expenses exceed revenue"
            })

        if financial_data["overdue_invoices_count"] > 5:
            anomalies.append({
                "kpi": "Overdue Invoices",
                "note": f"High number of overdue invoices: {financial_data['overdue_invoices_count']}"
            })

        # Determine trends
        trend = {
            "Cash Flow": "up" if financial_data["cash_flow"] > 0 else "down"
        }

        # Generate summary using OpenAI
        prompt = f"""
You are a financial analyst AI. Analyze the following financial data for {period_label} and provide a concise executive summary.

Financial Metrics:
- Revenue: ${financial_data['revenue']:,.2f}
- Expenses: ${financial_data['expenses']:,.2f}
- Cash Flow: ${financial_data['cash_flow']:,.2f}
- Overdue Invoices: {financial_data['overdue_invoices_count']} invoices totaling ${financial_data['overdue_invoices_amount']:,.2f}

Top Clients:
{financial_data.get('top_clients', [])}

Anomalies:
{anomalies}

Please provide:
1. Overall financial health assessment (1-2 sentences)
2. Key highlights and concerns (3-5 bullet points)
3. Actionable recommendations (2-3 bullet points)

Keep the summary under 250 words and use a professional, executive-friendly tone.
"""

        try:
            summary = summarize_with_openai(kpi_data, anomalies, trend)
            return summary
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            # Fallback summary
            return f"""
Financial Summary for {period_label}:

- Total Revenue: ${financial_data['revenue']:,.2f}
- Total Expenses: ${financial_data['expenses']:,.2f}
- Net Cash Flow: ${financial_data['cash_flow']:,.2f}
- Overdue Invoices: {financial_data['overdue_invoices_count']} invoices (${financial_data['overdue_invoices_amount']:,.2f})

The business generated ${financial_data['revenue']:,.2f} in revenue during this period.
Cash flow is {'positive' if financial_data['cash_flow'] > 0 else 'negative'} at ${financial_data['cash_flow']:,.2f}.
{'Action needed to collect overdue payments.' if financial_data['overdue_invoices_count'] > 0 else 'No overdue invoices.'}
"""

    def _create_visualizations(
        self,
        financial_data: Dict[str, Any],
        period_label: str,
        report_id: str
    ) -> str:
        """
        Create visualizations for the financial report.

        Args:
            financial_data: Financial data
            period_label: Period label
            report_id: Report ID for file naming

        Returns:
            Path to visualizations directory
        """
        logger.info("Creating visualizations")

        try:
            # Finance summary chart
            self.viz_service.create_finance_summary_chart(
                revenue=float(financial_data["revenue"]),
                expenses=float(financial_data["expenses"]),
                cash_flow=float(financial_data["cash_flow"]),
                period_label=period_label,
                filename=f"{report_id}_summary.html"
            )

            # Top clients chart
            if financial_data.get("top_clients"):
                self.viz_service.create_top_clients_chart(
                    top_clients=financial_data["top_clients"],
                    period_label=period_label,
                    filename=f"{report_id}_top_clients.html"
                )

            return settings.report_output_dir

        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return None

    def generate_weekly_report(self, deliver: bool = True) -> FinanceReport:
        """
        Generate a weekly financial report.

        Args:
            deliver: Whether to deliver the report via email/Slack

        Returns:
            The generated FinanceReport
        """
        logger.info("Generating weekly finance report")

        start_date, end_date = self._get_period_dates("weekly")
        period_label = f"Week of {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

        # Fetch data
        financial_data = self._fetch_financial_data(start_date, end_date)

        # Generate AI summary
        summary_text = self._generate_ai_summary(financial_data, period_label)

        # Create report ID
        report_id = str(uuid.uuid4())

        # Create visualizations
        viz_path = self._create_visualizations(financial_data, period_label, report_id)

        # Create report record
        report = FinanceReport(
            id=report_id,
            report_type=ReportType.finance_weekly,
            period_start=start_date,
            period_end=end_date,
            revenue=financial_data["revenue"],
            expenses=financial_data["expenses"],
            cash_flow=financial_data["cash_flow"],
            overdue_invoices_count=financial_data["overdue_invoices_count"],
            overdue_invoices_amount=financial_data["overdue_invoices_amount"],
            top_clients_json=financial_data["top_clients"],
            metrics_json=financial_data,
            summary_text=summary_text,
            visualizations_path=viz_path
        )

        self.db.add(report)
        self.db.commit()

        logger.info(f"Weekly finance report generated: {report_id}")

        # Deliver report
        if deliver:
            self._deliver_report(report, period_label)

        return report

    def generate_monthly_report(self, deliver: bool = True) -> FinanceReport:
        """
        Generate a monthly financial report.

        Args:
            deliver: Whether to deliver the report via email/Slack

        Returns:
            The generated FinanceReport
        """
        logger.info("Generating monthly finance report")

        start_date, end_date = self._get_period_dates("monthly")
        period_label = f"{start_date.strftime('%B %Y')}"

        # Fetch data
        financial_data = self._fetch_financial_data(start_date, end_date)

        # Generate AI summary
        summary_text = self._generate_ai_summary(financial_data, period_label)

        # Create report ID
        report_id = str(uuid.uuid4())

        # Create visualizations
        viz_path = self._create_visualizations(financial_data, period_label, report_id)

        # Create report record
        report = FinanceReport(
            id=report_id,
            report_type=ReportType.finance_monthly,
            period_start=start_date,
            period_end=end_date,
            revenue=financial_data["revenue"],
            expenses=financial_data["expenses"],
            cash_flow=financial_data["cash_flow"],
            overdue_invoices_count=financial_data["overdue_invoices_count"],
            overdue_invoices_amount=financial_data["overdue_invoices_amount"],
            top_clients_json=financial_data["top_clients"],
            metrics_json=financial_data,
            summary_text=summary_text,
            visualizations_path=viz_path
        )

        self.db.add(report)
        self.db.commit()

        logger.info(f"Monthly finance report generated: {report_id}")

        # Deliver report
        if deliver:
            self._deliver_report(report, period_label)

        return report

    def _deliver_report(self, report: FinanceReport, period_label: str):
        """
        Deliver the report via email and Slack.

        Args:
            report: The finance report to deliver
            period_label: Label for the period
        """
        logger.info(f"Delivering finance report {report.id}")

        report_data = {
            "revenue": float(report.revenue) if report.revenue else 0,
            "expenses": float(report.expenses) if report.expenses else 0,
            "cash_flow": float(report.cash_flow) if report.cash_flow else 0,
            "overdue_invoices_count": report.overdue_invoices_count,
            "overdue_invoices_amount": float(report.overdue_invoices_amount) if report.overdue_invoices_amount else 0,
            "top_clients_json": report.top_clients_json or [],
            "summary_text": report.summary_text or "No summary available."
        }

        # Send via email (configure recipients as needed)
        # email_service.send_finance_report(
        #     to_emails=["finance@company.com"],
        #     report_data=report_data,
        #     period_label=period_label
        # )

        # Send via Slack
        try:
            slack_service.send_finance_report(
                report_data=report_data,
                period_label=period_label
            )
            report.delivered_at = datetime.now()
            self.db.commit()
        except Exception as e:
            logger.error(f"Error delivering report: {e}")
