"""Create or update admin user - Quick script for production setup."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.core.db import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models import User, UserRole


async def create_or_update_admin():
    """Ensure admin user exists with correct credentials."""
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == "admin@aub.com")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            # Update existing admin
            admin.hashed_password = get_password_hash("Admin@123")
            admin.name = "Admin User"
            admin.role = UserRole.ADMIN
            print("✓ Admin user updated")
        else:
            # Create new admin
            admin = User(
                email="admin@aub.com",
                name="Admin User",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("Admin@123"),
            )
            session.add(admin)
            print("✓ Admin user created")
        
        await session.commit()
        print()
        print("Admin credentials:")
        print("  Email: admin@aub.com")
        print("  Password: Admin@123")
        print()


async def main():
    """Run admin creation."""
    print("🔧 Setting up admin user...")
    print()
    
    # Initialize database
    await init_db()
    
    # Create/update admin
    await create_or_update_admin()
    
    print("✅ Admin setup complete!")


if __name__ == "__main__":
    asyncio.run(main())
