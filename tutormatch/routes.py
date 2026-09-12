"""TutorMatch JSON API, as a Flask Blueprint.

Brayden: register this in your Flask app with one line and every endpoint below
is available under /api/...:

    from tutormatch.routes import api
    app.register_blueprint(api)

You can also skip HTTP entirely and import the functions directly in your view
code - e.g. `from tutormatch.fixtures import QUIZ_QUESTIONS` to render the quiz
in a Jinja template. Both work.

PHASE 1 (now): every route returns fixture data, so you can build templates
before TigerData exists.
PHASE 2+: these get swapped for real implementations ONE AT A TIME so your
templates never fully break. Each route is tagged with the phase that replaces it.
"""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from .config import settings
from .fixtures import (
    MOCK_NOTES,
    MOCK_SESSION,
    MOCK_SESSION_ID,
    MOCK_STUDENT,
    QUIZ_QUESTIONS,
    mock_matches,
)
from .schemas import DownloadTicket, LearnerProfile, Payment, UploadTicket

api = Blueprint("api", __name__, url_prefix="/api")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# -------------------------------------------------------------------- health


@api.get("/health")
def health():
    """Shows which integrations are wired up yet. Handy for the whole team."""
    return jsonify(
        ok=True,
        phase="mock",
        ts=_now(),
        wired={
            "database": settings.has_db,
            "storage": settings.has_storage,
            "gemini": settings.has_gemini,
        },
    )


# ------------------------------------------------------------------------ me
# PHASE 3: JWT validation + lazy upsert into TigerData.


@api.get("/me")
def me():
    return jsonify(MOCK_STUDENT.to_dict())


# ---------------------------------------------------------------------- quiz


@api.get("/quiz/questions")
def quiz_questions():
    """Static content - already real, no phase 2 needed."""
    return jsonify([q.to_dict() for q in QUIZ_QUESTIONS])


@api.post("/quiz")
def submit_quiz():
    # PHASE 4: answers -> profile sentence -> Gemini embedding -> learner_profiles.
    body = request.get_json(silent=True) or {}
    answers = body.get("answers") or {}
    profile = LearnerProfile(
        user_id=MOCK_STUDENT.auth_sub,
        subjects=body.get("subjects") or [],
        pace=answers.get("pace", "moderate"),
        goals=answers.get("goal", ""),
        profile_sentence=(
            "Visual learner who prefers worked examples over abstract theory, "
            "moderate pace, wants to build intuition for calculus before exams."
        ),
    )
    return jsonify(profile.to_dict())


# --------------------------------------------------------------------- match
# PHASE 4: replaced by the pgvector query + cached Gemini rationales.


@api.get("/match")
def match():
    return jsonify([m.to_dict() for m in mock_matches()])


# ------------------------------------------------------------------ sessions
# PHASE 5: real rows in TigerData; room_url comes from Sam's room helper.


@api.post("/sessions")
def create_session():
    body = request.get_json(silent=True) or {}
    s = MOCK_SESSION.to_dict()
    s["tutor_id"] = body.get("tutorId", MOCK_SESSION.tutor_id)
    s["subject"] = body.get("subject", MOCK_SESSION.subject)
    s["mode"] = body.get("mode", "video")
    s["status"] = "pending"
    return jsonify(s)


@api.get("/sessions/<session_id>")
def get_session(session_id: str):
    s = MOCK_SESSION.to_dict()
    s["id"] = session_id
    return jsonify(s)


# ------------------------------------------------------------------ payments
# PHASE 5: getTransaction() against devnet, verify recipient + amount, persist.


@api.post("/payments/verify")
def verify_payment():
    body = request.get_json(silent=True) or {}
    p = Payment(
        id="mock-payment-0001",
        session_id=body.get("sessionId", MOCK_SESSION_ID),
        tx_signature=body.get("txSignature", "MockSignature" + "1" * 51),
        amount_lamports=180_000_000,
        status="confirmed",
        confirmed_at=_now(),
    )
    return jsonify(p.to_dict())


# -------------------------------------------------- recordings + AI notes


@api.post("/recordings/upload")
def recording_upload_ticket():
    """PHASE 2: real presigned PUT against Vultr Object Storage. Sam consumes this."""
    body = request.get_json(silent=True) or {}
    session_id = body.get("sessionId", MOCK_SESSION_ID)
    t = UploadTicket(
        upload_url=f"https://mock-bucket.vultrobjects.com/recordings/{session_id}.mp4?mock=true",
        object_key=f"recordings/{session_id}.mp4",
        expires_in=3600,
    )
    return jsonify(t.to_dict())


@api.get("/sessions/<session_id>/recording-url")
def recording_download_ticket(session_id: str):
    """PHASE 2: real presigned GET. Evan feeds this URL to Gemini."""
    t = DownloadTicket(
        download_url=f"https://mock-bucket.vultrobjects.com/recordings/{session_id}.mp4?mock=true",
        object_key=f"recordings/{session_id}.mp4",
        expires_in=3600,
    )
    return jsonify(t.to_dict())


@api.get("/sessions/<session_id>/notes")
def get_notes(session_id: str):
    """PHASE 5: reads session_notes. Evan writes the row; Brayden renders it."""
    n = MOCK_NOTES.to_dict()
    n["sessionId"] = session_id
    return jsonify(n)


@api.post("/sessions/<session_id>/notes")
def put_notes(session_id: str):
    """PHASE 5: Evan POSTs finished notes here and we persist them."""
    return jsonify(ok=True, persisted=False, sessionId=session_id)
