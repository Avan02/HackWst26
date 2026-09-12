"""Environment configuration.

Only what the data layer needs. Auth0, Solana and storage settings belong to
whoever owns those tracks - add them in your own module rather than here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repo root regardless of where the process was started.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    """TigerData connection string, from .env."""

    tiger_url: str = os.getenv("TIGER_URL", "")

    @property
    def has_db(self) -> bool:
        return bool(self.tiger_url)


settings = Settings()
