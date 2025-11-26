"""add whatsapp columns

Revision ID: 20251123_whatsapp
Revises: 0056464cb306
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = '20251123_whatsapp'
down_revision = '0056464cb306'
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    if not table_exists(table_name):
        return False
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def constraint_exists(table_name: str, constraint_name: str) -> bool:
    """Check if a unique constraint exists."""
    if not table_exists(table_name):
        return False
    try:
        bind = op.get_bind()
        inspector = inspect(bind)
        constraints = [c['name'] for c in inspector.get_unique_constraints(table_name)]
        return constraint_name in constraints
    except Exception:
        return False


def upgrade():
    """Add WhatsApp support columns to users table."""
    # Only proceed if users table exists
    if not table_exists('users'):
        # If users table doesn't exist, the migration will be handled by init_db()
        # which creates tables from models (including these columns)
        return
    
    # Add country_code column with default value (if it doesn't exist)
    if not column_exists('users', 'country_code'):
        op.add_column('users', sa.Column('country_code', sa.String(10), nullable=False, server_default='+961'))
    
    # Add whatsapp_verified column (if it doesn't exist)
    if not column_exists('users', 'whatsapp_verified'):
        op.add_column('users', sa.Column('whatsapp_verified', sa.Boolean(), nullable=False, server_default='0'))
    
    # Make phone column NOT NULL (if it exists and is nullable)
    # First, set any NULL phones to empty string to avoid constraint violation
    try:
        op.execute(text("UPDATE users SET phone = '' WHERE phone IS NULL"))
    except Exception:
        pass  # Table might not have data yet
    
    # Now we can safely make it NOT NULL (only if column exists and is currently nullable)
    if column_exists('users', 'phone'):
        try:
            with op.batch_alter_table('users') as batch_op:
                batch_op.alter_column('phone', nullable=False, existing_type=sa.String(50))
        except Exception:
            # Column might already be NOT NULL, ignore
            pass
    
    # Add unique constraint on phone + country_code combination (if it doesn't exist)
    # SQLite requires batch_alter_table for constraint operations
    if not constraint_exists('users', 'uix_phone_country'):
        try:
            with op.batch_alter_table('users') as batch_op:
                batch_op.create_unique_constraint('uix_phone_country', ['phone', 'country_code'])
        except Exception:
            # Constraint might already exist or there might be duplicate data, ignore
            pass
    
    # Create whatsapp_messages table for conversation history (if it doesn't exist)
    if not table_exists('whatsapp_messages'):
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
    # Drop whatsapp_messages table (if it exists)
    if table_exists('whatsapp_messages'):
        try:
            op.drop_index('ix_whatsapp_messages_created_at', table_name='whatsapp_messages')
            op.drop_index('ix_whatsapp_messages_phone_number', table_name='whatsapp_messages')
            op.drop_index('ix_whatsapp_messages_user_id', table_name='whatsapp_messages')
            op.drop_index('ix_whatsapp_messages_id', table_name='whatsapp_messages')
            op.drop_table('whatsapp_messages')
        except Exception:
            pass
    
    # Drop unique constraint (if it exists)
    if constraint_exists('users', 'uix_phone_country'):
        try:
            with op.batch_alter_table('users') as batch_op:
                batch_op.drop_constraint('uix_phone_country', type_='unique')
        except Exception:
            pass
    
    # Make phone nullable again (if users table exists)
    if table_exists('users') and column_exists('users', 'phone'):
        try:
            with op.batch_alter_table('users') as batch_op:
                batch_op.alter_column('phone', nullable=True, existing_type=sa.String(50))
        except Exception:
            pass
    
    # Drop columns (if they exist)
    if column_exists('users', 'whatsapp_verified'):
        try:
            op.drop_column('users', 'whatsapp_verified')
        except Exception:
            pass
    if column_exists('users', 'country_code'):
        try:
            op.drop_column('users', 'country_code')
        except Exception:
            pass
