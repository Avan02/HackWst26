"""Login through Auth0.

Auth0 hosts the login and sign-up forms and stores passwords - this app never
sees one. After login Auth0 sends the user back to /callback with their `sub`,
a permanent unique ID, and everything we know about them in TigerData is keyed
by it.

In views and templates:
    from .auth import login_required     # decorator for pages that need a login
    session["user"]                      # {"sub", "name", "email", "picture", "role"}
    {% if user %} ... {% endif %}        # `user` is available in every template
"""

import logging
import os
from functools import wraps
from urllib.parse import urlencode

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, redirect, request, session, url_for

from tutormatch import upsert_user

log = logging.getLogger(__name__)

auth = Blueprint("auth", __name__)
oauth = OAuth()


def _setting(name):
    return os.getenv(name, "").strip()


def init_auth(app):
    """Register the Auth0 client. The app still starts if Auth0 isn't configured."""
    oauth.init_app(app)
    domain = _setting("AUTH0_DOMAIN")
    client_id = _setting("AUTH0_CLIENT_ID")
    client_secret = _setting("AUTH0_CLIENT_SECRET")
    if not (domain and client_id and client_secret):
        log.warning("Auth0 is not configured - set AUTH0_DOMAIN, AUTH0_CLIENT_ID "
                    "and AUTH0_CLIENT_SECRET in .env")
        return
    oauth.register(
        "auth0",
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=f"https://{domain}/.well-known/openid-configuration",
    )


def _base_url():
    return _setting("APP_BASE_URL").rstrip("/")


def _external_url(endpoint):
    """Absolute URL on the app's canonical address.

    Uses APP_BASE_URL rather than the address the request arrived on, so the
    callback matches what's registered in Auth0 - including behind a proxy,
    where the request looks like it came from 127.0.0.1.
    """
    base = _base_url()
    return base + url_for(endpoint) if base else url_for(endpoint, _external=True)


def _on_wrong_host():
    """Bounce to APP_BASE_URL if the browser used a different host.

    Login stores a one-time check value in a cookie, and cookies are per-host:
    start on 127.0.0.1 but return to localhost and the check fails with a
    confusing "mismatching state" error. Starting on the right host avoids it.
    """
    base = _base_url()
    if base and request.host_url.rstrip("/") != base:
        return redirect(base + request.full_path.rstrip("?"))
    return None


def _auth0():
    return oauth.create_client("auth0")


def _not_configured():
    return ("Login isn't set up yet: add AUTH0_DOMAIN, AUTH0_CLIENT_ID and "
            "AUTH0_CLIENT_SECRET to .env and restart."), 503


@auth.route("/login")
def login():
    if session.get("user"):
        return redirect(url_for("views.home"))
    if (bounce := _on_wrong_host()) is not None:
        return bounce
    client = _auth0()
    if client is None:
        return _not_configured()
    return client.authorize_redirect(redirect_uri=_external_url("auth.callback"))


@auth.route("/signup")
def signup():
    """Same flow as login, but Auth0 opens on its sign-up tab."""
    if session.get("user"):
        return redirect(url_for("views.home"))
    if (bounce := _on_wrong_host()) is not None:
        return bounce
    client = _auth0()
    if client is None:
        return _not_configured()
    return client.authorize_redirect(
        redirect_uri=_external_url("auth.callback"), screen_hint="signup"
    )


@auth.route("/callback")
def callback():
    client = _auth0()
    if client is None:
        return _not_configured()

    token = client.authorize_access_token()
    info = token["userinfo"]

    # The link between Auth0 and TigerData: make sure this person has a row in
    # `users`, keyed by their Auth0 sub. Creates it on first login.
    row = upsert_user(
        auth_sub=info["sub"],
        name=info.get("name"),
        email=info.get("email"),
        avatar_url=info.get("picture"),
    )

    session["user"] = {
        "sub": info["sub"],
        "name": info.get("name") or info.get("email"),
        "email": info.get("email"),
        "picture": info.get("picture"),
        # Role lives in TigerData, not Auth0, so read it back from the row.
        "role": row.get("role", "student"),
    }
    return redirect(url_for("views.home"))


@auth.route("/logout")
def logout():
    session.clear()
    domain = _setting("AUTH0_DOMAIN")
    if not domain:
        return redirect(url_for("views.home"))
    # Also end the Auth0 session, or the next Login would sign straight back in.
    # returnTo must exactly match an "Allowed Logout URL" in Auth0, which is the
    # bare base URL - adding a path like /home makes Auth0 reject the logout.
    params = urlencode({
        "returnTo": _base_url() or url_for("views.home", _external=True),
        "client_id": _setting("AUTH0_CLIENT_ID"),
    })
    return redirect(f"https://{domain}/v2/logout?{params}")


def login_required(view):
    """Send people who aren't logged in to /login."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@auth.app_context_processor
def inject_user():
    """Make `user` available in every template."""
    return {"user": session.get("user")}
