import logging
from pathlib import Path

import psycopg

from app.config import settings

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"


async def run_migrations() -> None:
    logger.info("Checking and running pending migrations...")
    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:
        async with conn.cursor() as cur:
            # 1. Ensure migrations tracking table exists
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)
            await conn.commit()

            # 2. Get already applied migrations
            await cur.execute("SELECT version FROM schema_migrations;")
            applied = {row[0] for row in await cur.fetchall()}

            # 3. Find and sort migration files
            migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
            for mf in migration_files:
                version = mf.name
                if version not in applied:
                    logger.info(f"Applying migration: {version}")
                    sql_content = mf.read_text(encoding="utf-8")
                    # Execute migration within transaction
                    async with conn.transaction():
                        await cur.execute(sql_content)
                        await cur.execute(
                            "INSERT INTO schema_migrations (version) VALUES (%s);",
                            (version,)
                        )
                    logger.info(f"Successfully applied migration: {version}")
                else:
                    logger.debug(f"Migration already applied: {version}")

    logger.info("Migrations completed.")
