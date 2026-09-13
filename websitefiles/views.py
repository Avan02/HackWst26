from flask import Blueprint, render_template

views = Blueprint("views", __name__)


# Public on purpose: logout returns here, so requiring a login would send people
# straight back to the Auth0 login screen. Protect individual pages with
# `from .auth import login_required` instead.
# "/" is listed last so it registers first and becomes the canonical address -
# decorators apply bottom-up. Otherwise url_for("views.home") builds "/home".
@views.route("/home")
@views.route("/")
def home():
    return render_template("home.html")
