from app.db_connection import SessionLocal
import asyncio

from app.seed.user import seed_user
from app.seed.info import seed_info
from app.seed.timeline import seed_timeline
from app.seed.project import seed_project

async def seed_data():
    db = SessionLocal()
    print("📢 Start seed data ..........")
    try:
        # seed_timeline(db=db)
        await seed_project(db=db)
        db.commit()
        print(f"✅ Added and commited seed data was successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌  Oppps, Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())