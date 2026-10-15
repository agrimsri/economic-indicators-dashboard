import argparse
import asyncio
import getpass
import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.migrator import run_migrations
from app.db.pool import close_db_pool, init_db_pool
from app.db.queries import create_user
from app.security import hash_password


async def main():
    parser = argparse.ArgumentParser(description="Create or update an evaluation user.")
    parser.add_argument("--username", help="User username (or set PANEL_EVAL_USER env var)")
    parser.add_argument("--password", help="User password (or set PANEL_EVAL_PASSWORD env var; prompted if absent)")
    parser.add_argument("--role", default="evaluator", help="User role (default: evaluator)")
    args = parser.parse_args()

    username = args.username or os.environ.get("PANEL_EVAL_USER")
    if not username:
        username = input("Username: ").strip()

    if not username:
        print("Error: Username is required.")
        sys.exit(1)

    password = args.password or os.environ.get("PANEL_EVAL_PASSWORD")
    if not password:
        password = getpass.getpass("Password: ")

    if not password:
        print("Error: Password is required.")
        sys.exit(1)

    print("Ensuring database schema is ready...")
    await run_migrations()

    print(f"Provisioning user '{username}' with role '{args.role}'...")
    hashed = hash_password(password)

    await init_db_pool()
    try:
        user = await create_user(username=username, password_hash=hashed, role=args.role)
        print(f"SUCCESS: User '{user['username']}' (ID: {user['id']}) provisioned successfully.")
    finally:
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(main())
