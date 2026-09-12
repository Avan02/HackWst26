"""Data shapes for the user-data and matching layer.

Only what this layer produces or consumes. Sessions, payments and AI notes
belong to other people's tracks and aren't modelled here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Role = Literal["student", "tutor"]


class _Dictable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)  # type: ignore[call-overload]


@dataclass
class User(_Dictable):
    auth_sub: str
    role: Role
    name: str
    email: str
    avatar_url: str | None = None
    wallet_address: str | None = None


# ---------------------------------------------------------------------- quiz


@dataclass
class QuizOption(_Dictable):
    value: str
    label: str


@dataclass
class QuizQuestion(_Dictable):
    id: str
    prompt: str
    options: list[QuizOption] = field(default_factory=list)
    free_text: bool = False


@dataclass
class LearnerProfile(_Dictable):
    user_id: str
    subjects: list[str]
    pace: str
    goals: str
    # The natural-language sentence that gets embedded. Kept so bad matches
    # can be debugged by reading what we actually fed the model.
    profile_sentence: str


# --------------------------------------------------------------------- match


@dataclass
class TutorMatch(_Dictable):
    user: User
    bio: str
    subjects: list[str]
    hourly_rate_sol: float
    rating: float
    # 0..1 weighted blend of style similarity, subject overlap and rating.
    score: float
    # Why this tutor fits this learner. Filled by Gemini, cached in the DB.
    rationale: str = ""
    # Component scores, kept for debugging the ranking.
    style_similarity: float = 0.0
    subject_overlap: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["user"] = self.user.to_dict()
        return d
