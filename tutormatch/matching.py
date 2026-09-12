"""Learning-style matching.

The idea: don't match on subject alone. Turn the quiz answers into a sentence
describing how this person learns, embed it, and find tutors whose teaching
style sits nearby in vector space.

Pipeline:
    quiz answers  ->  profile sentence  ->  768-d embedding  ->  pgvector search

Embedding the SENTENCE rather than the raw answers matters: it gives the model
real language to work with, and it means a tutor bio and a learner profile land
in the same semantic space even though they're written differently.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from .config import settings
from .db import fetch_all
from .schemas import TutorMatch, User

EMBED_DIM = 768
EMBED_MODEL = "gemini-embedding-001"

# --------------------------------------------------------- profile sentence

# Maps each quiz answer to a clause. Keep these as natural language - they get
# embedded, so "prefers diagrams" carries more signal than "intake=visual".
_CLAUSES: dict[str, dict[str, str]] = {
    "intake": {
        "visual": "learns best from diagrams and pictures",
        "verbal": "learns best by being talked through ideas out loud",
        "reading": "learns best by reading clear written explanations",
        "kinesthetic": "learns best by trying things and seeing what breaks",
    },
    "explanation": {
        "examples_first": "wants a worked example before the general rule",
        "theory_first": "wants the rule stated first, then applied",
        "analogy": "understands new ideas through analogies to familiar things",
        "discovery": "prefers to experiment and work things out independently",
    },
    "pace": {
        "slow": "prefers a slow, thorough pace covering every step",
        "moderate": "prefers a steady, moderate pace with room for questions",
        "fast": "prefers a fast pace that hits highlights and skips basics",
    },
    "when_stuck": {
        "hint": "when stuck, wants a small hint and space to keep trying",
        "walkthrough": "when stuck, wants a full walkthrough from start to finish",
        "socratic": "when stuck, wants guiding questions rather than answers",
        "similar_example": "when stuck, wants to see a similar problem solved first",
    },
    "structure": {
        "agenda": "wants sessions run to a clear agenda",
        "freeform": "wants freeform sessions driven by their own questions",
        "drilling": "wants lots of back-to-back practice problems",
        "discussion": "wants open discussion of underlying concepts",
    },
}


def build_profile_sentence(answers: dict[str, str], subjects: list[str]) -> str:
    """Turn quiz answers into the sentence we embed.

    Example output:
        "A student who learns best from diagrams and pictures, wants a worked
         example before the general rule, prefers a steady, moderate pace...
         Studying calculus. Their goal: build intuition before the midterm."
    """
    parts = [
        _CLAUSES[qid][answers[qid]]
        for qid in ("intake", "explanation", "pace", "when_stuck", "structure")
        if qid in answers and answers[qid] in _CLAUSES.get(qid, {})
    ]

    sentence = "A student who " + ", ".join(parts) if parts else "A student"
    if subjects:
        sentence += f". Studying {', '.join(s.replace('_', ' ') for s in subjects)}"
    goal = (answers.get("goal") or "").strip()
    if goal:
        sentence += f". Their goal: {goal}"
    return sentence + "."


# ------------------------------------------------------------- embeddings

def _fallback_embedding(text: str) -> list[float]:
    """Deterministic local embedding, used when GEMINI_API_KEY isn't set.

    Hashes word bigrams into buckets and L2-normalises. This is NOT semantic -
    it only captures lexical overlap - but it lets the whole pipeline (seed,
    store, query, rank) be built and tested before anyone has an API key, and
    it produces stable vectors so results don't jump around between runs.

    Swap happens automatically the moment GEMINI_API_KEY appears in .env.
    """
    words = re.findall(r"[a-z]+", text.lower())
    vec = [0.0] * EMBED_DIM
    grams = words + [f"{a}_{b}" for a, b in zip(words, words[1:])]
    for g in grams:
        h = int(hashlib.blake2b(g.encode(), digest_size=8).hexdigest(), 16)
        vec[h % EMBED_DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed(text: str) -> list[float]:
    """Embed text to a 768-d vector. Uses Gemini when configured."""
    if not settings.has_gemini:
        return _fallback_embedding(text)

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM),
    )
    return list(result.embeddings[0].values)


def using_real_embeddings() -> bool:
    return settings.has_gemini


# ------------------------------------------------------------------ matching

# Weights. Style similarity dominates on purpose - that's the whole premise of
# the product. Subject overlap is a strong secondary signal, rating a tiebreak.
W_STYLE = 0.55
W_SUBJECT = 0.30
W_RATING = 0.15

MATCH_SQL = """
SELECT
    u.auth_sub,
    u.name,
    u.email,
    u.avatar_url,
    tp.bio,
    tp.subjects,
    tp.hourly_rate_sol,
    tp.rating,
    1 - (tp.teaching_style_vector <=> %(vec)s::vector) AS style_similarity,
    cardinality(ARRAY(SELECT unnest(tp.subjects) INTERSECT SELECT unnest(%(subjects)s::text[])))::float
        / GREATEST(cardinality(%(subjects)s::text[]), 1) AS subject_overlap,
      %(w_style)s   * (1 - (tp.teaching_style_vector <=> %(vec)s::vector))
    + %(w_subject)s * (cardinality(ARRAY(SELECT unnest(tp.subjects) INTERSECT SELECT unnest(%(subjects)s::text[])))::float
                       / GREATEST(cardinality(%(subjects)s::text[]), 1))
    + %(w_rating)s  * (tp.rating / 5.0) AS score
FROM tutor_profiles tp
JOIN users u ON u.auth_sub = tp.user_id
WHERE tp.teaching_style_vector IS NOT NULL
  AND (%(subjects)s::text[] = '{}' OR tp.subjects && %(subjects)s::text[])
  AND (%(max_rate)s::numeric IS NULL OR tp.hourly_rate_sol <= %(max_rate)s::numeric)
ORDER BY score DESC
LIMIT %(limit)s
"""


def find_matches(
    style_vector: list[float],
    subjects: list[str],
    *,
    max_rate: float | None = None,
    limit: int = 3,
) -> list[TutorMatch]:
    """Rank tutors for a learner. Hard-filters on subject and price, then scores.

    `<=>` is pgvector's cosine distance, so `1 - distance` is similarity.
    """
    rows: list[dict[str, Any]] = fetch_all(
        MATCH_SQL,
        {
            "vec": str(style_vector),
            "subjects": subjects,
            "max_rate": max_rate,
            "limit": limit,
            "w_style": W_STYLE,
            "w_subject": W_SUBJECT,
            "w_rating": W_RATING,
        },
    )

    return [
        TutorMatch(
            user=User(
                auth_sub=r["auth_sub"],
                role="tutor",
                name=r["name"],
                email=r["email"],
                avatar_url=r["avatar_url"],
            ),
            bio=r["bio"],
            subjects=r["subjects"],
            hourly_rate_sol=float(r["hourly_rate_sol"]),
            rating=float(r["rating"]),
            score=round(float(r["score"]), 4),
            style_similarity=round(float(r["style_similarity"]), 4),
            subject_overlap=round(float(r["subject_overlap"]), 4),
        )
        for r in rows
    ]


def match_for_answers(
    answers: dict[str, str],
    subjects: list[str],
    *,
    max_rate: float | None = None,
    limit: int = 3,
) -> tuple[str, list[TutorMatch]]:
    """Convenience: quiz answers straight to ranked tutors.

    Returns the profile sentence alongside the matches so callers can show
    (or debug) what the ranking was actually based on.
    """
    sentence = build_profile_sentence(answers, subjects)
    vector = embed(sentence)
    return sentence, find_matches(vector, subjects, max_rate=max_rate, limit=limit)
