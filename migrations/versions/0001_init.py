from alembic import op
import sqlalchemy as sa
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('kpis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('aggregation', sa.Enum('sum','avg', name='aggregation'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kpi_id', sa.Integer(), nullable=False),
        sa.Column('period_type', sa.String(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('target_value', sa.Numeric(18,6), nullable=False),
        sa.ForeignKeyConstraint(['kpi_id'], ['kpis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('file_uri', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('report_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(), nullable=False),
        sa.Column('kpi_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Numeric(18,6), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['kpi_id'], ['kpis.id'], ),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(), nullable=False),
        sa.Column('goal_period', sa.String(), nullable=False),
        sa.Column('summary_md', sa.String(), nullable=True),
        sa.Column('comparisons_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('analyses')
    op.drop_table('report_metrics')
    op.drop_table('reports')
    op.drop_table('goals')
    op.drop_table('kpis')
    op.execute('DROP TYPE IF EXISTS aggregation')
