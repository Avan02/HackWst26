"""ICE servers for the video call, including Cloudflare TURN relays.

WebRTC tries to connect two browsers directly. On restrictive networks - venue
wifi, university networks - that fails, and TURN relays the media instead. The
browser chooses automatically; it just needs the list.

Cloudflare doesn't issue fixed TURN passwords. The server trades a long-lived
API token for short-lived credentials, so the token never reaches the browser.

    from ice_servers import get_ice_servers
    get_ice_servers()   # -> list for RTCPeerConnection({"iceServers": ...})
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

log = logging.getLogger(__name__)

# Used when TURN isn't configured or Cloudflare is unreachable. Direct
# connections still work on most networks - calls only lose the relay fallback.
STUN_ONLY: list[dict[str, Any]] = [
    {"urls": "stun:stun.l.google.com:19302"},
    {"urls": "stun:stun1.l.google.com:19302"},
]

_CREDENTIAL_TTL = 24 * 60 * 60          # lifetime we request from Cloudflare
_REFRESH_AFTER = _CREDENTIAL_TTL // 2   # fetch new ones well before expiry

_lock = threading.Lock()
_cached: list[dict[str, Any]] | None = None
_cached_at = 0.0


def _fetch_from_cloudflare(key_id: str, api_token: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(
        f"https://rtc.live.cloudflare.com/v1/turn/keys/{key_id}"
        "/credentials/generate-ice-servers",
        data=json.dumps({"ttl": _CREDENTIAL_TTL}).encode(),
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            # Required. Cloudflare's bot protection rejects Python's default
            # "Python-urllib" user agent with a 403 (error 1010). Without this,
            # every request fails quietly into the STUN-only fallback.
            "User-Agent": "TutorMatch/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)["iceServers"]


def get_ice_servers() -> list[dict[str, Any]]:
    """ICE servers for RTCPeerConnection. Never raises - the call page must load."""
    global _cached, _cached_at

    key_id = os.getenv("CLOUDFLARE_TURN_KEY_ID", "").strip()
    api_token = os.getenv("CLOUDFLARE_TURN_API_TOKEN", "").strip()
    if not (key_id and api_token):
        return STUN_ONLY

    with _lock:
        age = time.monotonic() - _cached_at
        if _cached and age < _REFRESH_AFTER:
            return _cached
        try:
            _cached = _fetch_from_cloudflare(key_id, api_token)
            _cached_at = time.monotonic()
            return _cached
        except Exception as err:  # any failure degrades to STUN rather than breaking calls
            log.warning("TURN credentials unavailable, using STUN only: %s", err)
            # Keep serving the last good list while its credentials are still valid.
            if _cached and age < _CREDENTIAL_TTL:
                return _cached
            return STUN_ONLY
