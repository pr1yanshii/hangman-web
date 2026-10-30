# Hangman Web

A web-based Hangman game for CSE 4095. A Python game engine and a Flask REST API run on the server.
A vanilla HTML/CSS/JavaScript client runs in the browser. The server is authoritative: the hidden word
is never sent to the browser until the game ends.

- **Live site:** <https://hangman-web-0je9.onrender.com>
- **Repository:** <https://github.com/pr1yanshii/hangman-web>

## Features

- Easy, Medium, and Hard word lists (`words/`).
- Six incorrect guesses allowed. Duplicate and invalid guesses are rejected without changing the game.
- On-screen and physical keyboard input, a Hangman drawing, and win/loss messages.
- New Game without reloading the page.
- A responsive layout for mobile and desktop.

## Project Structure

```
game.py            Hangman game engine (no Flask dependency)
words.py           Word list loading and random selection by difficulty
server.py          Flask app (`app`): REST API + serves the browser client
static/            index.html, style.css, app.js (browser client)
words/             easy.txt, medium.txt, hard.txt
tests/             pytest suite (engine, words, API, integration)
docs/              manual test checklist
requirements.txt   Pinned dependencies (Flask, Gunicorn, pytest)
.python-version    Python version used by Render (3.13)
```

## Local Setup

Requires Python 3.13 (3.10+ should work).

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

## REST API (summary)

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| POST | `/api/games` | `{"difficulty": "easy" \| "medium" \| "hard"}` | 201 + state | 400 |
| GET | `/api/games/<game_id>` | — | 200 + state | 404 |
| POST | `/api/games/<game_id>/guess` | `{"letter": "e"}` | 200 + state | 400 invalid/duplicate, 404, 409 game over |

The state contains `game_id`, `difficulty`, `pattern`, `guessed_letters`, `incorrect_letters`,
`remaining_guesses`, `max_incorrect`, and `status` (`playing`/`won`/`lost`). `word` is included only after the game ends.
Errors are JSON: `{"error": "..."}`.

## Deployment (Render)

1. Push this repository to GitHub.
2. In Render, choose **New → Web Service** and connect the repository.
3. Use these settings:

   | Setting | Value |
   |---|---|
   | Runtime | Python 3 |
   | Branch | `main` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn server:app --workers 1 --bind 0.0.0.0:$PORT` |
   | Instance Type | Free |

   Render sets `PORT` automatically and reads the Python version from `.python-version`. No environment variables or secrets are required.
4. Deploy, then open the `https://<service-name>.onrender.com` URL.
5. With auto-deploy enabled, every push to `main` redeploys the site.

## Limitations: In-Memory Game Storage

Games are stored in a Python dictionary inside the server process. As a result:

- **Restarts erase all games.** A deploy, crash, or restart deletes every game in progress. The browser then shows
  "This game is no longer available", and New Game starts a fresh one.
- **Free-tier spin-down.** Render's free tier stops idle services. The next visit may take up to about a minute to load,
  and any games in progress are lost.
- **One worker only.** Each Gunicorn worker is a separate process with its own memory, so a game created in one worker
  would not exist in another. The start command therefore uses `--workers 1`, and the app cannot be scaled to multiple
  instances without shared storage such as a database.
- **No cleanup.** Finished games are not removed until the server restarts. That is acceptable for a course project but
  not for long-running production use.

## Scope

This is a reduced-scope implementation of `Specification.md`. The terminal client, bots, evaluation mode, scoring,
leaderboard, and logging/replay system are intentionally not implemented. See `TODO.md` for the full plan.
