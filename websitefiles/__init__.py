import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

# Load .env from the repo root regardless of where the app was started.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    # Signs the session cookie that remembers who's logged in. It must come from
    # .env: the repo is public, so a key written here would let anyone forge a
    # session cookie and be logged in as any user.
    secret = os.getenv("AUTH0_SECRET", "").strip()
    if not secret:
        log.warning("AUTH0_SECRET is not set - using a temporary key; logins reset on restart")
        secret = secrets.token_hex(32)
    app.config["SECRET_KEY"] = secret

    from .auth import auth, init_auth
    from .views import views

    init_auth(app)
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app
