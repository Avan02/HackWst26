"""Environment configuration.

Everything the app needs from .env lives here, so nothing else has to touch
os.environ. Import `settings` and read attributes off it.
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
    # --- web ---
    port: int = int(os.getenv("PORT", "5000"))
    host: str = os.getenv("HOST", "0.0.0.0")

    # --- TigerData ---
    tiger_url: str = os.getenv("TIGER_URL", "")

    # --- Vultr Object Storage ---
    vultr_endpoint: str = os.getenv("VULTR_OBJ_ENDPOINT", "")
    vultr_bucket: str = os.getenv("VULTR_OBJ_BUCKET", "tutormatch")
    vultr_key: str = os.getenv("VULTR_OBJ_KEY", "")
    vultr_secret: str = os.getenv("VULTR_OBJ_SECRET", "")

    # --- Auth0 ---
    auth0_domain: str = os.getenv("AUTH0_DOMAIN", "")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "")
    auth0_claim_namespace: str = os.getenv("AUTH0_CLAIM_NAMESPACE", "https://tutormatch.tech")

    # --- Gemini ---
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # --- Solana ---
    solana_rpc_url: str = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
    platform_wallet: str = os.getenv("PLATFORM_WALLET", "")

    @property
    def has_db(self) -> bool:
        return bool(self.tiger_url)

    @property
    def has_storage(self) -> bool:
        return bool(self.vultr_endpoint and self.vultr_key and self.vultr_secret)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)


settings = Settings()
