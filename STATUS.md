# TutorMatch — Status, TODOs, and Team Handoff

Last updated by Caden. Branch: `Caden-data-layer`.

This is the single place to look for: what exists, what doesn't, what each
person needs from someone else, and what the team still has to decide.

---

## 1. What the product is

Students take a short quiz about **how they learn**. They get matched to tutors
whose **teaching style** fits — not just tutors who happen to teach the subject.
They meet over video (or voice, or text), the session is recorded, and AI turns
the recording into notes with clickable timestamps so they can re-watch only the
parts that mattered.

**Stack (fixed):** Auth0 (login) · TigerData (database) · Vultr (hosting +
recording storage) · Gemini (transcripts/notes) · Solana (payment) · .tech domain

**Team:**
| Person | Owns |
|---|---|
| Brayden | Frontend (Flask + templates), Auth0, Solana payment |
| Sam | Video calls, voice calls, chat, messaging |
| Evan | Gemini — transcripts, timestamps, notes |
| Caden | User data, the database, matching students to tutors |

---

## 2. DONE — the data layer (Caden)

Working and verified against the live TigerData database. 25 checks pass,
including edge cases and SQL-injection safety.

- **Database is live.** PostgreSQL 18.6, TimescaleDB 2.30, pgvector 0.8.6.
  8 tables created. `transcript_segments` and `messages` are hypertables.
- **16 tutors seeded** across calculus, chemistry, computer science, physics,
  biology — each with a bio and a teaching-style score.
- **Learning-style quiz** — 6 questions, defined in code, ready to render.
- **Matching engine** — takes quiz answers, returns ranked tutors with a written
  explanation of why each one fits. Scores 5/5 on the test personas.
- **User storage** — `upsert_user()` creates or updates a user row. This is the
  Auth0 → database bridge.

### Files

| File | What it is |
|---|---|
| `schema.sql` | All database tables |
| `tutormatch/matching.py` | The matching engine |
| `tutormatch/db.py` | Database connection + user data functions |
| `tutormatch/fixtures.py` | The 6 quiz questions + 16 tutors |
| `tutormatch/schemas.py` | Data shapes (User, TutorMatch, etc.) |
| `tutormatch/config.py` | Reads `.env` |
| `scripts/apply_schema.py` | Creates the tables |
| `scripts/seed.py` | Loads the tutors |
| `scripts/check_match.py` | Proves matching works |

---

## 3. NOT DONE — the whole rest of the product

Be honest about this: **the data layer is the only finished piece.** As of now
there is no website, no login, no video, no payment, no AI pipeline, and nothing
is deployed anywhere.

| Piece | Owner | Status |
|---|---|---|
| Website / templates | Brayden | Not started |
| Auth0 login | Brayden | Not started |
| Solana payment | Brayden | Not started |
| Video / voice / chat | Sam | Not started |
| Recording storage | Sam | Not started |
| Gemini transcripts + notes | Evan | Not started |
| Deployment to Vultr | Caden (tentatively) | Half-written, not pushed |
| .tech domain | Nobody | Not registered |

---

## 4. WHAT EACH PERSON NEEDS TO KNOW

### → Brayden (frontend, Auth0, payment)

**You can start immediately. The data layer is ready and does not need a server
running — just import it.**

**Setup:**
```
git clone https://github.com/CadenM101321/HackWst26.git
cd HackWst26
git checkout Caden-data-layer
pip install -r requirements.txt
```
Then ask Caden for the `.env` file contents (it has the database password and is
deliberately not on GitHub).

**Render the quiz** — don't write your own questions, they're already defined:
```python
from tutormatch.fixtures import QUIZ_QUESTIONS

# Each question has: .id, .prompt, .options (list of .value/.label), .free_text
# The 'goal' question is free text - render it as a text input, not radio buttons.
```

**Get matches** — one function call:
```python
from tutormatch.matching import match_for_answers

answers = {
    "intake": "visual",            # from the quiz
    "explanation": "examples_first",
    "pace": "moderate",
    "when_stuck": "similar_example",
    "structure": "agenda",
    "goal": "understand the chain rule before my midterm",
}
sentence, matches = match_for_answers(answers, ["calculus"], limit=3)

for m in matches:
    m.user.name        # "Maya Okonkwo"
    m.user.avatar_url  # profile picture URL
    m.bio              # their teaching-style description
    m.hourly_rate_sol  # 0.18
    m.rating           # 4.9
    m.score            # 0.876
    m.rationale        # "This tutor teaches through diagrams and visuals and..."
```
`m.rationale` is the "why you matched" line for the tutor card. It's generated
from the same numbers that produced the ranking, so it's always accurate.

**Save the quiz answers** after someone completes it:
```python
from tutormatch.db import save_learner_profile
from tutormatch.matching import build_profile_sentence

save_learner_profile(
    user_id=auth0_sub,
    subjects=["calculus"],
    pace=answers["pace"],
    goals=answers["goal"],
    raw_answers=answers,
    profile_sentence=build_profile_sentence(answers, ["calculus"]),
)
```

**On login — this is the bit we have to agree on.** When someone logs in via
Auth0, call this once so they exist in the database:
```python
from tutormatch.db import upsert_user

upsert_user(
    auth_sub=token["sub"],        # Auth0's user ID, e.g. "auth0|65f1a2..."
    name=token.get("name"),
    email=token.get("email"),
    avatar_url=token.get("picture"),
)
```
Safe to call on every request — it updates rather than duplicating.

**DECISION NEEDED FROM YOU:** what exactly do you pass as `auth_sub`? It must be
Auth0's `sub` claim and it must be the *same string every time* for the same
person, or users will get duplicated. Also tell Caden the claim namespace if you
set up custom claims for roles (student vs tutor). **This is the seam most
likely to break at 2am — settle it early.**

---

### → Sam (video, voice, chat, messaging)

**Two database tables are already built and waiting for you.** Both are
TimescaleDB hypertables, which means they're optimised for time-ordered data.

```sql
messages (session_id, ts, sender_id, body)
transcript_segments (session_id, ts, start_ms, end_ms, speaker, text, embedding)
```

Use `messages` for text chat. Ask Caden for helper functions when you need them —
they're not written yet because nobody knew what shape you'd want.

**Nothing from the data layer blocks you.** Recording storage (Vultr Object
Storage) is entirely yours — Caden is not touching it.

**Suggestion, not a decision:** Daily.co's prebuilt iframe gives video, voice,
screenshare *and* text chat in one drop-in component. Voice-only is just the same
room with the camera off, so it isn't a separate feature to build. Worth 10
minutes of evaluation before building on raw WebRTC, which can eat a whole day.

**Check early:** whether recording is included on whatever plan you pick. Find
out in the first hour, not the last.

---

### → Evan (Gemini transcripts and notes)

**Your tables exist:**
```sql
session_notes (session_id, summary, key_moments, concepts, action_items, generated_at)
transcript_segments (session_id, ts, start_ms, end_ms, speaker, text, embedding)
```

**CRITICAL — timestamp format.** `key_moments` is JSON shaped like:
```json
[{"tMs": 154000, "title": "The outer/inner box diagram",
  "why": "First time the chain rule is drawn visually"}]
```
**`tMs` is MILLISECONDS, as an integer.** Not seconds. Brayden feeds this
straight to the video player's seek function. If you produce seconds and he
expects milliseconds, every timestamp jumps to the wrong place and it will not
be obvious why. **Confirm with Brayden before you build.**

**Suggestion:** Gemini accepts audio/video files directly, so you don't need a
separate speech-to-text step. Use structured output (a response schema) so you
get parseable JSON instead of prose you have to regex.

**Start against a pre-recorded sample file today.** Don't wait for Sam's
recording pipeline — the AI pipeline can't tell where a file came from, and this
also becomes the demo-day fallback if live recording fails.

---

### → Everyone

**The `.env` file is not on GitHub and never will be** — it holds the database
password. Ask Caden for it directly. `.env.example` shows what goes in it.

**Working with the repo:**
```
git checkout Caden-data-layer     # the data layer lives here
git pull                          # before you start working
```
Make your own branch for your work. Don't all commit to `main`.

---

## 5. TEAM DECISIONS NOBODY HAS MADE

These are blocking or will be soon. Someone needs to just decide.

1. **Which video service?** (Sam) — affects whether recording works at all.
2. **How deep does Solana go?** (Brayden) — a simple devnet transfer is hours;
   an escrow program is days. Recommend the simple transfer.
3. **Who registers the .tech domain?** Nobody has. It's free through
   `get.tech/hackathon` or a coupon in the hackathon Discord. Do it early —
   good names go fast and DNS takes time to propagate.
4. **Auth0 tenant** — Brayden owns it, but nobody has created it yet.
5. **Does anyone have sponsor credits?** TigerData and Vultr are both sponsors.
   Check the Discord before paying for anything.
6. **What subject does the demo use?** Pick one and make the seed data great for
   it rather than spreading thin.

---

## 6. CADEN'S REMAINING TODOs

**Blocked on other people (can't start yet):**
- Connect the quiz to Brayden's pages — needs his frontend to exist
- Verify `upsert_user()` with a real Auth0 token — needs his login to exist

**Not blocked:**
- Finish the Vultr deployment (half-written in `deploy/`, not pushed)
- Write `messages` helper functions when Sam says what he needs
- Tune the matching scores if anyone disagrees with the rankings

**How to re-run anything:**
```
python scripts/apply_schema.py   # create/update tables (safe to re-run)
python scripts/seed.py           # reload tutors (safe to re-run)
python scripts/check_match.py    # see the match rankings
```

---

## 7. KNOWN GAPS — things that are NOT verified

Be honest about these rather than discovering them on stage.

- **Nothing has ever run on a server.** Only on Caden's laptop. Deployment is
  completely untested.
- **The Auth0 → database bridge has never seen a real Auth0 token.** It works
  with made-up IDs. This is the most likely thing to break first.
- **Never tested with two people at once.** Single user only.
- **Match tuning is one person's judgment.** Caden wrote both the test personas
  and the tutor scores, so "5/5 correct" partly means he agrees with himself.
  Someone else should look at `python scripts/check_match.py` output and say
  whether it seems right.
- **All 16 tutors are fake.** There's no tutor signup flow. Fine for a demo,
  but say so if a judge asks.

---

## 8. RISKS — and what to do about them

| Risk | What to do |
|---|---|
| **Deployment left until the end** | Get *something* live on the domain early. This is the most common way hackathon teams lose. |
| **Recording pipeline doesn't work in time** | Build an "upload a file" path. Evan needs it anyway to develop against a sample, and it doubles as demo-day insurance. |
| **Venue wifi kills the live demo** | Record a backup video of the working flow the night before. Have a phone hotspot ready. |
| **The tMs units mismatch** | Brayden and Evan confirm milliseconds-vs-seconds *before* building. |
| **Auth0 `sub` inconsistency** | Brayden and Caden agree the exact claim early, or users duplicate. |
| **Everyone waiting on each other** | Each person should build against fake data first and integrate second. |

---

## 9. THE DEMO — what actually has to work

Protect this path. Everything else is optional.

1. Student logs in
2. Takes the 6-question quiz
3. **Sees 3 matched tutors with an explanation of why** ← works today
4. Books and pays
5. Joins a video call
6. Session ends, recording is processed
7. **Sees notes with clickable timestamps that jump the video** ← the money shot

Steps 3 and 7 are what judges remember. Step 3 is done. Step 7 is Evan + Brayden.

**Rehearse the whole thing twice on the real deployed site before presenting.**
