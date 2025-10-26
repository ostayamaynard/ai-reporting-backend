"""
Marketing AI Agent

This module implements the Marketing AI Agent that automates marketing performance reporting.
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import logging

from ..models import MarketingReport, ReportType, ZohoSyncLog
from ..integrations.zoho import zoho_client
from ..services.visualization import VisualizationService
from ..services.delivery import email_service, slack_service
from ..services.ai import summarize_with_openai
from ..config import settings

logger = logging.getLogger(__name__)


class MarketingAgent:
    """
    AI Agent for automating marketing performance reports.
    """

    def __init__(self, db: Session):
        """
        Initialize the Marketing Agent.

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

    def _fetch_marketing_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Fetch marketing data from Zoho for the specified period.

        Args:
            start_date: Start of the period
            end_date: End of the period

        Returns:
            Dictionary containing all marketing data
        """
        logger.info(f"Fetching marketing data from {start_date} to {end_date}")

        # Create sync log
        sync_log = ZohoSyncLog(
            module_name="marketing",
            sync_type="data_fetch",
            status="in_progress"
        )
        self.db.add(sync_log)
        self.db.commit()

        try:
            # Fetch data from Zoho
            leads_data = self.zoho.get_leads_data(start_date, end_date)
            campaigns = self.zoho.get_campaign_performance(start_date, end_date)
            traffic_data = self.zoho.get_website_traffic(start_date, end_date)

            # Calculate metrics
            total_leads = leads_data["leads_count"]
            total_ad_spend = sum(c.get("spend", 0) for c in campaigns)
            total_clicks = sum(c.get("clicks", 0) for c in campaigns)
            total_conversions = sum(c.get("conversions", 0) for c in campaigns)

            # Calculate CTR (Click-Through Rate)
            total_impressions = sum(c.get("impressions", c.get("clicks", 0) * 100) for c in campaigns)
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

            # Calculate ROI (assuming revenue from conversions)
            # This is a simplified calculation - adjust based on actual business logic
            estimated_revenue = total_conversions * 100  # Assume $100 per conversion
            roi = self.zoho.calculate_marketing_roi(estimated_revenue, total_ad_spend)

            # Traffic growth calculation (compare to previous period)
            traffic_growth = 0  # Placeholder - would compare to previous period

            # Engagement rate (from website traffic)
            engagement_rate = traffic_data.get("engagement_rate", 0)

            # Organize channel performance
            channel_performance = {}
            leads_by_source = leads_data.get("leads_by_source", {})
            for source, count in leads_by_source.items():
                channel_performance[source] = {
                    "leads": count,
                    "conversions": 0  # Would need to track conversions by source
                }

            # Update sync log
            sync_log.status = "success"
            sync_log.records_fetched = (
                len(leads_data.get("leads", [])) +
                len(campaigns)
            )
            self.db.commit()

            return {
                "leads_generated": total_leads,
                "ad_spend": total_ad_spend,
                "ctr": round(ctr, 2),
                "roi": round(roi, 2),
                "traffic_growth": traffic_growth,
                "engagement_rate": engagement_rate,
                "top_campaigns": sorted(campaigns, key=lambda x: x.get("conversions", 0), reverse=True)[:10],
                "channel_performance": channel_performance,
                "leads_by_source": leads_by_source,
                "traffic_data": traffic_data,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions
            }

        except Exception as e:
            logger.error(f"Error fetching marketing data: {e}")
            sync_log.status = "failed"
            sync_log.error_message = str(e)
            self.db.commit()
            raise

    def _generate_ai_summary(self, marketing_data: Dict[str, Any], period_label: str) -> str:
        """
        Generate AI-powered summary of marketing data.

        Args:
            marketing_data: Marketing data dictionary
            period_label: Label for the reporting period

        Returns:
            AI-generated summary text
        """
        # Prepare data for AI analysis
        kpi_data = [
            {
                "kpi": "Leads Generated",
                "value": marketing_data["leads_generated"],
                "unit": "leads"
            },
            {
                "kpi": "Ad Spend",
                "value": marketing_data["ad_spend"],
                "unit": "$"
            },
            {
                "kpi": "CTR",
                "value": marketing_data["ctr"],
                "unit": "%"
            },
            {
                "kpi": "ROI",
                "value": marketing_data["roi"],
                "unit": "%"
            }
        ]

        anomalies = []
        if marketing_data["ctr"] < 1.0:
            anomalies.append({
                "kpi": "CTR",
                "note": "Low click-through rate - consider optimizing ad creatives"
            })

        if marketing_data["roi"] < 0:
            anomalies.append({
                "kpi": "ROI",
                "note": "Negative ROI - ad spend exceeds estimated revenue"
            })

        # Determine trends
        trend = {
            "ROI": "up" if marketing_data["roi"] > 0 else "down",
            "Leads": "up" if marketing_data["leads_generated"] > 0 else "flat"
        }

        # Generate summary using OpenAI
        prompt = f"""
You are a marketing analytics AI. Analyze the following marketing performance data for {period_label} and provide a concise executive summary.

Marketing Metrics:
- Leads Generated: {marketing_data['leads_generated']}
- Total Ad Spend: ${marketing_data['ad_spend']:,.2f}
- Click-Through Rate (CTR): {marketing_data['ctr']}%
- Return on Investment (ROI): {marketing_data['roi']}%
- Traffic Growth: {marketing_data['traffic_growth']}%
- Engagement Rate: {marketing_data['engagement_rate']}%

Top Campaigns:
{marketing_data.get('top_campaigns', [])}

Channel Performance:
{marketing_data.get('channel_performance', {})}

Anomalies:
{anomalies}

Please provide:
1. Overall marketing performance assessment (1-2 sentences)
2. Key highlights and areas of concern (3-5 bullet points)
3. Actionable recommendations to improve performance (2-3 bullet points)

Keep the summary under 250 words and use a professional, executive-friendly tone.
"""

        try:
            summary = summarize_with_openai(kpi_data, anomalies, trend)
            return summary
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            # Fallback summary
            return f"""
Marketing Performance Summary for {period_label}:

- Leads Generated: {marketing_data['leads_generated']}
- Total Ad Spend: ${marketing_data['ad_spend']:,.2f}
- Click-Through Rate: {marketing_data['ctr']}%
- ROI: {marketing_data['roi']}%
- Engagement Rate: {marketing_data['engagement_rate']}%

The marketing team generated {marketing_data['leads_generated']} leads during this period with a CTR of {marketing_data['ctr']}%.
ROI is {'positive' if marketing_data['roi'] > 0 else 'negative'} at {marketing_data['roi']}%.
{'Consider optimizing campaigns to improve ROI.' if marketing_data['roi'] < 50 else 'Marketing campaigns are performing well.'}
"""

    def _create_visualizations(
        self,
        marketing_data: Dict[str, Any],
        period_label: str,
        report_id: str
    ) -> str:
        """
        Create visualizations for the marketing report.

        Args:
            marketing_data: Marketing data
            period_label: Period label
            report_id: Report ID for file naming

        Returns:
            Path to visualizations directory
        """
        logger.info("Creating visualizations")

        try:
            # Marketing overview chart
            self.viz_service.create_marketing_overview_chart(
                leads=marketing_data["leads_generated"],
                ad_spend=float(marketing_data["ad_spend"]),
                roi=float(marketing_data["roi"]),
                period_label=period_label,
                filename=f"{report_id}_overview.html"
            )

            # Campaign performance chart
            if marketing_data.get("top_campaigns"):
                self.viz_service.create_campaign_performance_chart(
                    campaigns=marketing_data["top_campaigns"],
                    period_label=period_label,
                    filename=f"{report_id}_campaigns.html"
                )

            # Channel performance chart
            if marketing_data.get("channel_performance"):
                self.viz_service.create_channel_performance_chart(
                    channel_data=marketing_data["channel_performance"],
                    period_label=period_label,
                    filename=f"{report_id}_channels.html"
                )

            # CTR and engagement chart
            self.viz_service.create_ctr_engagement_chart(
                ctr=float(marketing_data["ctr"]),
                engagement_rate=float(marketing_data["engagement_rate"]),
                period_label=period_label,
                filename=f"{report_id}_metrics.html"
            )

            return settings.report_output_dir

        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return None

    def generate_weekly_report(self, deliver: bool = True) -> MarketingReport:
        """
        Generate a weekly marketing report.

        Args:
            deliver: Whether to deliver the report via email/Slack

        Returns:
            The generated MarketingReport
        """
        logger.info("Generating weekly marketing report")

        start_date, end_date = self._get_period_dates("weekly")
        period_label = f"Week of {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

        # Fetch data
        marketing_data = self._fetch_marketing_data(start_date, end_date)

        # Generate AI summary
        summary_text = self._generate_ai_summary(marketing_data, period_label)

        # Create report ID
        report_id = str(uuid.uuid4())

        # Create visualizations
        viz_path = self._create_visualizations(marketing_data, period_label, report_id)

        # Create report record
        report = MarketingReport(
            id=report_id,
            report_type=ReportType.marketing_weekly,
            period_start=start_date,
            period_end=end_date,
            leads_generated=marketing_data["leads_generated"],
            ad_spend=marketing_data["ad_spend"],
            ctr=marketing_data["ctr"],
            roi=marketing_data["roi"],
            traffic_growth=marketing_data["traffic_growth"],
            engagement_rate=marketing_data["engagement_rate"],
            top_campaigns_json=marketing_data["top_campaigns"],
            channel_performance_json=marketing_data["channel_performance"],
            metrics_json=marketing_data,
            summary_text=summary_text,
            visualizations_path=viz_path
        )

        self.db.add(report)
        self.db.commit()

        logger.info(f"Weekly marketing report generated: {report_id}")

        # Deliver report
        if deliver:
            self._deliver_report(report, period_label)

        return report

    def generate_monthly_report(self, deliver: bool = True) -> MarketingReport:
        """
        Generate a monthly marketing report.

        Args:
            deliver: Whether to deliver the report via email/Slack

        Returns:
            The generated MarketingReport
        """
        logger.info("Generating monthly marketing report")

        start_date, end_date = self._get_period_dates("monthly")
        period_label = f"{start_date.strftime('%B %Y')}"

        # Fetch data
        marketing_data = self._fetch_marketing_data(start_date, end_date)

        # Generate AI summary
        summary_text = self._generate_ai_summary(marketing_data, period_label)

        # Create report ID
        report_id = str(uuid.uuid4())

        # Create visualizations
        viz_path = self._create_visualizations(marketing_data, period_label, report_id)

        # Create report record
        report = MarketingReport(
            id=report_id,
            report_type=ReportType.marketing_monthly,
            period_start=start_date,
            period_end=end_date,
            leads_generated=marketing_data["leads_generated"],
            ad_spend=marketing_data["ad_spend"],
            ctr=marketing_data["ctr"],
            roi=marketing_data["roi"],
            traffic_growth=marketing_data["traffic_growth"],
            engagement_rate=marketing_data["engagement_rate"],
            top_campaigns_json=marketing_data["top_campaigns"],
            channel_performance_json=marketing_data["channel_performance"],
            metrics_json=marketing_data,
            summary_text=summary_text,
            visualizations_path=viz_path
        )

        self.db.add(report)
        self.db.commit()

        logger.info(f"Monthly marketing report generated: {report_id}")

        # Deliver report
        if deliver:
            self._deliver_report(report, period_label)

        return report

    def _deliver_report(self, report: MarketingReport, period_label: str):
        """
        Deliver the report via email and Slack.

        Args:
            report: The marketing report to deliver
            period_label: Label for the period
        """
        logger.info(f"Delivering marketing report {report.id}")

        report_data = {
            "leads_generated": report.leads_generated,
            "ad_spend": float(report.ad_spend) if report.ad_spend else 0,
            "ctr": float(report.ctr) if report.ctr else 0,
            "roi": float(report.roi) if report.roi else 0,
            "traffic_growth": float(report.traffic_growth) if report.traffic_growth else 0,
            "engagement_rate": float(report.engagement_rate) if report.engagement_rate else 0,
            "top_campaigns_json": report.top_campaigns_json or [],
            "channel_performance_json": report.channel_performance_json or {},
            "summary_text": report.summary_text or "No summary available."
        }

        # Send via email (configure recipients as needed)
        # email_service.send_marketing_report(
        #     to_emails=["marketing@company.com"],
        #     report_data=report_data,
        #     period_label=period_label
        # )

        # Send via Slack
        try:
            slack_service.send_marketing_report(
                report_data=report_data,
                period_label=period_label
            )
            report.delivered_at = datetime.now()
            self.db.commit()
        except Exception as e:
            logger.error(f"Error delivering report: {e}")
