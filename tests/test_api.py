import pytest

import server
from words import DIFFICULTIES

# Letters p, y, t, h, o, n are not hex digits, so the word can never appear inside a game_id.
WORD = "python"
WRONG_SIX = ["a", "b", "c", "d", "e", "f"]
STATE_KEYS = {"game_id", "difficulty", "pattern", "guessed_letters", "incorrect_letters",
              "remaining_guesses", "max_incorrect", "status"}


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    server.games.clear()
    with server.app.test_client() as c:
        yield c
    server.games.clear()


@pytest.fixture
def fixed_word(monkeypatch):
    monkeypatch.setattr(server.word_manager, "random_word", lambda difficulty: WORD)


def create(client, difficulty="medium"):
    return client.post("/api/games", json={"difficulty": difficulty})


def guess(client, game_id, letter):
    return client.post(f"/api/games/{game_id}/guess", json={"letter": letter})


def assert_error(response, status):
    assert response.status_code == status
    assert response.is_json
    assert isinstance(response.get_json()["error"], str)


def assert_word_hidden(response):
    assert WORD not in response.get_data(as_text=True)
    assert "word" not in response.get_json()


# --- POST /api/games ---

@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_create_game_each_difficulty(client, difficulty):
    response = create(client, difficulty)
    assert response.status_code == 201
    assert response.is_json
    state = response.get_json()
    assert set(state) == STATE_KEYS
    assert state["difficulty"] == difficulty
    assert state["status"] == "playing"
    assert state["remaining_guesses"] == 6
    assert state["guessed_letters"] == state["incorrect_letters"] == []
    word = server.games[state["game_id"]]["game"]._word
    assert word in server.word_manager.words(difficulty)
    assert state["pattern"] == " ".join("_" * len(word))


def test_create_game_difficulty_case_insensitive(client):
    response = create(client, "HARD")
    assert response.status_code == 201
    assert response.get_json()["difficulty"] == "hard"


@pytest.mark.parametrize("body", [{"difficulty": "extreme"}, {"difficulty": ""}, {"difficulty": None},
                                  {"difficulty": 1}, {}, [], "medium"])
def test_create_game_invalid_json_body(client, body):
    assert_error(client.post("/api/games", json=body), 400)


def test_create_game_empty_body(client):
    assert_error(client.post("/api/games"), 400)


def test_create_game_non_json_body(client):
    assert_error(client.post("/api/games", data="difficulty=easy",
                             content_type="application/x-www-form-urlencoded"), 400)
    assert_error(client.post("/api/games", data="{bad json", content_type="application/json"), 400)


# --- GET /api/games/<id> ---

def test_get_game_returns_current_state(client, fixed_word):
    game_id = create(client).get_json()["game_id"]
    guess(client, game_id, "p")
    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    state = response.get_json()
    assert state["game_id"] == game_id
    assert state["pattern"] == "p _ _ _ _ _"
    assert state["guessed_letters"] == ["p"]


def test_get_unknown_game(client):
    assert_error(client.get("/api/games/doesnotexist"), 404)


# --- POST /api/games/<id>/guess ---

def test_correct_guess(client, fixed_word):
    game_id = create(client).get_json()["game_id"]
    response = guess(client, game_id, "o")
    assert response.status_code == 200
    state = response.get_json()
    assert state["pattern"] == "_ _ _ _ o _"
    assert state["guessed_letters"] == ["o"]
    assert state["incorrect_letters"] == []
    assert state["remaining_guesses"] == 6


def test_incorrect_guess(client, fixed_word):
    game_id = create(client).get_json()["game_id"]
    response = guess(client, game_id, "z")
    assert response.status_code == 200
    state = response.get_json()
    assert state["incorrect_letters"] == ["z"]
    assert state["remaining_guesses"] == 5
    assert state["status"] == "playing"


def test_uppercase_guess_accepted(client, fixed_word):
    game_id = create(client).get_json()["game_id"]
    assert guess(client, game_id, "P").get_json()["guessed_letters"] == ["p"]


@pytest.mark.parametrize("letter", ["", "ab", "1", "!", " ", None, 7, ["a"]])
def test_invalid_letter(client, fixed_word, letter):
    game_id = create(client).get_json()["game_id"]
    assert_error(guess(client, game_id, letter), 400)
    assert client.get(f"/api/games/{game_id}").get_json()["guessed_letters"] == []


@pytest.mark.parametrize("letter", ["p", "z"])
def test_duplicate_guess(client, fixed_word, letter):
    game_id = create(client).get_json()["game_id"]
    first = guess(client, game_id, letter).get_json()
    assert_error(guess(client, game_id, letter), 400)
    assert client.get(f"/api/games/{game_id}").get_json() == first


def test_missing_letter_field(client):
    game_id = create(client).get_json()["game_id"]
    assert_error(client.post(f"/api/games/{game_id}/guess", json={"guess": "a"}), 400)


def test_guess_non_json_body(client):
    game_id = create(client).get_json()["game_id"]
    assert_error(client.post(f"/api/games/{game_id}/guess"), 400)
    assert_error(client.post(f"/api/games/{game_id}/guess", data="a", content_type="text/plain"), 400)


def test_guess_unknown_game(client):
    assert_error(guess(client, "doesnotexist", "a"), 404)


def test_win_through_api(client, fixed_word):
    game_id = create(client).get_json()["game_id"]
    for letter in "pytho":
        assert guess(client, game_id, letter).get_json()["status"] == "playing"
    state = guess(client, game_id, "n").get_json()
    assert state["status"] == "won"
    assert state["pattern"] == "p y t h o n"
    assert state["word"] == WORD


def test_loss_through_api(client, fixed_word):
    game_id = create(client).get_json()["game_id"]
    for letter in WRONG_SIX[:5]:
        guess(client, game_id, letter)
    state = guess(client, game_id, WRONG_SIX[5]).get_json()
    assert state["status"] == "lost"
    assert state["remaining_guesses"] == 0
    assert state["word"] == WORD


@pytest.mark.parametrize("finish", ["python", WRONG_SIX])
def test_guess_after_game_over_returns_409(client, fixed_word, finish):
    game_id = create(client).get_json()["game_id"]
    for letter in finish:
        guess(client, game_id, letter)
    final = client.get(f"/api/games/{game_id}").get_json()
    assert final["word"] == WORD
    assert_error(guess(client, game_id, "z"), 409)
    assert client.get(f"/api/games/{game_id}").get_json() == final


# --- Hidden-word protection ---

def test_word_never_exposed_while_playing(client, fixed_word):
    response = create(client)
    assert_word_hidden(response)
    game_id = response.get_json()["game_id"]
    responses = [client.get(f"/api/games/{game_id}")]
    for letter in ["p", "a", "y", "b", "t", "h", "o"]:  # stop one letter short of winning
        responses.append(guess(client, game_id, letter))
        responses.append(client.get(f"/api/games/{game_id}"))
    responses += [guess(client, game_id, "p"), guess(client, game_id, "1"),
                  client.post(f"/api/games/{game_id}/guess", json={})]
    for r in responses:
        assert_word_hidden(r)
    assert client.get(f"/api/games/{game_id}").get_json()["status"] == "playing"


# --- Separate games ---

def test_games_have_unique_ids_and_separate_state(client, fixed_word):
    first = create(client).get_json()["game_id"]
    second = create(client).get_json()["game_id"]
    assert first != second
    guess(client, first, "p")
    guess(client, first, "z")
    other = client.get(f"/api/games/{second}").get_json()
    assert other["guessed_letters"] == []
    assert other["remaining_guesses"] == 6


def test_many_game_ids_unique(client):
    ids = {create(client).get_json()["game_id"] for _ in range(200)}
    assert len(ids) == 200


# --- Routing and error format ---

def test_wrong_method_returns_json_405(client):
    game_id = create(client).get_json()["game_id"]
    for response in [client.get(f"/api/games/{game_id}/guess"), client.get("/api/games"),
                     client.delete(f"/api/games/{game_id}")]:
        assert_error(response, 405)
        assert "Allow" in response.headers


def test_unknown_api_route_returns_json_404(client):
    assert_error(client.get("/api/nothing"), 404)


def test_index_and_static_files_served(client):
    index = client.get("/")
    assert index.status_code == 200
    assert index.mimetype == "text/html"
    for path, mimetype in [("/static/app.js", "text/javascript"), ("/static/style.css", "text/css")]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.mimetype == mimetype
