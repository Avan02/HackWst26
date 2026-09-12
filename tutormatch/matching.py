"""Learning-style matching.

The premise: don't match on subject alone. The quiz asks how a student learns
across five axes, every tutor is scored on those same axes, and a match is a
tutor whose teaching style scores high on the answers this student actually gave.

    quiz answers  ->  per-axis affinity lookup in TigerData  ->  ranked tutors

No AI involved. The scoring is a weighted sum the database computes directly,
which means it's fast, deterministic, and - importantly - explainable: we can
say exactly which answers drove a match rather than guessing at why a model
put two things near each other.
"""

from __future__ import annotations

from typing import Any

from .db import fetch_all
from .schemas import TutorMatch, User

# The five quiz axes that carry style signal. `goal` is free text and is not
# scored - it's kept for display and for the tutor to read before a session.
STYLE_AXES = ("intake", "explanation", "pace", "when_stuck", "structure")

# Style dominates on purpose: matching on how someone learns is the whole
# premise. Subject is a strong secondary signal, rating a tiebreak.
W_STYLE = 0.55
W_SUBJECT = 0.30
W_RATING = 0.15


# ------------------------------------------------------------ profile summary

# Human-readable phrasing for each answer, from the student's side.
_LEARNER_PHRASES: dict[str, dict[str, str]] = {
    "intake": {
        "visual": "learns best from diagrams and pictures",
        "verbal": "learns best by being talked through ideas",
        "reading": "learns best from clear written explanations",
        "kinesthetic": "learns best by trying things hands-on",
    },
    "explanation": {
        "examples_first": "wants a worked example before the rule",
        "theory_first": "wants the rule stated first, then applied",
        "analogy": "understands ideas through analogies",
        "discovery": "prefers working things out independently",
    },
    "pace": {
        "slow": "wants a slow, thorough pace",
        "moderate": "wants a steady, moderate pace",
        "fast": "wants a fast pace that skips basics",
    },
    "when_stuck": {
        "hint": "wants a hint and space to keep trying when stuck",
        "walkthrough": "wants a full walkthrough when stuck",
        "socratic": "wants guiding questions rather than answers",
        "similar_example": "wants to see a similar problem solved first",
    },
    "structure": {
        "agenda": "wants sessions run to a clear agenda",
        "freeform": "wants freeform, question-driven sessions",
        "drilling": "wants lots of back-to-back practice",
        "discussion": "wants to discuss the underlying concepts",
    },
}

# Phrasing for the same answers from the tutor's side, used to build the
# "why you matched" line without an AI.
_TUTOR_PHRASES: dict[str, dict[str, str]] = {
    "intake": {
        "visual": "teaches through diagrams and visuals",
        "verbal": "talks students through ideas out loud",
        "reading": "leaves you with clear written explanations",
        "kinesthetic": "gets you doing rather than watching",
    },
    "explanation": {
        "examples_first": "shows a worked example before the rule",
        "theory_first": "starts from the rule and then applies it",
        "analogy": "explains through everyday analogies",
        "discovery": "lets you work things out yourself",
    },
    "pace": {
        "slow": "works at a slow, thorough pace",
        "moderate": "keeps a steady pace with room for questions",
        "fast": "moves fast and skips the basics",
    },
    "when_stuck": {
        "hint": "gives a nudge rather than the answer",
        "walkthrough": "walks you through the whole problem",
        "socratic": "asks questions until you find it yourself",
        "similar_example": "solves a similar problem first, then hands it back",
    },
    "structure": {
        "agenda": "runs every session to a clear agenda",
        "freeform": "lets you drive the session with your own questions",
        "drilling": "runs lots of practice problems back to back",
        "discussion": "digs into the concepts underneath",
    },
}


def build_profile_sentence(answers: dict[str, str], subjects: list[str]) -> str:
    """A readable summary of the learner, for display and for debugging matches."""
    parts = [
        _LEARNER_PHRASES[ax][answers[ax]]
        for ax in STYLE_AXES
        if answers.get(ax) in _LEARNER_PHRASES.get(ax, {})
    ]
    sentence = "A student who " + ", ".join(parts) if parts else "A student"
    if subjects:
        sentence += f". Studying {', '.join(s.replace('_', ' ') for s in subjects)}"
    goal = (answers.get("goal") or "").strip()
    if goal:
        sentence += f". Their goal: {goal}"
    return sentence + "."


# ----------------------------------------------------------------- explaining


def explain(answers: dict[str, str], affinity: dict[str, Any], limit: int = 2) -> str:
    """Say why this tutor fits, naming the answers that actually drove the score.

    Picks the axes where the tutor scores highest on this student's answers, so
    the explanation is always true by construction - it's reading the same
    numbers the ranking used.
    """
    scored: list[tuple[float, str]] = []
    for ax in STYLE_AXES:
        ans = answers.get(ax)
        if not ans:
            continue
        score = float((affinity.get(ax) or {}).get(ans, 0.0))
        phrase = _TUTOR_PHRASES.get(ax, {}).get(ans)
        if phrase and score >= 0.6:
            scored.append((score, phrase))

    scored.sort(reverse=True)
    picked = [p for _, p in scored[:limit]]
    if not picked:
        return "Covers your subject, though their teaching style is a looser fit."
    if len(picked) == 1:
        return f"This tutor {picked[0]} - which is what you asked for."
    return f"This tutor {picked[0]} and {picked[1]} - both things you asked for."


# ------------------------------------------------------------------- matching

# Scoring happens in SQL so TigerData does the work. Each axis contributes the
# tutor's stored affinity for the answer this student gave; missing entries
# score 0 via COALESCE.
_STYLE_SUM = " + ".join(
    f"COALESCE((tp.style_affinity -> '{ax}' ->> %({ax})s)::float, 0)" for ax in STYLE_AXES
)

MATCH_SQL = f"""
WITH scored AS (
    SELECT
        u.auth_sub, u.name, u.email, u.avatar_url,
        tp.bio, tp.subjects, tp.hourly_rate_sol, tp.rating, tp.style_affinity,
        ({_STYLE_SUM}) / {len(STYLE_AXES)}.0 AS style_score,
        CASE WHEN cardinality(%(subjects)s::text[]) = 0 THEN 1.0
             ELSE cardinality(ARRAY(SELECT unnest(tp.subjects)
                                    INTERSECT SELECT unnest(%(subjects)s::text[])))::float
                  / cardinality(%(subjects)s::text[])
        END AS subject_overlap
    FROM tutor_profiles tp
    JOIN users u ON u.auth_sub = tp.user_id
    WHERE tp.style_affinity IS NOT NULL
      AND (cardinality(%(subjects)s::text[]) = 0 OR tp.subjects && %(subjects)s::text[])
      AND (%(max_rate)s::numeric IS NULL OR tp.hourly_rate_sol <= %(max_rate)s::numeric)
)
SELECT *,
       {W_STYLE} * style_score
     + {W_SUBJECT} * subject_overlap
     + {W_RATING} * (rating / 5.0) AS score
FROM scored
ORDER BY score DESC
LIMIT %(limit)s
"""


def find_matches(
    answers: dict[str, str],
    subjects: list[str],
    *,
    max_rate: float | None = None,
    limit: int = 3,
) -> list[TutorMatch]:
    """Rank tutors for a learner. Hard-filters on subject and price, then scores."""
    params: dict[str, Any] = {
        "subjects": subjects,
        "max_rate": max_rate,
        "limit": limit,
    }
    # Answers the student didn't give become a sentinel that matches no key,
    # so that axis contributes 0 rather than erroring.
    for ax in STYLE_AXES:
        params[ax] = answers.get(ax) or "__none__"

    rows: list[dict[str, Any]] = fetch_all(MATCH_SQL, params)

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
            style_similarity=round(float(r["style_score"]), 4),
            subject_overlap=round(float(r["subject_overlap"]), 4),
            rationale=explain(answers, r["style_affinity"] or {}),
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
    """Quiz answers straight to ranked tutors, plus the readable profile summary."""
    sentence = build_profile_sentence(answers, subjects)
    return sentence, find_matches(answers, subjects, max_rate=max_rate, limit=limit)
