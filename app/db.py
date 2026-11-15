import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = os.environ.get("CLOUDVAULT_DB_PATH", "cloudvault.db")


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    target = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    target = db_path or DEFAULT_DB_PATH
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    with get_connection(target) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
