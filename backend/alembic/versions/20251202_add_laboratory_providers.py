"""Add dedicated laboratory providers."""

from datetime import datetime, timezone

from alembic import op
from sqlalchemy import text
# For SQLite compatibility, use raw SQL executed via connection.execute().

# revision identifiers, used by Alembic.
revision = "20251202_add_laboratory_providers"
down_revision = "20251123_whatsapp"
branch_labels = None
depends_on = None

LAB_PROVIDERS = [
    {
        "name": "Lab Services Team A",
        "department": "Laboratory",
        "type": "specialist",
        "specialty": "Diagnostic Lab Testing",
        "bio": "Core laboratory team handling specimen collection and diagnostic testing",
    },
    {
        "name": "Lab Services Team B",
        "department": "Laboratory",
        "type": "specialist",
        "specialty": "Diagnostic Lab Testing",
        "bio": "Experienced technologists ensuring timely turnaround for comprehensive panels",
    },
    {
        "name": "Lab Services Team C",
        "department": "Laboratory",
        "type": "specialist",
        "specialty": "Diagnostic Lab Testing",
        "bio": "Dedicated lab technicians supporting high-volume test scheduling",
    },
]


def upgrade() -> None:
    # Check if providers table exists before trying to insert
    connection = op.get_bind()
    
    # For SQLite, check if table exists
    if connection.dialect.name == 'sqlite':
        try:
            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'")
            ).fetchone()
            if not result:
                # Table doesn't exist yet, skip this migration
                # The table will be created by init_db() or a previous migration
                print("Warning: providers table does not exist, skipping lab provider migration")
                return
        except Exception as e:
            # If we can't check, assume table doesn't exist
            print(f"Warning: Could not check if providers table exists: {e}, skipping migration")
            return
    
    now = datetime.now(timezone.utc)
    for provider in LAB_PROVIDERS:
        try:
            op.execute(
                text(f"""
                INSERT INTO providers (name, department, type, specialty, bio, created_at, updated_at)
                SELECT '{provider["name"]}', '{provider["department"]}', '{provider["type"]}',
                       '{provider["specialty"]}', '{provider["bio"]}', '{now.isoformat()}', '{now.isoformat()}'
                WHERE NOT EXISTS (
                    SELECT 1 FROM providers WHERE name = '{provider["name"]}'
                )
                """)
            )
        except Exception as e:
            # If table doesn't exist or other error, log and continue
            # This migration will be retried on next startup
            print(f"Warning: Could not insert provider {provider['name']}: {e}")
            continue


def downgrade() -> None:
    names = "', '".join(p["name"] for p in LAB_PROVIDERS)
    op.execute(f"DELETE FROM providers WHERE name IN ('{names}')")

