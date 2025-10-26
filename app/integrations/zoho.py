"""
Zoho API Integration Service

This module handles all interactions with Zoho APIs for Finance and Marketing data.
"""

import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class ZohoClient:
    """
    Client for interacting with Zoho APIs.
    Handles authentication and data retrieval from Zoho Books (Finance) and Zoho Marketing Hub.
    """

    def __init__(self):
        self.base_url = settings.zoho_base_url
        self.client_id = settings.zoho_client_id
        self.client_secret = settings.zoho_client_secret
        self.refresh_token = settings.zoho_refresh_token
        self.org_id = settings.zoho_org_id
        self.access_token = None
        self.token_expiry = None

    def _get_access_token(self) -> str:
        """
        Get or refresh the Zoho access token.
        """
        # Check if we have a valid token
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        # Refresh the token
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            # Tokens typically expire in 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600) - 60)

            return self.access_token
        except Exception as e:
            logger.error(f"Failed to refresh Zoho access token: {e}")
            raise

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     json_data: Optional[Dict] = None) -> Dict:
        """
        Make an authenticated request to Zoho API.
        """
        token = self._get_access_token()
        headers = {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Zoho API request failed: {e}")
            raise

    # Finance Data Methods (Zoho Books)

    def get_revenue_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get revenue data from Zoho Books for the specified period.
        """
        params = {
            "organization_id": self.org_id,
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d")
        }

        # Get invoices
        invoices = self._make_request("GET", "/books/v3/invoices", params=params)

        total_revenue = 0
        invoice_count = 0

        if invoices.get("invoices"):
            for invoice in invoices["invoices"]:
                if invoice.get("status") == "paid":
                    total_revenue += float(invoice.get("total", 0))
                    invoice_count += 1

        return {
            "total_revenue": total_revenue,
            "invoice_count": invoice_count,
            "invoices": invoices.get("invoices", [])
        }

    def get_expenses_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get expenses data from Zoho Books for the specified period.
        """
        params = {
            "organization_id": self.org_id,
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d")
        }

        # Get bills/expenses
        expenses = self._make_request("GET", "/books/v3/bills", params=params)

        total_expenses = 0
        expense_count = 0

        if expenses.get("bills"):
            for bill in expenses["bills"]:
                total_expenses += float(bill.get("total", 0))
                expense_count += 1

        return {
            "total_expenses": total_expenses,
            "expense_count": expense_count,
            "expenses": expenses.get("bills", [])
        }

    def get_cash_flow_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Calculate cash flow from revenue and expenses.
        """
        revenue_data = self.get_revenue_data(start_date, end_date)
        expenses_data = self.get_expenses_data(start_date, end_date)

        cash_flow = revenue_data["total_revenue"] - expenses_data["total_expenses"]

        return {
            "cash_flow": cash_flow,
            "revenue": revenue_data["total_revenue"],
            "expenses": expenses_data["total_expenses"]
        }

    def get_overdue_invoices(self) -> Dict[str, Any]:
        """
        Get overdue invoices from Zoho Books.
        """
        params = {
            "organization_id": self.org_id,
            "status": "overdue"
        }

        invoices = self._make_request("GET", "/books/v3/invoices", params=params)

        overdue_count = 0
        overdue_amount = 0

        if invoices.get("invoices"):
            overdue_count = len(invoices["invoices"])
            for invoice in invoices["invoices"]:
                overdue_amount += float(invoice.get("balance", 0))

        return {
            "overdue_count": overdue_count,
            "overdue_amount": overdue_amount,
            "invoices": invoices.get("invoices", [])
        }

    def get_top_clients(self, start_date: date, end_date: date, limit: int = 10) -> List[Dict]:
        """
        Get top clients by revenue for the specified period.
        """
        revenue_data = self.get_revenue_data(start_date, end_date)

        # Aggregate by customer
        client_revenue = {}
        for invoice in revenue_data.get("invoices", []):
            if invoice.get("status") == "paid":
                customer_name = invoice.get("customer_name", "Unknown")
                customer_id = invoice.get("customer_id")
                amount = float(invoice.get("total", 0))

                if customer_id not in client_revenue:
                    client_revenue[customer_id] = {
                        "name": customer_name,
                        "revenue": 0,
                        "invoice_count": 0
                    }

                client_revenue[customer_id]["revenue"] += amount
                client_revenue[customer_id]["invoice_count"] += 1

        # Sort and get top clients
        top_clients = sorted(
            client_revenue.values(),
            key=lambda x: x["revenue"],
            reverse=True
        )[:limit]

        return top_clients

    # Marketing Data Methods (Zoho Marketing Hub / CRM)

    def get_leads_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get leads data from Zoho CRM for the specified period.
        """
        params = {
            "created_time": f"{start_date.isoformat()}T00:00:00+00:00,{end_date.isoformat()}T23:59:59+00:00"
        }

        leads = self._make_request("GET", "/crm/v3/Leads", params=params)

        leads_count = 0
        leads_by_source = {}

        if leads.get("data"):
            leads_count = len(leads["data"])
            for lead in leads["data"]:
                source = lead.get("Lead_Source", "Unknown")
                leads_by_source[source] = leads_by_source.get(source, 0) + 1

        return {
            "leads_count": leads_count,
            "leads_by_source": leads_by_source,
            "leads": leads.get("data", [])
        }

    def get_campaign_performance(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Get marketing campaign performance data.
        Note: This is a simplified version. Actual implementation depends on Zoho Marketing Hub setup.
        """
        # This would connect to Zoho Campaigns or Marketing Hub
        # For now, returning a placeholder structure
        campaigns = []

        try:
            # Example: Get campaigns from Zoho Campaigns API
            params = {
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d")
            }

            # Note: Adjust endpoint based on actual Zoho setup
            response = self._make_request("GET", "/campaigns/v1/campaigns", params=params)

            if response.get("data"):
                for campaign in response["data"]:
                    campaigns.append({
                        "name": campaign.get("name"),
                        "clicks": campaign.get("clicks", 0),
                        "opens": campaign.get("opens", 0),
                        "conversions": campaign.get("conversions", 0),
                        "spend": campaign.get("spend", 0),
                        "ctr": campaign.get("ctr", 0)
                    })
        except Exception as e:
            logger.warning(f"Failed to fetch campaign data: {e}")
            # Return mock data if API not configured
            pass

        return campaigns

    def get_website_traffic(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get website traffic data from Zoho Analytics or similar.
        """
        # This would integrate with Zoho Analytics or Google Analytics via Zoho
        # Placeholder implementation
        return {
            "total_visits": 0,
            "unique_visitors": 0,
            "page_views": 0,
            "bounce_rate": 0,
            "avg_session_duration": 0
        }

    def calculate_marketing_roi(self, revenue: float, ad_spend: float) -> float:
        """
        Calculate marketing ROI.
        """
        if ad_spend == 0:
            return 0

        roi = ((revenue - ad_spend) / ad_spend) * 100
        return round(roi, 2)


# Singleton instance
zoho_client = ZohoClient()
