import os
import subprocess
import sys
from urllib.parse import urlparse

# Tambah root project ke path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import src.config.env as env

# Parse URL
parsed_url = urlparse(env.DATABASE_URL)
DB_NAME = parsed_url.path.lstrip("/")
DB_URL = env.DATABASE_URL


def terminate_connections():
    print(f"Terminating active connections to database '{DB_NAME}'...")
    try:
        subprocess.run(
            [
                "psql",
                DB_URL,
                "-c",
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid();",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error terminating connections: {e}")
        sys.exit(1)


def drop_and_create_db():
    print(f"Dropping database '{DB_NAME}' if exists...")
    subprocess.run(
        [
            "dropdb",
            "--if-exists",
            DB_NAME,
            "--host",
            parsed_url.hostname,
            "--port",
            str(parsed_url.port),
            "--username",
            parsed_url.username,
        ],
        check=True,
    )

    print(f"Creating database '{DB_NAME}'...")
    subprocess.run(
        [
            "createdb",
            DB_NAME,
            "--host",
            parsed_url.hostname,
            "--port",
            str(parsed_url.port),
            "--username",
            parsed_url.username,
        ],
        check=True,
    )


def upgrade_migrations():
    print("Upgrading Alembic migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)


def main():
    terminate_connections()
    drop_and_create_db()
    upgrade_migrations()
    print("✅ Database fresh migrated!")


if __name__ == "__main__":
    main()
