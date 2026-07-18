"""Flask server for Duck Hunter web version."""

import json
import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

SCORES_FILE = "web_scores.json"
MAX_ENTRIES = 10


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_scores(scores):
    try:
        with open(SCORES_FILE, "w") as f:
            json.dump(scores, f, indent=2)
    except (IOError, OSError):
        pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scores", methods=["GET"])
def get_scores():
    return jsonify(load_scores()[:MAX_ENTRIES])


@app.route("/api/scores", methods=["POST"])
def add_score():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    score = data.get("score", 0)
    accuracy = data.get("accuracy", 0)
    ducks = data.get("ducks", 0)
    name = data.get("name", "Anonymous")[:20]

    if not isinstance(score, (int, float)) or score < 0:
        return jsonify({"error": "Invalid score"}), 400

    scores = load_scores()
    entry = {
        "name": name,
        "score": int(score),
        "accuracy": round(accuracy, 1),
        "ducks": int(ducks),
    }
    scores.append(entry)
    scores.sort(key=lambda e: e["score"], reverse=True)
    scores = scores[:MAX_ENTRIES]
    save_scores(scores)
    return jsonify(scores)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
