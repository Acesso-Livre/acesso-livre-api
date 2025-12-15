import asyncio
import sys
import os
from sqlalchemy import select
from datetime import datetime, timezone

# Add the project directory to sys.path to allow imports
# Assuming this script is run from the root of the project
sys.path.append(os.getcwd())

# Import from the application
try:
    from acesso_livre_api.src.database import AsyncSessionLocal
    from acesso_livre_api.src.admins.models import Admins
    from acesso_livre_api.src.admins.service import get_password_hash
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you are running this script from the root of the project.")
    sys.exit(1)

async def create_admin_user(email, password):
    print(f"Connecting to database to create admin: {email}")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin already exists
            stmt = select(Admins).where(Admins.email == email)
            result = await session.execute(stmt)
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print(f"Admin with email '{email}' already exists.")
                return

            # Hash the password
            hashed_password = get_password_hash(password)
            
            # Create new admin instance
            new_admin = Admins(
                email=email,
                password=hashed_password,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            session.add(new_admin)
            await session.commit()
            print(f"Successfully created admin user: {email}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            await session.rollback()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password>")
        sys.exit(1)
        
    email_arg = sys.argv[1]
    password_arg = sys.argv[2]
    
    asyncio.run(create_admin_user(email_arg, password_arg))
