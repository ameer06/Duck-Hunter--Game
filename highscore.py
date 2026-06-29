"""High score persistence – saves top scores to a JSON file."""

import json
import os

SCORES_FILE = "highscores.json"
MAX_ENTRIES = 5


def _load():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def get_scores():
    return _load()


def get_high_score():
    scores = _load()
    return scores[0]["score"] if scores else 0


def add_score(score, accuracy, ducks_shot):
    scores = _load()
    entry = {
        "score": score,
        "accuracy": round(accuracy, 1),
        "ducks": ducks_shot,
    }
    scores.append(entry)
    scores.sort(key=lambda e: e["score"], reverse=True)
    scores = scores[:MAX_ENTRIES]
    _save(scores)
    return scores
