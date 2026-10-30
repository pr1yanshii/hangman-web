# Hangman Web

A web-based Hangman game built for the CSE 4095 individual assignment. A Python game engine and a Flask
REST API run on the server. A vanilla HTML/CSS/JavaScript client runs in the browser. The server is
authoritative: the hidden word is never sent to the browser until the game ends.

- **Live site:** <https://hangman-web-0je9.onrender.com>
- **Repository:** <https://github.com/pr1yanshii/hangman-web>
- **Development report:** [docs/report.pdf](docs/report.pdf)
- **Demo video:** _link to be added after recording_ (script: [docs/demo_script.md](docs/demo_script.md))

## Technology Stack

| Layer | Technology |
|---|---|
| Game engine | Python 3.13 (`game.py`, standard library only) |
| Web server / REST API | Flask 3.1 (`server.py`) |
| Production server | Gunicorn 26 (one worker) |
| Browser client | HTML, CSS, vanilla JavaScript (`fetch()`), SVG drawing |
| Tests | pytest 9 |
| Hosting | Render (free web service), GitHub |

## Game Rules

- The server picks a random word from the chosen difficulty's list.
- Guess one letter at a time (`a`–`z`, case-insensitive).
- A correct guess reveals every position of that letter. An incorrect guess adds one part to the drawing.
- Six incorrect guesses are allowed. The sixth loses the game.
- You win when every letter is revealed.
- Invalid guesses (empty, more than one character, digits, symbols) and repeated guesses are **rejected**
  and do not change the game.
- No guesses are accepted after the game ends. The word is revealed only once the game is won or lost.

### Difficulty Levels

| Level | Word list | Words | Character |
|---|---|---|---|
| Easy | `words/easy.txt` | 55 | 3–5 letter common words (e.g. *cat*, *apple*) |
| Medium | `words/medium.txt` | 55 | 6–8 letter everyday words (e.g. *garden*, *penguin*) |
| Hard | `words/hard.txt` | 55 | 4–10 letters with uncommon letters and patterns (e.g. *rhythm*, *quartz*, *xylophone*) |

Word lists are loaded at startup. Entries are trimmed and lowercased. Blank lines, duplicates, and
non-`a–z` entries are skipped.

## Project Structure

```
game.py            Hangman game engine (no Flask dependency)
words.py           Word list loading and random selection by difficulty
server.py          Flask app (`app`): REST API + serves the browser client
static/            index.html, style.css, app.js (browser client)
words/             easy.txt, medium.txt, hard.txt
tests/             pytest suite (engine, words, API, integration)
docs/              report (PDF + build_report.py source), manual test checklist, demo script
requirements.txt   Pinned dependencies (Flask, Gunicorn, pytest)
.python-version    Python version used by Render (3.13)
Specification.md   Original project specification (unchanged)
TODO.md            Revised roadmap for the reduced scope (original: TODO_original.md)
```

## Local Setup

Requires Python 3.13.

```bash
git clone https://github.com/pr1yanshii/hangman-web.git
cd hangman-web
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the server

```bash
PORT=8000 python server.py
```

Open <http://127.0.0.1:8000>. Without `PORT`, the server uses port 5000.
On macOS, port 5000 is often taken by the AirPlay Receiver, so use another port such as 8000.

To run with the same server used in production:

```bash
PORT=8000 gunicorn server:app --workers 1 --bind 127.0.0.1:8000
```

### Run the tests

```bash
pytest -v
```

The suite covers the word lists, game engine, REST API (including error codes and hidden-word protection),
and end-to-end/integration flows. The manual browser checklist is in
[docs/manual_tests.md](docs/manual_tests.md).

## REST API

All requests and responses use JSON. Errors return `{"error": "<message>"}` with an appropriate status code.
The examples below use the live site. Set `BASE=http://127.0.0.1:8000` to use a local server instead.

```bash
BASE=https://hangman-web-0je9.onrender.com
```

### Game state object

| Field | Description |
|---|---|
| `game_id` | Unique game ID (32 hex characters) |
| `difficulty` | `easy`, `medium`, or `hard` |
| `pattern` | Masked word, letters separated by spaces, e.g. `_ i _ _ _ _` |
| `guessed_letters` | Every accepted guess, correct and incorrect, in order |
| `incorrect_letters` | Accepted guesses not in the word, in order |
| `remaining_guesses` | Incorrect guesses left (6 → 0) |
| `max_incorrect` | Always 6 |
| `status` | `playing`, `won`, or `lost` |
| `word` | The hidden word. **Only present when `status` is `won` or `lost`.** |

### 1. Create a game — `POST /api/games`

```bash
curl -s -X POST "$BASE/api/games" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "medium"}'
```

`201 Created`

```json
{
  "difficulty": "medium",
  "game_id": "0fe0732b5bd7489e824fdccad5b3efb8",
  "guessed_letters": [],
  "incorrect_letters": [],
  "max_incorrect": 6,
  "pattern": "_ _ _ _ _ _",
  "remaining_guesses": 6,
  "status": "playing"
}
```

| Error | Status |
|---|---|
| Missing, empty, or non-JSON body, or `difficulty` not `easy`/`medium`/`hard` | 400 |

```json
{"error": "Unknown difficulty: 'extreme'. Choose one of easy, medium, hard."}
```

### 2. Get the current state — `GET /api/games/<game_id>`

```bash
curl -s "$BASE/api/games/0fe0732b5bd7489e824fdccad5b3efb8"
```

`200 OK`

```json
{
  "difficulty": "medium",
  "game_id": "0fe0732b5bd7489e824fdccad5b3efb8",
  "guessed_letters": ["i", "z"],
  "incorrect_letters": ["z"],
  "max_incorrect": 6,
  "pattern": "_ i _ _ _ _",
  "remaining_guesses": 5,
  "status": "playing"
}
```

| Error | Status |
|---|---|
| Unknown game ID: `{"error": "Game not found."}` | 404 |

### 3. Guess a letter — `POST /api/games/<game_id>/guess`

```bash
curl -s -X POST "$BASE/api/games/0fe0732b5bd7489e824fdccad5b3efb8/guess" \
  -H "Content-Type: application/json" \
  -d '{"letter": "i"}'
```

`200 OK` (correct guess)

```json
{
  "difficulty": "medium",
  "game_id": "0fe0732b5bd7489e824fdccad5b3efb8",
  "guessed_letters": ["i"],
  "incorrect_letters": [],
  "max_incorrect": 6,
  "pattern": "_ i _ _ _ _",
  "remaining_guesses": 6,
  "status": "playing"
}
```

When the final letter is guessed, the response includes the word:

```json
{
  "difficulty": "medium",
  "game_id": "0fe0732b5bd7489e824fdccad5b3efb8",
  "guessed_letters": ["i", "z", "t", "c", "k", "e"],
  "incorrect_letters": ["z"],
  "max_incorrect": 6,
  "pattern": "t i c k e t",
  "remaining_guesses": 5,
  "status": "won",
  "word": "ticket"
}
```

| Error | Status | Example body |
|---|---|---|
| Not exactly one letter `a`–`z` | 400 | `{"error": "Guess must be a single letter a-z."}` |
| Letter already guessed | 400 | `{"error": "'e' has already been guessed."}` |
| Missing `letter` field or non-JSON body | 400 | `{"error": "Missing 'letter' field."}` |
| Unknown game ID | 404 | `{"error": "Game not found."}` |
| Game already won or lost | 409 | `{"error": "The game is over. Start a new game."}` |
| Wrong HTTP method on an API route | 405 | JSON error with an `Allow` header |

## Deployment (Render)

The live site is deployed from the `main` branch as a Render web service.

| Setting | Value |
|---|---|
| Runtime | Python 3 (version from `.python-version`) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn server:app --workers 1 --bind 0.0.0.0:$PORT` |
| Instance Type | Free |

Render sets `PORT` automatically and serves the site over HTTPS. No environment variables or secrets are
required. With auto-deploy enabled, every push to `main` redeploys the site.

To deploy your own copy:

1. Fork or push the repository to GitHub.
2. In Render, choose **New → Web Service** and connect the repository.
3. Enter the settings above.

## Known Limitations

Games are stored in a Python dictionary inside the server process. As a result:

- **Restarts erase all games.** A deploy, crash, or restart deletes every game in progress. The browser then shows
  "This game is no longer available", and New Game starts a fresh one.
- **Free-tier spin-down.** Render's free tier stops idle services. The next visit may take up to about a minute to load,
  and any games in progress are lost.
- **One worker only.** Each Gunicorn worker is a separate process with its own memory, so a game created in one worker
  would not exist in another. The start command therefore uses `--workers 1`, and the app cannot be scaled to multiple
  instances without shared storage such as a database.
- **No cleanup.** Finished games are not removed until the server restarts.
- **No page-reload resume.** Reloading the browser starts a new game. The client does not keep the game ID between page
  loads.

## Deviations from the Specification

This is a reduced-scope implementation of [Specification.md](Specification.md), as defined in [TODO.md](TODO.md).

**Not implemented (out of scope):** the terminal client, student/reference bots, evaluation mode, scoring,
leaderboard, the logging/replay system, and the spec's "Future Extensions".

**Interpretations and additions:**

- **Duplicate guesses** are *rejected* with HTTP 400 (the spec allows "ignored or rejected").
- **Guesses after the game ends** return HTTP 409. The spec does not define this case.
- **Create game** returns `201 Created`, and every state response includes the same fields: `game_id`, `difficulty`,
  and `max_incorrect` are added to the spec's examples, plus `word` once the game ends.
- **`guessed_letters`** lists every accepted guess, correct and incorrect. The spec's example is consistent with this.
- **Difficulty** is required when creating a game, and is case-insensitive.
- **Project layout:** word loading lives in `words.py` (the spec's "Word Manager"), and tests live in `tests/`.
  There is no `terminal_client.py` or `bot_examples/` because they are out of scope.
- **Browser client:** it uses `POST /api/games` and `POST /api/games/<id>/guess`. It renders the state returned by each
  POST, so it never needs to call `GET /api/games/<id>`. That endpoint is available to any HTTP client, and it is shown
  in the demo.
