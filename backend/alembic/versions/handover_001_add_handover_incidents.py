"""Add handover incidents table

Revision ID: handover_001
Revises: 
Create Date: 2025-10-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'handover_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create handover_incidents table."""
    op.create_table(
        'handover_incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('patient_name', sa.String(length=255), nullable=False),
        sa.Column('patient_email', sa.String(length=255), nullable=False),
        sa.Column('patient_phone', sa.String(length=50), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('chat_summary', sa.Text(), nullable=False),
        sa.Column('full_conversation', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_handover_incidents_id'), 'handover_incidents', ['id'], unique=False)


def downgrade() -> None:
    """Drop handover_incidents table."""
    op.drop_index(op.f('ix_handover_incidents_id'), table_name='handover_incidents')
    op.drop_table('handover_incidents')
