"""Flask REST API for Hangman. All game logic lives in game.py."""

import json
import os
import uuid

from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

from game import DuplicateGuess, GameOver, HangmanGame, InvalidGuess
from words import WordManager, normalize_difficulty

app = Flask(__name__, static_folder="static", static_url_path="/static")
word_manager = WordManager()
games = {}  # game_id -> {"difficulty": str, "game": HangmanGame}


def game_state(game_id):
    entry = games[game_id]
    return {"game_id": game_id, "difficulty": entry["difficulty"], **entry["game"].to_dict()}


def json_body():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        abort(400, description="Request body must be a JSON object.")
    return body


def find_game(game_id):
    if game_id not in games:
        abort(404, description="Game not found.")
    return games[game_id]["game"]


@app.post("/api/games")
def create_game():
    try:
        difficulty = normalize_difficulty(json_body().get("difficulty"))
    except ValueError as e:
        abort(400, description=str(e))
    game_id = uuid.uuid4().hex
    games[game_id] = {"difficulty": difficulty, "game": HangmanGame(word_manager.random_word(difficulty))}
    return jsonify(game_state(game_id)), 201


@app.get("/api/games/<game_id>")
def get_game(game_id):
    find_game(game_id)
    return jsonify(game_state(game_id))


@app.post("/api/games/<game_id>/guess")
def guess(game_id):
    game = find_game(game_id)
    body = json_body()
    if "letter" not in body:
        abort(400, description="Missing 'letter' field.")
    try:
        game.guess(body["letter"])
    except (InvalidGuess, DuplicateGuess) as e:
        abort(400, description=str(e))
    except GameOver as e:
        abort(409, description=str(e))
    return jsonify(game_state(game_id))


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.errorhandler(HTTPException)
def handle_http_error(e):
    """Return every HTTP error (400, 404, 405, 409, 500, ...) as JSON."""
    response = e.get_response()
    response.data = json.dumps({"error": e.description})
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
