"""End-to-end API flows and checks that the browser client matches the server."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

import server
from words import DIFFICULTIES

STATIC = Path(__file__).parent.parent / "static"
STATE_KEYS = {"game_id", "difficulty", "pattern", "guessed_letters", "incorrect_letters",
              "remaining_guesses", "max_incorrect", "status", "word"}


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    server.games.clear()
    with server.app.test_client() as c:
        yield c
    server.games.clear()


def post_guess(client, game_id, letter):
    return client.post(f"/api/games/{game_id}/guess", json={"letter": letter})


def hidden_word(game_id):
    return server.games[game_id]["game"]._word


def test_full_game_flow_win_then_loss(client, monkeypatch):
    monkeypatch.setattr(server.word_manager, "random_word", lambda d: "python")

    created = client.post("/api/games", json={"difficulty": "medium"})
    assert created.status_code == 201
    game_id = created.get_json()["game_id"]
    assert client.get(f"/api/games/{game_id}").get_json() == created.get_json()

    correct = post_guess(client, game_id, "p").get_json()
    assert correct["pattern"] == "p _ _ _ _ _"
    wrong = post_guess(client, game_id, "z").get_json()
    assert wrong["remaining_guesses"] == 5 and wrong["status"] == "playing"
    for letter in "ytho":
        assert "word" not in post_guess(client, game_id, letter).get_json()
    won = post_guess(client, game_id, "n").get_json()
    assert (won["status"], won["word"], won["remaining_guesses"]) == ("won", "python", 5)
    assert post_guess(client, game_id, "q").status_code == 409

    lost_id = client.post("/api/games", json={"difficulty": "easy"}).get_json()["game_id"]
    for letter in "abcdef":
        state = post_guess(client, lost_id, letter).get_json()
    assert (state["status"], state["remaining_guesses"], state["word"]) == ("lost", 0, "python")
    assert post_guess(client, lost_id, "p").status_code == 409
    assert client.get(f"/api/games/{lost_id}").get_json() == state


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_win_each_difficulty_with_real_word_lists(client, difficulty):
    game_id = client.post("/api/games", json={"difficulty": difficulty}).get_json()["game_id"]
    word = hidden_word(game_id)
    assert word in server.word_manager.words(difficulty)
    for letter in dict.fromkeys(word):
        state = post_guess(client, game_id, letter).get_json()
    assert state["status"] == "won"
    assert state["pattern"] == " ".join(word)
    assert state["remaining_guesses"] == 6


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_lose_each_difficulty_with_real_word_lists(client, difficulty):
    game_id = client.post("/api/games", json={"difficulty": difficulty}).get_json()["game_id"]
    word = hidden_word(game_id)
    wrong = [c for c in "abcdefghijklmnopqrstuvwxyz" if c not in word][:6]
    for letter in wrong:
        state = post_guess(client, game_id, letter).get_json()
        if state["status"] == "playing":
            assert word not in str(state)
    assert state["status"] == "lost"
    assert state["word"] == word


def test_new_game_after_finished_game(client, monkeypatch):
    monkeypatch.setattr(server.word_manager, "random_word", lambda d: "cat")
    first = client.post("/api/games", json={"difficulty": "easy"}).get_json()["game_id"]
    for letter in "cat":
        post_guess(client, first, letter)
    finished = client.get(f"/api/games/{first}").get_json()

    second = client.post("/api/games", json={"difficulty": "hard"}).get_json()
    assert second["game_id"] != first
    assert second["difficulty"] == "hard"
    assert second["status"] == "playing"
    assert second["guessed_letters"] == [] and second["remaining_guesses"] == 6
    assert post_guess(client, second["game_id"], "c").status_code == 200
    assert client.get(f"/api/games/{first}").get_json() == finished


# --- Browser client / API integration ---

def test_index_loads_client_assets(client):
    html = client.get("/").get_data(as_text=True)
    assert 'src="/static/app.js"' in html
    assert 'href="/static/style.css"' in html
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200


def test_every_element_id_used_by_app_js_exists_in_index():
    html = (STATIC / "index.html").read_text()
    js = (STATIC / "app.js").read_text()
    used_ids = set(re.findall(r'getElementById\("([^"]+)"\)', js))
    assert used_ids
    for element_id in used_ids:
        assert f'id="{element_id}"' in html, element_id


def test_index_has_controls_and_six_drawing_parts():
    html = (STATIC / "index.html").read_text()
    for value in DIFFICULTIES:
        assert f'<option value="{value}"' in html
    assert html.count('class="part"') == 6


def test_app_js_uses_only_documented_endpoints_and_fields():
    js = (STATIC / "app.js").read_text()
    assert "fetch(" in js
    assert '"/api/games"' in js
    assert "/api/games/${encodeURIComponent(gameId)}/guess" in js
    endpoints = set(re.findall(r'["`](/api/[^"`]*)["`]', js))
    assert endpoints <= {"/api/games", "/api/games/${encodeURIComponent(gameId)}/guess"}
    fields = set(re.findall(r"\bstate\.(\w+)", js))
    assert fields and fields <= STATE_KEYS


# --- Deployment readiness ---

def test_app_works_from_another_working_directory(tmp_path):
    """Gunicorn/Render may start the app from any directory: word lists and static files must still load."""
    project = Path(__file__).parent.parent
    script = (
        "import sys; sys.path.insert(0, sys.argv[1]); from server import app; c = app.test_client(); "
        "assert c.post('/api/games', json={'difficulty': 'hard'}).status_code == 201; "
        "assert c.get('/').status_code == 200; assert c.get('/static/app.js').status_code == 200"
    )
    result = subprocess.run([sys.executable, "-c", script, str(project)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
