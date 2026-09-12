"""Load the tutor pool into TigerData and embed each teaching-style bio.

    python scripts/seed.py

Safe to re-run - upserts by auth_sub. Re-run this after adding a GEMINI_API_KEY
to replace the fallback vectors with real semantic ones.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tutormatch.config import settings  # noqa: E402
from tutormatch.db import execute, fetch_one, upsert_user  # noqa: E402
from tutormatch.fixtures import TUTORS  # noqa: E402
from tutormatch.matching import embed, using_real_embeddings  # noqa: E402


def main() -> int:
    if not settings.has_db:
        print("TIGER_URL is not set. Put your TigerData connection string in .env")
        return 1

    kind = "Gemini" if using_real_embeddings() else "local fallback (no GEMINI_API_KEY)"
    print(f"Embedding with: {kind}")
    print(f"Seeding {len(TUTORS)} tutors...\n")

    for t in TUTORS:
        upsert_user(
            t.auth_sub,
            name=t.name,
            email=t.email,
            avatar_url=t.avatar_url,
            role="tutor",
        )
        # Embed the bio - this is what learner profiles get compared against.
        vector = embed(t.bio)
        execute(
            """
            INSERT INTO tutor_profiles
                (user_id, bio, subjects, teaching_style_vector, hourly_rate_sol, rating)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                bio                   = EXCLUDED.bio,
                subjects              = EXCLUDED.subjects,
                teaching_style_vector = EXCLUDED.teaching_style_vector,
                hourly_rate_sol       = EXCLUDED.hourly_rate_sol,
                rating                = EXCLUDED.rating
            """,
            (t.auth_sub, t.bio, t.subjects, str(vector), t.hourly_rate_sol, t.rating),
        )
        print(f"  {t.auth_sub}  {t.name:<20} {', '.join(t.subjects)}")

    row = fetch_one(
        "SELECT count(*) AS n FROM tutor_profiles WHERE teaching_style_vector IS NOT NULL"
    )
    print(f"\n{row['n']} tutors have style vectors.")
    print("Next: python scripts/check_match.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
