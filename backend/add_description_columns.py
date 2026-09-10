"""
One-time helper: adds the new multi-language description columns to an
*already existing* `products` table.

Why this script exists: there's no Alembic migration setup in this
project (see create_tables.py) - `Base.metadata.create_all()` only
creates tables that don't exist yet, it never alters a table that's
already there. Since the `products` table was created before this
change, running create_tables.py again will NOT add the new columns.
Run this script once instead, against the same DATABASE_URL:

    cd backend
    python add_description_columns.py

Safe to re-run - every ALTER TABLE uses IF NOT EXISTS.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text

from app.database import engine

NEW_COLUMNS = [
    ("description_regional", "TEXT"),
    ("description_english", "TEXT"),
    ("description_hindi", "TEXT"),
    ("regional_language_label", "VARCHAR(50)"),
]

if __name__ == "__main__":
    print(f"Altering `products` table on: {engine.url}")

    with engine.begin() as connection:
        for column_name, column_type in NEW_COLUMNS:
            connection.execute(
                text(
                    f"ALTER TABLE products "
                    f"ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                )
            )
            print(f"  ok: {column_name} ({column_type})")

    print("Done. `products` table is up to date.")