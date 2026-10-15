import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.migrator import run_migrations


async def main():
    print("Running database migrations...")
    await run_migrations()
    print("Database migrations applied successfully.")


if __name__ == "__main__":
    asyncio.run(main())
