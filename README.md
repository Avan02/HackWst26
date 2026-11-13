# TutorMatch

**Built at HackWesTx 2026.** TutorMatch pairs students with the tutor who best fits how they learn. It runs the tutoring session as a live video call in the browser, then turns the recording into timestamped study notes with the Google Gemini API.

## Features

- **Learning-style matching:** Students take a six-question quiz about how they learn, covering intake style, explanations, pace, what they do when stuck, structure and goals. Each tutor is scored 0 to 1 on the same answers. PostgreSQL ranks tutors with a weighted sum filtered by subject, so matches are fast, repeatable and explainable, with no AI involved.
- **Live video sessions:** Peer-to-peer video calls run on WebRTC, with a WebSocket channel for signaling and chat. Cloudflare TURN relays keep calls working on restrictive networks like campus Wi-Fi.
- **AI session notes:** When a call ends, the recording is uploaded and processed automatically:
  1. **Extract audio:** ffmpeg pulls the audio track out of the video.
  2. **Transcribe:** Gemini returns a word-level transcript with timestamps.
  3. **Segment:** Words are grouped into readable segments, splitting at pauses over 1.2 seconds or segments longer than 15 seconds.
  4. **Summarize:** Gemini turns the segments into highlights, each with a title, a short note and the `MM:SS` range it covers. Structured output is enforced with a Pydantic schema.
  5. **Save:** The segments and highlights are stored in PostgreSQL and shown on the session's transcript page.
- **Accounts:** Login and signup use Auth0.

## Tech Stack

| Area | Tools |
| --- | --- |
| Backend | Python, FastAPI, Flask, Uvicorn |
| Video and chat | WebRTC, WebSockets, MediaRecorder, Cloudflare TURN |
| AI | Google Gemini API (`google-genai`), Pydantic |
| Audio | ffmpeg |
| Database | PostgreSQL (TigerData), psycopg, SQLAlchemy |
| Auth | Auth0 (Authlib) |

## Project Structure

```
HackWst26/
├── main.py              # Starts the Flask website (home page, Auth0 login)
├── VideoandChat.py      # FastAPI server: video calls, chat, uploads, transcript pages
├── tutormatch.py        # Data layer: database schema, quiz, tutor matching, CLI
├── ice_servers.py       # Fetches short-lived Cloudflare TURN credentials
├── Transcriber/
│   └── Transcribe.py    # Audio extraction -> transcription -> timestamped notes
├── websitefiles/        # Flask blueprints, templates and static files
├── Video_Folder/        # Saved call recordings (created at runtime)
├── requirements.txt
└── .env.example
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your PATH
- A [Gemini API key](https://aistudio.google.com/apikey)
- A PostgreSQL database (the team used [TigerData](https://www.tigerdata.com/))
- An [Auth0](https://auth0.com/) application, for login
- Optional: a Cloudflare TURN key, for calls on restrictive networks

### Setup

```bash
git clone https://github.com/Avan02/HackWst26.git
cd HackWst26
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`. `.env.example` explains each value.

| Variable | What it's for |
| --- | --- |
| `GEMINI_API_KEY` | Transcription and note generation |
| `TIGER_URL` | PostgreSQL connection string |
| `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET` | Auth0 login |
| `AUTH0_SECRET` | Session cookie key. Generate one with `openssl rand -hex 32` |
| `APP_BASE_URL`, `PORT` | Where the app runs locally |
| `CLOUDFLARE_TURN_KEY_ID`, `CLOUDFLARE_TURN_API_TOKEN` | Optional TURN relay. Without these, calls use direct connections only |

Create the tables and load the 16 sample tutors:

```bash
python tutormatch.py schema
python tutormatch.py seed
python tutormatch.py check      # Optional: shows match results for 5 test students
```

### Run

The website and the video server run as two processes:

```bash
python main.py                  # Flask website
python VideoandChat.py          # Video, chat and transcripts (port from PORT, default 8000)
```

### Run the transcriber on its own

```bash
python Transcriber/Transcribe.py path/to/video.mp4
```

This writes `session_output.json` with the transcript segments and highlights. A highlight looks like this:

```json
{
  "start_ts": "00:00",
  "end_ts": "00:15",
  "title": "Testing Code and Video Setup",
  "note": "The speaker confirms that the code is working and begins testing another video."
}
```

## Team

- [Avan02](https://github.com/Avan02): call recording, audio extraction and the Gemini transcription and notes pipeline
- [braydenA-f86](https://github.com/braydenA-f86)
- [CadenM101321](https://github.com/CadenM101321): data layer and tutor matching
