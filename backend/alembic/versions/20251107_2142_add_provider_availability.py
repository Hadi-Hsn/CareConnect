"""add_provider_availability

Revision ID: 0056464cb306
Revises:
Create Date: 2025-11-07 21:42:33.711794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0056464cb306'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create provider_availability table
    op.create_table(
        'provider_availability',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.String(20), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_provider_availability_id', 'provider_availability', ['id'])
    op.create_index('ix_provider_availability_provider_id', 'provider_availability', ['provider_id'])


def downgrade() -> None:
    op.drop_index('ix_provider_availability_provider_id', table_name='provider_availability')
    op.drop_index('ix_provider_availability_id', table_name='provider_availability')
    op.drop_table('provider_availability')
