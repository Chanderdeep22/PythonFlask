"""Flask & MongoDB assignment application.

/api reads a JSON list from backend_data.json.
/submit saves a validated, non-sensitive form submission to MongoDB Atlas.
"""
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "backend_data.json"

# Load a local .env only if present. Deployment environment variables take priority.
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "").strip()
app.config["MONGO_DB_NAME"] = os.getenv("MONGO_DB_NAME", "flask_mongodb_assignment").strip()
app.config["MONGO_COLLECTION_NAME"] = os.getenv(
    "MONGO_COLLECTION_NAME", "form_submissions"
).strip()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # 16 KB request limit
logging.basicConfig(level=logging.INFO)


class MongoConfigurationError(Exception):
    """Raised when MongoDB Atlas connection details are not configured."""


def save_submission(submission: dict) -> None:
    """Insert one submission into Atlas. Never logs credentials or submitted data."""
    mongo_uri = app.config.get("MONGO_URI", "")
    if not mongo_uri:
        raise MongoConfigurationError("MONGO_URI is not configured.")

    # A context-managed client is closed when the operation finishes.
    with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
        collection = client[app.config["MONGO_DB_NAME"]][
            app.config["MONGO_COLLECTION_NAME"]
        ]
        collection.insert_one(submission)


@app.get("/")
def home():
    now = datetime.now().astimezone()
    return render_template(
        "index.html",
        current_date=now.strftime("%A, %d %B %Y"),
        current_time=now.strftime("%H:%M"),
        form_data={},
        error=None,
    )


@app.get("/api")
def api():
    """Return the JSON list held in the backend data file."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as data_file:
            records = json.load(data_file)
        if not isinstance(records, list):
            app.logger.error("backend_data.json must contain a JSON list.")
            return jsonify(error="Backend data must be a JSON list."), 500
        return jsonify(records)
    except FileNotFoundError:
        app.logger.error("Backend JSON data file is missing.")
        return jsonify(error="Backend data file is missing."), 500
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Could not read backend JSON data file.")
        return jsonify(error="Backend data file could not be read."), 500


@app.post("/submit")
def submit():
    """Validate form data, save it to Atlas, and respond with redirect or inline error."""
    form_data = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "message": request.form.get("message", "").strip(),
    }
    wants_json = request.accept_mimetypes.best == "application/json"

    def error_response(message: str, status: int):
        # AJAX requests receive JSON for inline display; regular POSTs re-render this form.
        if wants_json:
            return jsonify(error=message), status
        now = datetime.now().astimezone()
        return render_template(
            "index.html",
            current_date=now.strftime("%A, %d %B %Y"),
            current_time=now.strftime("%H:%M"),
            form_data=form_data,
            error=message,
        ), status

    if not form_data["name"] or not form_data["email"]:
        return error_response("Please enter both your name and email address.", 400)

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", form_data["email"]):
        return error_response("Please enter a valid email address.", 400)

    # The assignment does not require authentication, so no password field is collected or stored.
    submission = {
        **form_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        save_submission(submission)
    except MongoConfigurationError:
        app.logger.warning("Submission rejected: MongoDB Atlas is not configured.")
        return error_response(
            "MongoDB Atlas is not configured. Add your MONGO_URI to .env and try again.", 503
        )
    except PyMongoError:
        # Do not expose the connection string or driver internals to the visitor.
        app.logger.error("MongoDB insert failed; sensitive exception details are withheld.")
        return error_response(
            "The data could not be saved. Check your Atlas connection and try again.", 503
        )

    if wants_json:
        return jsonify(redirect_url=url_for("success")), 200
    return redirect(url_for("success"), code=303)


@app.get("/success")
def success():
    return render_template("success.html")


@app.errorhandler(413)
def request_too_large(_error):
    return render_template(
        "index.html",
        current_date=datetime.now().astimezone().strftime("%A, %d %B %Y"),
        current_time=datetime.now().astimezone().strftime("%H:%M"),
        form_data={},
        error="The submitted form is too large. Please shorten the message and try again.",
    ), 413


if __name__ == "__main__":
    # Debug is disabled by default to avoid exposing interactive tracebacks.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
