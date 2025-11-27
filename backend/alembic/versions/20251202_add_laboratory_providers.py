"""Add dedicated laboratory providers."""

from datetime import datetime, timezone

from alembic import op
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
    now = datetime.now(timezone.utc)
    for provider in LAB_PROVIDERS:
        op.execute(
            f"""
            INSERT INTO providers (name, department, type, specialty, bio, created_at, updated_at)
            SELECT '{provider["name"]}', '{provider["department"]}', '{provider["type"]}',
                   '{provider["specialty"]}', '{provider["bio"]}', '{now.isoformat()}', '{now.isoformat()}'
            WHERE NOT EXISTS (
                SELECT 1 FROM providers WHERE name = '{provider["name"]}'
            )
            """
        )


def downgrade() -> None:
    names = "', '".join(p["name"] for p in LAB_PROVIDERS)
    op.execute(f"DELETE FROM providers WHERE name IN ('{names}')")

