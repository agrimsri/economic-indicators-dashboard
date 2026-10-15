import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.migrator import run_migrations
from app.db.pool import close_db_pool, init_db_pool
from app.services.scheduler import ALL_COLLECTORS


async def main():
    print("Ensuring database schema is ready...")
    await run_migrations()
    await init_db_pool()

    try:
        print(f"Triggering {len(ALL_COLLECTORS)} collectors sequentially...")
        for col in ALL_COLLECTORS:
            print(f"Running '{col.name}'...")
            ok = await col.run()
            status_str = "SUCCESS" if ok else "FAILED"
            print(f"[{status_str}] '{col.name}' finished.")
    finally:
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(main())

