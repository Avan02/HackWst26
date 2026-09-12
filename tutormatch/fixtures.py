"""Fixture data.

Two jobs:
  1. The mock routes return this, so Brayden can build templates before the DB exists.
  2. `scripts/seed.py` loads TUTORS into TigerData as the real seed data.

The teaching-style bios are deliberately DISTINCT from one another. If they all
sound alike their embeddings cluster together and the match ranking looks
arbitrary - which is the single most likely way the demo falls flat.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import (
    KeyMoment,
    QuizOption,
    QuizQuestion,
    Session,
    SessionNotes,
    TutorMatch,
    User,
)

# ---------------------------------------------------------------------- quiz

QUIZ_QUESTIONS: list[QuizQuestion] = [
    QuizQuestion(
        id="intake",
        prompt="When you meet a new idea, what makes it click fastest?",
        options=[
            QuizOption("visual", "A diagram or picture of how it fits together"),
            QuizOption("verbal", "Someone talking me through it out loud"),
            QuizOption("reading", "Reading a clear written explanation"),
            QuizOption("kinesthetic", "Trying it myself and seeing what breaks"),
        ],
    ),
    QuizQuestion(
        id="explanation",
        prompt="Which explanation style do you prefer?",
        options=[
            QuizOption("examples_first", "Show me a worked example, then the rule"),
            QuizOption("theory_first", "Give me the rule, then we apply it"),
            QuizOption("analogy", "Compare it to something I already understand"),
            QuizOption("discovery", "Let me poke at it until I figure it out"),
        ],
    ),
    QuizQuestion(
        id="pace",
        prompt="What pace suits you?",
        options=[
            QuizOption("slow", "Slow and thorough - I want every step"),
            QuizOption("moderate", "Moderate - steady with room for questions"),
            QuizOption("fast", "Fast - hit the highlights, I fill gaps myself"),
        ],
    ),
    QuizQuestion(
        id="when_stuck",
        prompt="When you're stuck, what do you want your tutor to do?",
        options=[
            QuizOption("hint", "Drop a small hint and let me keep trying"),
            QuizOption("walkthrough", "Walk me through the whole thing start to finish"),
            QuizOption("socratic", "Ask me questions until I find it myself"),
            QuizOption("similar_example", "Show a similar problem solved, then I retry"),
        ],
    ),
    QuizQuestion(
        id="structure",
        prompt="How should a session be structured?",
        options=[
            QuizOption("agenda", "A clear agenda we work through"),
            QuizOption("freeform", "Freeform - I bring questions as they come"),
            QuizOption("drilling", "Lots of practice problems back to back"),
            QuizOption("discussion", "Open discussion of the underlying concepts"),
        ],
    ),
    QuizQuestion(
        id="goal",
        prompt="What are you working toward right now?",
        free_text=True,
    ),
]


# -------------------------------------------------------------------- tutors


@dataclass
class TutorFixture:
    auth_sub: str
    name: str
    email: str
    avatar_url: str
    bio: str
    subjects: list[str]
    hourly_rate_sol: float
    rating: float


TUTORS: list[TutorFixture] = [
    TutorFixture(
        "seed|tutor-01", "Maya Okonkwo", "maya@tutormatch.tech",
        "https://i.pravatar.cc/160?img=47",
        "Teaches almost entirely through diagrams. Draws the shape of a problem on a "
        "shared whiteboard before touching any algebra, and will redraw it three "
        "different ways until the picture makes the answer obvious. Best for people "
        "who need to see a thing to believe it.",
        ["calculus"], 0.18, 4.9,
    ),
    TutorFixture(
        "seed|tutor-02", "Dev Raghunathan", "dev@tutormatch.tech",
        "https://i.pravatar.cc/160?img=12",
        "Relentless problem-drilling. Expect twenty short problems in an hour, graded "
        "live, with the pattern named after each one. Not much theory talk - the "
        "belief here is that fluency comes from reps and that speed removes fear.",
        ["calculus"], 0.12, 4.6,
    ),
    TutorFixture(
        "seed|tutor-03", "Priya Venkatesan", "priya@tutormatch.tech",
        "https://i.pravatar.cc/160?img=32",
        "Socratic to a fault. Almost never gives a direct answer, instead asking "
        "narrowing questions until the student says the thing out loud themselves. "
        "Slow going at first and enormously sticky afterwards. Suits people who "
        "resent being handed answers.",
        ["calculus", "physics"], 0.20, 4.8,
    ),
    TutorFixture(
        "seed|tutor-04", "Tomas Lindqvist", "tomas@tutormatch.tech",
        "https://i.pravatar.cc/160?img=52",
        "Formal and theory-first. Starts from the definition, states the theorem, "
        "proves it, and only then works an example. Dry by design. Students who want "
        "to know why a rule is true, rather than just how to apply it, tend to stay "
        "for months.",
        ["calculus"], 0.22, 4.5,
    ),
    TutorFixture(
        "seed|tutor-05", "Rosa Delgado", "rosa@tutormatch.tech",
        "https://i.pravatar.cc/160?img=45",
        "Explains everything by analogy to ordinary life - derivatives as "
        "speedometers, integrals as filling a bathtub. Warm, chatty, low-pressure "
        "sessions aimed at students who have decided they are bad at math and need "
        "that belief dismantled before anything else.",
        ["calculus"], 0.14, 4.7,
    ),
    TutorFixture(
        "seed|tutor-06", "Ken Arai", "ken@tutormatch.tech",
        "https://i.pravatar.cc/160?img=13",
        "Structured agenda every time: five minutes reviewing last session, thirty on "
        "the new topic, twenty on mixed practice, five setting homework. Sends written "
        "notes afterward. Ideal for students who are behind and need a plan more than "
        "inspiration.",
        ["calculus", "chemistry"], 0.16, 4.8,
    ),
    TutorFixture(
        "seed|tutor-07", "Amara Boateng", "amara@tutormatch.tech",
        "https://i.pravatar.cc/160?img=26",
        "Runs chemistry as a visual molecular story - builds 3D models on screen and "
        "rotates them so students can see why a reaction goes one way and not the "
        "other. Very little rote memorisation; heavy emphasis on seeing the mechanism.",
        ["chemistry"], 0.19, 4.9,
    ),
    TutorFixture(
        "seed|tutor-08", "Colin Mbeki", "colin@tutormatch.tech",
        "https://i.pravatar.cc/160?img=14",
        "Exam-focused chemistry drilling. Works from past papers exclusively, times "
        "every question, and teaches the specific tricks markers reward. Blunt "
        "feedback. Students cramming for a date circled on the calendar do well here.",
        ["chemistry"], 0.13, 4.4,
    ),
    TutorFixture(
        "seed|tutor-09", "Hannah Weiss", "hannah@tutormatch.tech",
        "https://i.pravatar.cc/160?img=44",
        "Lab-first chemistry. Every concept arrives attached to an experiment, often "
        "demonstrated live on camera. Encourages students to predict the outcome "
        "before seeing it, then explains the gap between guess and result. Messy, "
        "memorable sessions.",
        ["chemistry"], 0.21, 4.7,
    ),
    TutorFixture(
        "seed|tutor-10", "Yusuf Karim", "yusuf@tutormatch.tech",
        "https://i.pravatar.cc/160?img=59",
        "Reads like a textbook in the best way - precise written explanations shared "
        "in the chat as the session goes, so the student leaves with a clean document. "
        "Quiet, unhurried, and excellent for learners who process by reading rather "
        "than listening.",
        ["chemistry", "biology"], 0.15, 4.6,
    ),
    TutorFixture(
        "seed|tutor-11", "Grace Sullivan", "grace@tutormatch.tech",
        "https://i.pravatar.cc/160?img=31",
        "Project-based computer science. No lectures - the student builds something "
        "small and real from minute one, and concepts get introduced only when the "
        "build demands them. Suits people who lose interest in abstractions with no "
        "payoff.",
        ["computer_science"], 0.20, 4.9,
    ),
    TutorFixture(
        "seed|tutor-12", "Emeka Nwosu", "emeka@tutormatch.tech",
        "https://i.pravatar.cc/160?img=68",
        "Whiteboards data structures as pictures - boxes, arrows, and memory laid out "
        "visually before a single line of code. Especially good at making pointers and "
        "recursion stop being terrifying. Interview-prep heavy.",
        ["computer_science"], 0.23, 4.8,
    ),
    TutorFixture(
        "seed|tutor-13", "Sofia Marchetti", "sofia@tutormatch.tech",
        "https://i.pravatar.cc/160?img=49",
        "Pair-programs the entire session with the student driving and never touches "
        "the keyboard. Asks what do you think that error means more than anything "
        "else. Frustrating for people in a hurry, transformative for people who want "
        "independence.",
        ["computer_science"], 0.17, 4.7,
    ),
    TutorFixture(
        "seed|tutor-14", "Arjun Malhotra", "arjun@tutormatch.tech",
        "https://i.pravatar.cc/160?img=56",
        "Theory-heavy computer science - complexity analysis, formal correctness, why "
        "an algorithm is optimal rather than merely working. Moves fast and assumes "
        "the student wants depth. Not the right fit for someone with a deadline "
        "tomorrow.",
        ["computer_science"], 0.25, 4.5,
    ),
    TutorFixture(
        "seed|tutor-15", "Nadia Haddad", "nadia@tutormatch.tech",
        "https://i.pravatar.cc/160?img=24",
        "Teaches programming through analogy and story - a queue is a checkout line, a "
        "hash map is a coat check. Patient with absolute beginners and deliberately "
        "avoids jargon until the idea has landed. Gentle pace, lots of encouragement.",
        ["computer_science"], 0.14, 4.8,
    ),
    TutorFixture(
        "seed|tutor-16", "Leo Fitzgerald", "leo@tutormatch.tech",
        "https://i.pravatar.cc/160?img=51",
        "Fast, high-level sessions for students who are already competent and want the "
        "last twenty percent. Skips fundamentals, talks in shorthand, and focuses on "
        "edge cases and elegance. Explicitly not for beginners.",
        ["computer_science", "calculus"], 0.26, 4.6,
    ),
]


# ---------------------------------------------------------------- mock users

MOCK_STUDENT = User(
    auth_sub="auth0|mock-student",
    role="student",
    name="Alex Rivera",
    email="alex@example.com",
    avatar_url="https://i.pravatar.cc/160?img=8",
    wallet_address="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
)

# Hand-written so the mock match screen looks like the real thing.
_MOCK_RATIONALES = {
    "seed|tutor-01": "You said diagrams make things click - Maya draws the shape of "
                     "every problem before touching the algebra.",
    "seed|tutor-05": "Rosa leans on everyday analogies and a low-pressure pace, which "
                     "fits your preference for intuition over formalism.",
    "seed|tutor-12": "Emeka whiteboards structures visually before any code, matching "
                     "how you said you take in new ideas.",
}


def mock_matches() -> list[TutorMatch]:
    picks = ["seed|tutor-01", "seed|tutor-05", "seed|tutor-12"]
    scores = [0.91, 0.84, 0.79]
    out: list[TutorMatch] = []
    for sub, score in zip(picks, scores):
        t = next(x for x in TUTORS if x.auth_sub == sub)
        out.append(
            TutorMatch(
                user=User(t.auth_sub, "tutor", t.name, t.email, t.avatar_url),
                bio=t.bio,
                subjects=t.subjects,
                hourly_rate_sol=t.hourly_rate_sol,
                rating=t.rating,
                score=score,
                rationale=_MOCK_RATIONALES[sub],
            )
        )
    return out


# -------------------------------------------------------------- mock session

MOCK_SESSION_ID = "11111111-2222-3333-4444-555555555555"

MOCK_SESSION = Session(
    id=MOCK_SESSION_ID,
    student_id=MOCK_STUDENT.auth_sub,
    tutor_id="seed|tutor-01",
    subject="calculus",
    mode="video",
    status="processed",
    room_url="https://tutormatch.daily.co/mock-room",
    recording_url="https://example.com/mock-recording.mp4",
    started_at="2026-09-12T18:00:00.000Z",
    ended_at="2026-09-12T18:42:00.000Z",
)

# Realistic notes payload. Brayden builds the recap page against this;
# Evan's pipeline must produce this exact shape.
MOCK_NOTES = SessionNotes(
    session_id=MOCK_SESSION_ID,
    summary=(
        "Worked through the chain rule, starting from why composition requires it "
        "rather than how to apply it. Alex could differentiate simple polynomials "
        "confidently but stalled whenever a function appeared inside another. Maya "
        "drew the outer box / inner box diagram three times with different examples "
        "until Alex applied it unprompted to sin(3x^2). Ended with four practice "
        "problems, three correct."
    ),
    key_moments=[
        KeyMoment(154_000, "The outer/inner box diagram",
                  "First time the chain rule is drawn visually - this is the "
                  "explanation that finally landed."),
        KeyMoment(428_000, "Alex misapplies the rule to sin(3x^2)",
                  "The inner derivative gets dropped. Worth rewatching to see exactly "
                  "where the slip happens."),
        KeyMoment(612_000, "Correction and the peel the onion rule of thumb",
                  "Maya reframes the mistake as a peeling order, which Alex repeats "
                  "back correctly."),
        KeyMoment(1_187_000, "Alex solves one unassisted",
                  "The turning point - full chain rule applied with no prompting."),
        KeyMoment(1_502_000, "Homework set and next session planned",
                  "Four problems assigned; quotient rule flagged as the next gap."),
    ],
    concepts=[
        "Chain rule",
        "Function composition",
        "Derivative of trigonometric functions",
        "Power rule (review)",
    ],
    action_items=[
        "Finish problems 3 and 4 from the practice set",
        "Rewatch 2:34 if the outer/inner split stops being obvious",
        "Come to next session with one quotient-rule question",
    ],
    generated_at="2026-09-12T18:47:12.000Z",
)
