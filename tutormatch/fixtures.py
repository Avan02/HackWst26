"""Seed data for the tutor pool.

`scripts/seed.py` loads TUTORS into TigerData and embeds each bio.
QUIZ_QUESTIONS defines the learning-style quiz whose answers become a
learner's style vector.

The teaching-style bios are deliberately DISTINCT from one another. If they all
sound alike their embeddings cluster together and the match ranking looks
arbitrary - which is the single most likely way the demo falls flat.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import QuizOption, QuizQuestion

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
