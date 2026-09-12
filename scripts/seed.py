"""Load the tutor pool and their teaching-style scores into TigerData.

    python scripts/seed.py

Safe to re-run - upserts by auth_sub. Re-run after editing any tutor's style
scores in tutormatch/fixtures.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from psycopg.types.json import Json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tutormatch.config import settings  # noqa: E402
from tutormatch.db import execute, fetch_one, upsert_user  # noqa: E402
from tutormatch.fixtures import TUTORS  # noqa: E402


def main() -> int:
    if not settings.has_db:
        print("TIGER_URL is not set. Put your TigerData connection string in .env")
        return 1

    print(f"Seeding {len(TUTORS)} tutors...\n")

    for t in TUTORS:
        upsert_user(
            t.auth_sub,
            name=t.name,
            email=t.email,
            avatar_url=t.avatar_url,
            role="tutor",
        )
        execute(
            """
            INSERT INTO tutor_profiles
                (user_id, bio, subjects, style_affinity, hourly_rate_sol, rating)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                bio             = EXCLUDED.bio,
                subjects        = EXCLUDED.subjects,
                style_affinity  = EXCLUDED.style_affinity,
                hourly_rate_sol = EXCLUDED.hourly_rate_sol,
                rating          = EXCLUDED.rating
            """,
            (t.auth_sub, t.bio, t.subjects, Json(t.style), t.hourly_rate_sol, t.rating),
        )
        print(f"  {t.auth_sub}  {t.name:<20} {', '.join(t.subjects)}")

    row = fetch_one(
        "SELECT count(*) AS n FROM tutor_profiles WHERE style_affinity IS NOT NULL"
    )
    print(f"\n{row['n']} tutors have style scores.")
    print("Next: python scripts/check_match.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
