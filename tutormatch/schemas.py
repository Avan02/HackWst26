"""Shared data shapes for TutorMatch.

This is the contract between the API (Caden), the Flask templates (Brayden),
the realtime layer (Sam) and the AI pipeline (Evan).

Everything here is a plain dataclass with a `to_dict()` so it can be dropped
straight into a Jinja template OR returned as JSON. If you need a shape
changed, change it HERE and tell the others.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Role = Literal["student", "tutor"]
SessionMode = Literal["video", "voice", "text"]
SessionStatus = Literal["pending", "paid", "live", "ended", "processed"]
PaymentStatus = Literal["pending", "confirmed", "failed"]


class _Dictable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)  # type: ignore[call-overload]


# --------------------------------------------------------------------- users


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
    # The natural-language sentence we embed. Kept so we can debug bad matches.
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
    # One-sentence Gemini explanation of why this tutor fits this learner.
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["user"] = self.user.to_dict()
        return d


# ------------------------------------------------------------------ sessions


@dataclass
class Session(_Dictable):
    id: str
    student_id: str
    tutor_id: str
    subject: str
    mode: SessionMode = "video"
    status: SessionStatus = "pending"
    room_url: str | None = None
    recording_url: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


# ------------------------------------------------------------------ payments


@dataclass
class Payment(_Dictable):
    id: str
    session_id: str
    tx_signature: str
    amount_lamports: int
    status: PaymentStatus = "pending"
    confirmed_at: str | None = None


# --------------------------------------------------------- AI / recordings


@dataclass
class KeyMoment(_Dictable):
    """A moment worth jumping to in the recording.

    `t_ms` is milliseconds from the start of the recording, as an INTEGER.
    Evan produces it; Brayden feeds it straight to the player's seek call.
    Do not change this to seconds without telling both of them.

    Serialised as `tMs` in JSON so the browser side reads naturally.
    """

    t_ms: int
    title: str
    why: str

    def to_dict(self) -> dict[str, Any]:
        return {"tMs": self.t_ms, "title": self.title, "why": self.why}


@dataclass
class SessionNotes(_Dictable):
    session_id: str
    summary: str
    key_moments: list[KeyMoment]
    concepts: list[str]
    action_items: list[str]
    generated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "summary": self.summary,
            "keyMoments": [k.to_dict() for k in self.key_moments],
            "concepts": self.concepts,
            "actionItems": self.action_items,
            "generatedAt": self.generated_at,
        }


@dataclass
class TranscriptSegment(_Dictable):
    session_id: str
    start_ms: int
    end_ms: int
    speaker: str
    text: str


@dataclass
class UploadTicket(_Dictable):
    """A presigned PUT to Vultr Object Storage. Sam uploads recordings with this."""

    upload_url: str
    object_key: str
    expires_in: int


@dataclass
class DownloadTicket(_Dictable):
    """A presigned GET. Evan feeds this URL to Gemini."""

    download_url: str
    object_key: str
    expires_in: int
