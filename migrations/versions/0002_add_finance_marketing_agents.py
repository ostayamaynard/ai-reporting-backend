"""Add finance and marketing agent models

Revision ID: 0002
Revises: 0001
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    op.execute("""
        CREATE TYPE reporttype AS ENUM (
            'finance_weekly',
            'finance_monthly',
            'marketing_weekly',
            'marketing_monthly'
        )
    """)

    # Create finance_reports table
    op.create_table(
        'finance_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('report_type', sa.Enum('finance_weekly', 'finance_monthly', 'marketing_weekly', 'marketing_monthly', name='reporttype'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('revenue', sa.Numeric(18, 2), nullable=True),
        sa.Column('expenses', sa.Numeric(18, 2), nullable=True),
        sa.Column('cash_flow', sa.Numeric(18, 2), nullable=True),
        sa.Column('overdue_invoices_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('overdue_invoices_amount', sa.Numeric(18, 2), nullable=True, server_default='0'),
        sa.Column('top_clients_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('summary_text', sa.Text(), nullable=True),
        sa.Column('visualizations_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create marketing_reports table
    op.create_table(
        'marketing_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('report_type', sa.Enum('finance_weekly', 'finance_monthly', 'marketing_weekly', 'marketing_monthly', name='reporttype'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('leads_generated', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('ad_spend', sa.Numeric(18, 2), nullable=True, server_default='0'),
        sa.Column('ctr', sa.Numeric(5, 2), nullable=True),
        sa.Column('roi', sa.Numeric(10, 2), nullable=True),
        sa.Column('traffic_growth', sa.Numeric(10, 2), nullable=True),
        sa.Column('engagement_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('top_campaigns_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('channel_performance_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('summary_text', sa.Text(), nullable=True),
        sa.Column('visualizations_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create zoho_sync_logs table
    op.create_table(
        'zoho_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(), nullable=False),
        sa.Column('sync_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('records_fetched', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create report_deliveries table
    op.create_table(
        'report_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(), nullable=False),
        sa.Column('report_table', sa.String(), nullable=False),
        sa.Column('delivery_method', sa.String(), nullable=False),
        sa.Column('recipients', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_finance_reports_period', 'finance_reports', ['period_start', 'period_end'])
    op.create_index('ix_finance_reports_type', 'finance_reports', ['report_type'])
    op.create_index('ix_marketing_reports_period', 'marketing_reports', ['period_start', 'period_end'])
    op.create_index('ix_marketing_reports_type', 'marketing_reports', ['report_type'])
    op.create_index('ix_zoho_sync_logs_module', 'zoho_sync_logs', ['module_name'])
    op.create_index('ix_report_deliveries_report', 'report_deliveries', ['report_id', 'report_table'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_report_deliveries_report', table_name='report_deliveries')
    op.drop_index('ix_zoho_sync_logs_module', table_name='zoho_sync_logs')
    op.drop_index('ix_marketing_reports_type', table_name='marketing_reports')
    op.drop_index('ix_marketing_reports_period', table_name='marketing_reports')
    op.drop_index('ix_finance_reports_type', table_name='finance_reports')
    op.drop_index('ix_finance_reports_period', table_name='finance_reports')

    # Drop tables
    op.drop_table('report_deliveries')
    op.drop_table('zoho_sync_logs')
    op.drop_table('marketing_reports')
    op.drop_table('finance_reports')

    # Drop enum type
    op.execute('DROP TYPE reporttype')
