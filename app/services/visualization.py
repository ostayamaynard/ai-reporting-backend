"""
Data Visualization Service

This module handles the generation of charts, graphs, and visualizations
for Finance and Marketing reports.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import os
from datetime import date
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class VisualizationService:
    """
    Service for creating visualizations for reports.
    """

    def __init__(self, output_dir: str):
        """
        Initialize the visualization service.

        Args:
            output_dir: Directory where visualizations will be saved
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # Finance Visualizations

    def create_finance_summary_chart(
        self,
        revenue: float,
        expenses: float,
        cash_flow: float,
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a finance summary chart showing revenue, expenses, and cash flow.

        Returns:
            Path to the saved chart
        """
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Revenue',
            x=['Finance Summary'],
            y=[revenue],
            marker_color='green',
            text=[f'${revenue:,.2f}'],
            textposition='auto'
        ))

        fig.add_trace(go.Bar(
            name='Expenses',
            x=['Finance Summary'],
            y=[expenses],
            marker_color='red',
            text=[f'${expenses:,.2f}'],
            textposition='auto'
        ))

        fig.add_trace(go.Bar(
            name='Cash Flow',
            x=['Finance Summary'],
            y=[cash_flow],
            marker_color='blue' if cash_flow > 0 else 'orange',
            text=[f'${cash_flow:,.2f}'],
            textposition='auto'
        ))

        fig.update_layout(
            title=f'Financial Summary - {period_label}',
            barmode='group',
            yaxis_title='Amount ($)',
            showlegend=True,
            template='plotly_white'
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_top_clients_chart(
        self,
        top_clients: List[Dict],
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a chart showing top clients by revenue.

        Returns:
            Path to the saved chart
        """
        if not top_clients:
            return None

        df = pd.DataFrame(top_clients)

        fig = px.bar(
            df,
            x='name',
            y='revenue',
            title=f'Top Clients by Revenue - {period_label}',
            labels={'name': 'Client', 'revenue': 'Revenue ($)'},
            text='revenue',
            color='revenue',
            color_continuous_scale='Blues'
        )

        fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
        fig.update_layout(
            showlegend=False,
            template='plotly_white',
            xaxis_tickangle=-45
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_revenue_trend_chart(
        self,
        revenue_data: List[Dict],
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a line chart showing revenue trends over time.

        Args:
            revenue_data: List of dicts with 'date' and 'amount' keys

        Returns:
            Path to the saved chart
        """
        if not revenue_data:
            return None

        df = pd.DataFrame(revenue_data)
        df['date'] = pd.to_datetime(df['date'])

        fig = px.line(
            df,
            x='date',
            y='amount',
            title=f'Revenue Trend - {period_label}',
            labels={'date': 'Date', 'amount': 'Revenue ($)'},
            markers=True
        )

        fig.update_layout(
            template='plotly_white',
            hovermode='x unified'
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_expense_breakdown_chart(
        self,
        expense_categories: Dict[str, float],
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a pie chart showing expense breakdown by category.

        Returns:
            Path to the saved chart
        """
        if not expense_categories:
            return None

        labels = list(expense_categories.keys())
        values = list(expense_categories.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo='label+percent',
            hovertemplate='%{label}<br>$%{value:,.2f}<br>%{percent}<extra></extra>'
        )])

        fig.update_layout(
            title=f'Expense Breakdown - {period_label}',
            template='plotly_white'
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    # Marketing Visualizations

    def create_marketing_overview_chart(
        self,
        leads: int,
        ad_spend: float,
        roi: float,
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a marketing overview chart.

        Returns:
            Path to the saved chart
        """
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Leads Generated', 'Ad Spend', 'ROI'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
        )

        fig.add_trace(go.Indicator(
            mode="number",
            value=leads,
            title={"text": "Leads"},
            number={'font': {'size': 40}}
        ), row=1, col=1)

        fig.add_trace(go.Indicator(
            mode="number",
            value=ad_spend,
            title={"text": "Ad Spend"},
            number={'prefix': "$", 'font': {'size': 40}}
        ), row=1, col=2)

        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=roi,
            title={"text": "ROI"},
            number={'suffix': "%", 'font': {'size': 40}},
            delta={'reference': 100}
        ), row=1, col=3)

        fig.update_layout(
            title_text=f'Marketing Overview - {period_label}',
            template='plotly_white',
            height=300
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_campaign_performance_chart(
        self,
        campaigns: List[Dict],
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a chart showing campaign performance.

        Args:
            campaigns: List of dicts with campaign metrics

        Returns:
            Path to the saved chart
        """
        if not campaigns:
            return None

        df = pd.DataFrame(campaigns)

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Campaign Clicks', 'Campaign Conversions'),
            vertical_spacing=0.15
        )

        fig.add_trace(go.Bar(
            x=df['name'],
            y=df['clicks'],
            name='Clicks',
            marker_color='lightblue'
        ), row=1, col=1)

        fig.add_trace(go.Bar(
            x=df['name'],
            y=df['conversions'],
            name='Conversions',
            marker_color='green'
        ), row=2, col=1)

        fig.update_layout(
            title_text=f'Campaign Performance - {period_label}',
            showlegend=True,
            template='plotly_white',
            height=600
        )

        fig.update_xaxes(tickangle=-45)

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_channel_performance_chart(
        self,
        channel_data: Dict[str, Dict],
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a chart showing performance by marketing channel.

        Args:
            channel_data: Dict with channel names as keys and metrics as values

        Returns:
            Path to the saved chart
        """
        if not channel_data:
            return None

        channels = list(channel_data.keys())
        leads = [channel_data[ch].get('leads', 0) for ch in channels]
        conversions = [channel_data[ch].get('conversions', 0) for ch in channels]

        fig = go.Figure(data=[
            go.Bar(name='Leads', x=channels, y=leads, marker_color='lightblue'),
            go.Bar(name='Conversions', x=channels, y=conversions, marker_color='green')
        ])

        fig.update_layout(
            title=f'Channel Performance - {period_label}',
            barmode='group',
            xaxis_title='Channel',
            yaxis_title='Count',
            template='plotly_white'
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_traffic_growth_chart(
        self,
        traffic_data: List[Dict],
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a chart showing website traffic growth.

        Args:
            traffic_data: List of dicts with 'date' and 'visits' keys

        Returns:
            Path to the saved chart
        """
        if not traffic_data:
            return None

        df = pd.DataFrame(traffic_data)
        df['date'] = pd.to_datetime(df['date'])

        fig = px.area(
            df,
            x='date',
            y='visits',
            title=f'Website Traffic Growth - {period_label}',
            labels={'date': 'Date', 'visits': 'Visits'},
            color_discrete_sequence=['#636EFA']
        )

        fig.update_layout(
            template='plotly_white',
            hovermode='x unified'
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_ctr_engagement_chart(
        self,
        ctr: float,
        engagement_rate: float,
        period_label: str,
        filename: str
    ) -> str:
        """
        Create a gauge chart for CTR and engagement rate.

        Returns:
            Path to the saved chart
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Click-Through Rate', 'Engagement Rate'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}]]
        )

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=ctr,
            title={'text': "CTR (%)"},
            gauge={'axis': {'range': [None, 10]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 2], 'color': "lightgray"},
                       {'range': [2, 5], 'color': "lightblue"},
                       {'range': [5, 10], 'color': "blue"}
                   ],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 5}
                  }
        ), row=1, col=1)

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=engagement_rate,
            title={'text': "Engagement (%)"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkgreen"},
                   'steps': [
                       {'range': [0, 30], 'color': "lightgray"},
                       {'range': [30, 60], 'color': "lightgreen"},
                       {'range': [60, 100], 'color': "green"}
                   ],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}
                  }
        ), row=1, col=2)

        fig.update_layout(
            title_text=f'CTR and Engagement Metrics - {period_label}',
            template='plotly_white',
            height=400
        )

        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_combined_report_pdf(
        self,
        visualizations: List[str],
        output_filename: str
    ) -> str:
        """
        Combine multiple visualizations into a single PDF report.

        Args:
            visualizations: List of paths to visualization files
            output_filename: Name of the output PDF file

        Returns:
            Path to the generated PDF
        """
        # This would use a library like reportlab or weasyprint
        # For now, we'll just return the list of visualizations
        # Implementation can be extended based on requirements
        pass
