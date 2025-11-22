"""add whatsapp columns

Revision ID: 20251123_whatsapp
Revises: 0056464cb306
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251123_whatsapp'
down_revision = '0056464cb306'
branch_labels = None
depends_on = None


def upgrade():
    """Add WhatsApp support columns to users table."""
    # Add country_code column with default value
    op.add_column('users', sa.Column('country_code', sa.String(10), nullable=False, server_default='+961'))
    
    # Add whatsapp_verified column
    op.add_column('users', sa.Column('whatsapp_verified', sa.Boolean(), nullable=False, server_default='0'))
    
    # Make phone column NOT NULL (if it exists, alter it; otherwise users must have phone already)
    # First, set any NULL phones to empty string to avoid constraint violation
    op.execute("UPDATE users SET phone = '' WHERE phone IS NULL")
    
    # Now we can safely make it NOT NULL
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('phone', nullable=False, existing_type=sa.String(50))
    
    # Add unique constraint on phone + country_code combination
    op.create_unique_constraint('uix_phone_country', 'users', ['phone', 'country_code'])
    
    # Create whatsapp_messages table for conversation history
    op.create_table(
        'whatsapp_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(50), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_sid', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_whatsapp_messages_id', 'whatsapp_messages', ['id'])
    op.create_index('ix_whatsapp_messages_user_id', 'whatsapp_messages', ['user_id'])
    op.create_index('ix_whatsapp_messages_phone_number', 'whatsapp_messages', ['phone_number'])
    op.create_index('ix_whatsapp_messages_created_at', 'whatsapp_messages', ['created_at'])


def downgrade():
    """Remove WhatsApp support columns."""
    # Drop whatsapp_messages table
    op.drop_index('ix_whatsapp_messages_created_at', table_name='whatsapp_messages')
    op.drop_index('ix_whatsapp_messages_phone_number', table_name='whatsapp_messages')
    op.drop_index('ix_whatsapp_messages_user_id', table_name='whatsapp_messages')
    op.drop_index('ix_whatsapp_messages_id', table_name='whatsapp_messages')
    op.drop_table('whatsapp_messages')
    
    # Drop unique constraint
    op.drop_constraint('uix_phone_country', 'users', type_='unique')
    
    # Make phone nullable again
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('phone', nullable=True, existing_type=sa.String(50))
    
    # Drop columns
    op.drop_column('users', 'whatsapp_verified')
    op.drop_column('users', 'country_code')
