"""
One-time helper: creates every table defined by the SQLAlchemy models.

There's no Alembic migration setup in this project yet, so this is the
quickest way to get a fresh database ready to run against. Run it once
after DATABASE_URL in your .env points at a real (empty) Postgres
database:

    cd backend
    python create_tables.py

Safe to re-run - create_all() skips tables that already exist.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine
from app.models import Base

if __name__ == "__main__":
    print(f"Creating tables on: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables are ready.")