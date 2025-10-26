"""
Report Delivery Service

This module handles the delivery of reports via Email and Slack.
"""

from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryService:
    """
    Service for delivering reports via email using SendGrid.
    """

    def __init__(self):
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.sendgrid_from_email
        self.client = None

        if self.api_key:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                self.client = SendGridAPIClient(self.api_key)
                self.Mail = Mail
            except ImportError:
                logger.warning("SendGrid not installed. Email delivery will not work.")
        else:
            logger.warning("SendGrid API key not configured. Email delivery disabled.")

    def send_report(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send a report via email.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            attachments: Optional list of attachments

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Email client not configured")
            return False

        try:
            message = self.Mail(
                from_email=self.from_email,
                to_emails=to_emails,
                subject=subject,
                html_content=html_content
            )

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    message.add_attachment(attachment)

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_emails}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_finance_report(
        self,
        to_emails: List[str],
        report_data: Dict[str, Any],
        period_label: str,
        visualizations: Optional[List[str]] = None
    ) -> bool:
        """
        Send a finance report via email.

        Args:
            to_emails: List of recipient emails
            report_data: Finance report data
            period_label: Period label (e.g., "Week of Jan 1-7, 2025")
            visualizations: Optional list of visualization file paths

        Returns:
            True if successful
        """
        subject = f"Finance Report - {period_label}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .metric {{ margin: 10px 0; padding: 15px; background-color: #ecf0f1; border-radius: 5px; }}
                .metric-label {{ font-weight: bold; color: #34495e; }}
                .metric-value {{ font-size: 24px; color: #27ae60; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 12px; text-align: left; }}
                th {{ background-color: #34495e; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Finance Report</h1>
                <p>{period_label}</p>
            </div>
            <div class="content">
                <h2>Executive Summary</h2>
                <div class="metric">
                    <div class="metric-label">Total Revenue</div>
                    <div class="metric-value positive">${report_data.get('revenue', 0):,.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Total Expenses</div>
                    <div class="metric-value negative">${report_data.get('expenses', 0):,.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Cash Flow</div>
                    <div class="metric-value {'positive' if report_data.get('cash_flow', 0) > 0 else 'negative'}">
                        ${report_data.get('cash_flow', 0):,.2f}
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Overdue Invoices</div>
                    <div class="metric-value negative">
                        {report_data.get('overdue_invoices_count', 0)} invoices
                        (${report_data.get('overdue_invoices_amount', 0):,.2f})
                    </div>
                </div>

                <h2>AI Insights</h2>
                <p>{report_data.get('summary_text', 'No summary available.')}</p>

                <h2>Top Clients</h2>
                <table>
                    <tr>
                        <th>Client Name</th>
                        <th>Revenue</th>
                        <th>Invoices</th>
                    </tr>
        """

        # Add top clients table rows
        top_clients = report_data.get('top_clients_json', [])
        for client in top_clients[:10]:
            html_content += f"""
                    <tr>
                        <td>{client.get('name', 'Unknown')}</td>
                        <td>${client.get('revenue', 0):,.2f}</td>
                        <td>{client.get('invoice_count', 0)}</td>
                    </tr>
            """

        html_content += """
                </table>
                <br>
                <p><em>This report was automatically generated by the Finance AI Agent.</em></p>
            </div>
        </body>
        </html>
        """

        return self.send_report(to_emails, subject, html_content)

    def send_marketing_report(
        self,
        to_emails: List[str],
        report_data: Dict[str, Any],
        period_label: str,
        visualizations: Optional[List[str]] = None
    ) -> bool:
        """
        Send a marketing report via email.

        Args:
            to_emails: List of recipient emails
            report_data: Marketing report data
            period_label: Period label
            visualizations: Optional list of visualization file paths

        Returns:
            True if successful
        """
        subject = f"Marketing Report - {period_label}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #3498db; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .metric {{ margin: 10px 0; padding: 15px; background-color: #ecf0f1; border-radius: 5px; }}
                .metric-label {{ font-weight: bold; color: #2c3e50; }}
                .metric-value {{ font-size: 24px; color: #3498db; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Marketing Report</h1>
                <p>{period_label}</p>
            </div>
            <div class="content">
                <h2>Performance Metrics</h2>
                <div class="metric">
                    <div class="metric-label">Leads Generated</div>
                    <div class="metric-value">{report_data.get('leads_generated', 0):,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Total Ad Spend</div>
                    <div class="metric-value">${report_data.get('ad_spend', 0):,.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Click-Through Rate (CTR)</div>
                    <div class="metric-value">{report_data.get('ctr', 0):.2f}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Return on Investment (ROI)</div>
                    <div class="metric-value">{report_data.get('roi', 0):.2f}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Traffic Growth</div>
                    <div class="metric-value">{report_data.get('traffic_growth', 0):.2f}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Engagement Rate</div>
                    <div class="metric-value">{report_data.get('engagement_rate', 0):.2f}%</div>
                </div>

                <h2>AI Insights</h2>
                <p>{report_data.get('summary_text', 'No summary available.')}</p>

                <h2>Top Campaigns</h2>
                <table>
                    <tr>
                        <th>Campaign Name</th>
                        <th>Clicks</th>
                        <th>Conversions</th>
                        <th>Spend</th>
                    </tr>
        """

        # Add top campaigns table rows
        top_campaigns = report_data.get('top_campaigns_json', [])
        for campaign in top_campaigns[:10]:
            html_content += f"""
                    <tr>
                        <td>{campaign.get('name', 'Unknown')}</td>
                        <td>{campaign.get('clicks', 0):,}</td>
                        <td>{campaign.get('conversions', 0):,}</td>
                        <td>${campaign.get('spend', 0):,.2f}</td>
                    </tr>
            """

        html_content += """
                </table>
                <br>
                <p><em>This report was automatically generated by the Marketing AI Agent.</em></p>
            </div>
        </body>
        </html>
        """

        return self.send_report(to_emails, subject, html_content)


class SlackDeliveryService:
    """
    Service for delivering reports via Slack.
    """

    def __init__(self):
        self.bot_token = settings.slack_bot_token
        self.finance_channel = settings.slack_channel_finance
        self.marketing_channel = settings.slack_channel_marketing
        self.client = None

        if self.bot_token:
            try:
                from slack_sdk import WebClient
                self.client = WebClient(token=self.bot_token)
            except ImportError:
                logger.warning("Slack SDK not installed. Slack delivery will not work.")
        else:
            logger.warning("Slack bot token not configured. Slack delivery disabled.")

    def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send a message to a Slack channel.

        Args:
            channel: Slack channel name or ID
            text: Plain text message
            blocks: Optional rich message blocks

        Returns:
            True if successful
        """
        if not self.client:
            logger.error("Slack client not configured")
            return False

        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response["ok"]
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False

    def send_finance_report(
        self,
        report_data: Dict[str, Any],
        period_label: str,
        channel: Optional[str] = None
    ) -> bool:
        """
        Send a finance report to Slack.

        Args:
            report_data: Finance report data
            period_label: Period label
            channel: Optional channel override

        Returns:
            True if successful
        """
        target_channel = channel or self.finance_channel

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Finance Report - {period_label}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Revenue:*\n${report_data.get('revenue', 0):,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Expenses:*\n${report_data.get('expenses', 0):,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Cash Flow:*\n${report_data.get('cash_flow', 0):,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Overdue Invoices:*\n{report_data.get('overdue_invoices_count', 0)} (${report_data.get('overdue_invoices_amount', 0):,.2f})"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*AI Insights:*\n{report_data.get('summary_text', 'No summary available.')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Automatically generated by Finance AI Agent_"
                    }
                ]
            }
        ]

        text = f"Finance Report - {period_label}"
        return self.send_message(target_channel, text, blocks)

    def send_marketing_report(
        self,
        report_data: Dict[str, Any],
        period_label: str,
        channel: Optional[str] = None
    ) -> bool:
        """
        Send a marketing report to Slack.

        Args:
            report_data: Marketing report data
            period_label: Period label
            channel: Optional channel override

        Returns:
            True if successful
        """
        target_channel = channel or self.marketing_channel

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Marketing Report - {period_label}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Leads Generated:*\n{report_data.get('leads_generated', 0):,}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Ad Spend:*\n${report_data.get('ad_spend', 0):,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*CTR:*\n{report_data.get('ctr', 0):.2f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*ROI:*\n{report_data.get('roi', 0):.2f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Traffic Growth:*\n{report_data.get('traffic_growth', 0):.2f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Engagement Rate:*\n{report_data.get('engagement_rate', 0):.2f}%"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*AI Insights:*\n{report_data.get('summary_text', 'No summary available.')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Automatically generated by Marketing AI Agent_"
                    }
                ]
            }
        ]

        text = f"Marketing Report - {period_label}"
        return self.send_message(target_channel, text, blocks)


# Singleton instances
email_service = EmailDeliveryService()
slack_service = SlackDeliveryService()
