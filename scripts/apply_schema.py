"""Create the TigerData tables.

    python scripts/apply_schema.py

Safe to re-run - schema.sql is idempotent.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tutormatch.config import settings  # noqa: E402
from tutormatch.db import apply_schema, fetch_all, ping  # noqa: E402


def main() -> int:
    if not settings.has_db:
        print("TIGER_URL is not set. Put your TigerData connection string in .env")
        return 1

    print("Connecting to TigerData...")
    info = ping()
    print(f"  postgres    : {str(info.get('pg_version', '?')).split(',')[0]}")
    print(f"  timescaledb : {info.get('timescaledb') or 'NOT INSTALLED'}")
    print(f"  pgvector    : {info.get('pgvector') or 'NOT INSTALLED'}")

    print("\nApplying schema.sql...")
    apply_schema()

    tables = fetch_all(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
    )
    print(f"\nTables ({len(tables)}):")
    for t in tables:
        print(f"  - {t['table_name']}")

    hyper = fetch_all("SELECT hypertable_name FROM timescaledb_information.hypertables")
    print(f"\nHypertables ({len(hyper)}):")
    for h in hyper:
        print(f"  - {h['hypertable_name']}")

    print("\nDone. Next: python scripts/seed.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
