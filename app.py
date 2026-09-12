"""Standalone dev server for the TutorMatch API.

Run it with:   python app.py

Brayden: you don't need this file. When your Flask app is ready, just do
`app.register_blueprint(api)` in yours and delete this one - it exists so the
API can be developed and tested before the frontend exists.
"""

from flask import Flask, jsonify

from tutormatch.config import settings
from tutormatch.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return jsonify(
            service="tutormatch-api",
            phase="mock",
            hint="Everything lives under /api - try /api/health",
            routes=sorted(
                str(r.rule) for r in app.url_map.iter_rules() if str(r.rule).startswith("/api")
            ),
        )

    return app


if __name__ == "__main__":
    create_app().run(host=settings.host, port=settings.port, debug=True)
