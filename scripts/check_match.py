"""Sanity-check the matching engine.

    python scripts/check_match.py

Runs several deliberately different learner personas through the real pipeline
and prints the ranking for each, with the expected top tutor.

This matters more than it looks. Every other part of the stack either works or
throws an exception - matching can silently return plausible-looking garbage.
If a visual learner isn't ranking the diagram-heavy tutor first, the seed bios
are probably too similar to each other to produce distinct vectors.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tutormatch.config import settings  # noqa: E402
from tutormatch.matching import match_for_answers, using_real_embeddings  # noqa: E402

# (label, answers, subjects, who we'd expect near the top and why)
PERSONAS = [
    (
        "Visual calculus learner",
        {
            "intake": "visual",
            "explanation": "examples_first",
            "pace": "moderate",
            "when_stuck": "similar_example",
            "structure": "agenda",
            "goal": "understand the chain rule before my midterm",
        },
        ["calculus"],
        "Maya Okonkwo (diagram-driven)",
    ),
    (
        "Wants to be questioned, not told",
        {
            "intake": "verbal",
            "explanation": "discovery",
            "pace": "slow",
            "when_stuck": "socratic",
            "structure": "discussion",
            "goal": "actually understand calculus instead of memorising it",
        },
        ["calculus"],
        "Priya Venkatesan (socratic)",
    ),
    (
        "Cramming for a chemistry exam",
        {
            "intake": "kinesthetic",
            "explanation": "examples_first",
            "pace": "fast",
            "when_stuck": "walkthrough",
            "structure": "drilling",
            "goal": "pass my chemistry final in two weeks",
        },
        ["chemistry"],
        "Colin Mbeki (exam drilling)",
    ),
    (
        "Nervous beginner programmer",
        {
            "intake": "verbal",
            "explanation": "analogy",
            "pace": "slow",
            "when_stuck": "walkthrough",
            "structure": "freeform",
            "goal": "learn to code from scratch, I have never programmed",
        },
        ["computer_science"],
        "Nadia Haddad (analogy, beginner-friendly)",
    ),
    (
        "Hands-on builder",
        {
            "intake": "kinesthetic",
            "explanation": "discovery",
            "pace": "fast",
            "when_stuck": "hint",
            "structure": "freeform",
            "goal": "build a real project and learn as I go",
        },
        ["computer_science"],
        "Grace Sullivan (project-based)",
    ),
]


def main() -> int:
    if not settings.has_db:
        print("TIGER_URL is not set. Put your TigerData connection string in .env")
        return 1

    kind = "Gemini" if using_real_embeddings() else "LOCAL FALLBACK (no GEMINI_API_KEY)"
    print(f"Embeddings: {kind}")
    if not using_real_embeddings():
        print("  ^ lexical only, not semantic. Rankings will improve a lot with a key.")

    for label, answers, subjects, expected in PERSONAS:
        sentence, matches = match_for_answers(answers, subjects, limit=3)
        print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
        print(f"profile: {sentence}")
        print(f"expect near top: {expected}\n")
        if not matches:
            print("  NO MATCHES - did you run scripts/seed.py?")
            continue
        for i, m in enumerate(matches, 1):
            print(
                f"  {i}. {m.user.name:<20} score={m.score:.3f}  "
                f"(style={m.style_similarity:.3f} subject={m.subject_overlap:.2f} "
                f"rating={m.rating})"
            )

    print(f"\n{'=' * 70}")
    print("Eyeball these. If the expected tutor isn't at or near the top, the")
    print("problem is almost always that the seed bios read too similarly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
