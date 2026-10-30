# TODO — Hangman Web Application (CSE 4095, Individual Assignment)

Implementation roadmap for a reduced-scope version of `Specification.md`.
The original roadmap is preserved, unchanged, in `TODO_original.md`.
Do not edit `Specification.md`. If the implementation deviates from it, record the deviation in the README.

## Scope

**In scope:** a Python game engine, word lists for three difficulties, a Flask REST API,
an HTML/CSS/vanilla-JS browser client, automated and manual testing, a GitHub repository,
public Render deployment, and the submission deliverables.

**Out of scope:** terminal clients, automated bots, evaluation mode, scoring,
leaderboards, the logging/replay system (`/log` and `/replay` endpoints, `replay.py`), and every "Future Extension" in the specification.

**"Replay" in the demo video** means playing again with New Game. It does not mean the out-of-scope replay system.

## Rules

- Do one phase at a time. Finish and test each phase before starting the next.
- Tick a box only after its tests pass or it has been verified manually.
- `game.py` must not import Flask or anything UI-related.
- The server is authoritative. The hidden word never appears in any response, DOM, or JS state while `status` is `playing`.
- All code must be original. Do not copy instructor source code. Do not commit secrets.
- The project must still run after every phase.

## API Contract (used by every phase)

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| POST | `/api/games` | `{"difficulty": "easy" \| "medium" \| "hard"}` | 201 + state | 400 invalid/missing difficulty or non-JSON body |
| GET | `/api/games/<game_id>` | — | 200 + state | 404 unknown id |
| POST | `/api/games/<game_id>/guess` | `{"letter": "e"}` | 200 + state | 400 invalid/missing letter or non-JSON body; 400 duplicate guess; 404 unknown id; 409 game already over |

**State object:** `game_id`, `difficulty`, `pattern`, `guessed_letters`, `incorrect_letters`,
`remaining_guesses`, `max_incorrect` (6), and `status` (`playing` / `won` / `lost`).
`word` is included **only** when `status` is `won` or `lost`.
**Error object:** `{"error": "<message>"}`, always JSON with `Content-Type: application/json`.

---

## Phase 1 — Project Setup and Word Management

### Tasks

- [x] Create the structure: `game.py`, `words.py`, `server.py`, `static/`, `words/`, `tests/`, `docs/`.
- [x] Add `requirements.txt` with pinned versions of `flask`, `gunicorn`, and `pytest`.
- [x] Add `.gitignore` covering `venv/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.env`, and `.DS_Store`.
- [x] Add `words/easy.txt`, `words/medium.txt`, `words/hard.txt` (one word per line, each with enough words for variety).
- [x] Implement `WordManager` in `words.py`:
  - [x] Load all three lists from `words/`.
  - [x] Lowercase and trim each word, skip blank lines, drop duplicates.
  - [x] Reject words that are not purely `a–z`.
  - [x] `random_word(difficulty)` returns a random word from that list (case-insensitive difficulty).
  - [x] Raise `ValueError` for an unknown difficulty.

### Acceptance Criteria

- `pip install -r requirements.txt` succeeds in a fresh virtualenv.
- Each of Easy, Medium, and Hard returns a valid random word. An unknown difficulty raises `ValueError`.

### Tests — `tests/test_words.py`

- [x] Each list loads, is non-empty, and contains only lowercase `a–z` words.
- [x] Duplicates, blank lines, and non-alphabetic entries are handled (use a temporary word directory).
- [x] `random_word(d)` returns a member of list `d` for each of `easy`, `medium`, `hard`.
- [x] Repeated calls can return different words (randomness, using a seeded or monkeypatched `random`).
- [x] `random_word("extreme")`, `random_word("")`, and `random_word(None)` raise `ValueError`.

### Deliverables

- `requirements.txt`, `.gitignore`, `words/*.txt`, `words.py`, `tests/test_words.py`.

---

## Phase 2 — Python Hangman Game Engine

### Tasks

- [x] Implement `HangmanGame(word, max_incorrect=6)` in `game.py` with no Flask imports.
- [x] Track correct guessed letters and incorrect letters separately, in guess order.
- [x] `guess(letter)`:
  - [x] Accept exactly one letter `a–z`, case-insensitive.
  - [x] Reject empty, multi-character, digit, symbol, whitespace, and non-string input with no change to state.
  - [x] Reject duplicate guesses (correct or incorrect) with no change to state.
  - [x] Reject any guess after the game is `won` or `lost`.
- [x] `pattern`: the masked word, e.g. `_ e _ _ e`.
- [x] `status`: `playing`, `won` (all letters revealed), or `lost` (6 incorrect guesses).
- [x] `remaining_guesses` = `max_incorrect − len(incorrect_letters)`.
- [x] `to_dict()`: the client-safe state. It includes `word` only when the game is over.
- [x] Define the exceptions `InvalidGuess`, `DuplicateGuess`, and `GameOver` for the API to map to status codes.

### Acceptance Criteria

- The engine is fully usable and testable without Flask (`grep -i flask game.py` finds nothing).
- Games are won when all letters are revealed and lost after exactly 6 incorrect guesses.
- No guess is accepted after the game ends.

### Tests — `tests/test_game.py`

- [x] A new game shows all blanks, 6 remaining guesses, empty guess lists, and `playing`.
- [x] A correct guess reveals every position of that letter (a word with repeated letters).
- [x] An incorrect guess lowers `remaining_guesses` by exactly 1 and is recorded in `incorrect_letters`.
- [x] Uppercase input is treated the same as lowercase.
- [x] Invalid input (`""`, `"ab"`, `"1"`, `"!"`, `" "`, `None`) raises `InvalidGuess` and the state is unchanged.
- [x] A duplicate correct guess and a duplicate incorrect guess both raise `DuplicateGuess` and the state is unchanged.
- [x] Win path: guessing every letter gives `won`.
- [x] Loss path: 6 wrong letters give `lost` with 0 remaining.
- [x] Winning on the last remaining life is still `won`.
- [x] Any guess after `won` or `lost` raises `GameOver`.
- [x] `to_dict()` has no `word` key while playing, and includes `word` after a win and after a loss.

### Deliverables

- `game.py`, `tests/test_game.py`.

---

## Phase 3 — Flask REST API

### Tasks

- [x] Create the Flask `app` in `server.py` using `WordManager` and `HangmanGame`.
- [x] Store games in memory in a dict keyed by a unique, unguessable ID (`secrets.token_urlsafe` or `uuid4().hex`).
- [x] Implement `POST /api/games`, `GET /api/games/<game_id>`, and `POST /api/games/<game_id>/guess` exactly as in the API Contract.
- [x] Validate JSON bodies: a missing body, non-JSON body, wrong type, or missing field returns 400.
- [x] Map `InvalidGuess`/`DuplicateGuess` to 400, `GameOver` to 409, and unknown IDs to 404.
- [x] Return a JSON 404/405 for unknown `/api/...` routes and wrong HTTP methods.
- [x] Serve `static/index.html` at `/` and static assets from `/static/`.
- [x] Read the port from the `PORT` environment variable and default to 5000. Debug mode is off in production.

### Acceptance Criteria

- A full game can be played with only `curl`.
- Every response, including errors, is JSON with the correct status code.
- Games have unique IDs and fully separate state.
- No API response contains the hidden word while the game is `playing`.

### Tests — `tests/test_api.py` (Flask test client)

- [x] `POST /api/games` for each of `easy`, `medium`, `hard` returns 201 and a valid state with `status: playing`.
- [x] An invalid difficulty, missing difficulty, empty body, or non-JSON body returns 400 with JSON `error`.
- [x] `GET` on an existing game returns 200 and its current state. On an unknown ID it returns 404.
- [x] A correct guess and an incorrect guess both return 200 with updated state.
- [x] Invalid letter → 400. Missing `letter` → 400. Duplicate → 400. Unknown game → 404. Guess after game over → 409.
- [x] Win and loss through the API (fix the word by monkeypatching `WordManager.random_word`).
- [x] Hidden-word protection: while playing, the raw body of every create, get, guess, and error response contains neither `word` nor the hidden word.
- [x] After the game ends, the response includes `word`.
- [x] Two games created back-to-back have different IDs. A guess in one does not affect the other.
- [x] Wrong method (e.g. `GET /api/games/<id>/guess`) returns 405.
- [x] `GET /` returns 200 HTML. `/static/app.js` and `/static/style.css` return 200.

### Deliverables

- `server.py`, `tests/test_api.py`, `curl` examples for the README.

---

## Phase 4 — HTML/CSS/JavaScript Browser Client

### Tasks

- [x] `static/index.html`: difficulty selector (Easy/Medium/Hard), New Game button, masked word, remaining attempts, previous guesses (correct and incorrect), Hangman drawing, and a status/message area.
- [x] `static/style.css`: a responsive layout (flex/grid and a media query) that works on mobile and desktop widths.
- [x] `static/app.js` (vanilla JS, no frameworks):
  - [x] Use `fetch()` with JSON for all three endpoints, with relative URLs so it works locally and on Render.
  - [x] Build an on-screen A–Z keyboard.
  - [x] Support physical keyboard input (letters only; ignore other keys and modifier combos).
  - [x] Disable or mark letters that have already been guessed (correct vs. incorrect styling).
  - [x] Update the masked word, remaining attempts, and previous guesses from every server response.
  - [x] Draw the Hangman in SVG or canvas, revealing one part per incorrect guess (0–6 parts).
  - [x] Show a win or loss message with the revealed word when the game ends, then disable input.
  - [x] New Game starts a fresh game with the selected difficulty **without reloading the page** and fully resets the UI.
  - [x] Show API and network errors to the user instead of failing silently.
- [x] Keep all game logic on the server. JS stores only the `game_id` and renders the server's response.

### Acceptance Criteria

- A full game can be played in the browser from start to win or loss, then restarted without a page reload.
- On-screen and physical keyboards both work.
- The hidden word is not present in JS state, the DOM, or the Network tab until the game ends.
- The layout is usable on mobile (~375px) and desktop (~1280px).

### Tests — Manual Checklist (results recorded in `docs/manual_tests.md`)

- [ ] Win a game and lose a game on each of Easy, Medium, and Hard.
- [ ] A correct guess reveals letters. A wrong guess adds a drawing part and lowers remaining attempts.
- [ ] On-screen keyboard works, physical keyboard works, and guessed keys are disabled.
- [ ] Pressing an already-guessed key or a non-letter key does nothing harmful.
- [ ] The drawing advances by exactly one part per wrong guess and is complete at a loss.
- [ ] Win and loss messages appear. Input is disabled after the game ends.
- [ ] New Game resets the word, guesses, drawing, keyboard, and message with no page reload (Network tab shows only a `POST /api/games`).
- [ ] Changing the difficulty and then pressing New Game uses the new difficulty.
- [ ] Chrome DevTools → Network: no `word` field in any response while playing. It appears only after the game ends.
- [ ] Stopping the server mid-game shows a user-visible error message.
- [ ] Responsive: DevTools device toolbar at ~375px and ~768px, plus a desktop window.
- [ ] Works in Chrome and in one other browser (Safari or Firefox).

### Deliverables

- `static/index.html`, `static/style.css`, `static/app.js`, `docs/manual_tests.md`.

---

## Phase 5 — Testing and Debugging

### Tasks

- [x] Run the full automated suite with `pytest -v`. All tests pass.
- [ ] Optional: check coverage (`pytest --cov`) and fill gaps in `game.py`, `words.py`, and `server.py`.
- [x] Add `tests/test_integration.py`: an end-to-end API flow (create → GET state → correct guess → wrong guess → win, then a separate loss → 409 on a further guess).
- [ ] Add a browser/API integration check: `GET /` serves HTML that loads `app.js`, and `app.js` calls the documented endpoints. Then re-run the full Phase 4 manual checklist against a live local server.
- [x] Fix any bugs found and add a regression test for each one. *(No application bugs found.)*
- [x] Remove debug `print` and `console.log` calls.

### Acceptance Criteria

- `pytest -v` passes with zero failures.
- All Phase 4 manual checks pass and no known bugs remain open.
- Every item in "Testing Requirements" in the rubric checklist below is covered.

### Tests

- [x] Full suite: `tests/test_words.py`, `tests/test_game.py`, `tests/test_api.py`, `tests/test_integration.py`.
- [ ] Manual checklist re-run, with results dated in `docs/manual_tests.md`.

### Deliverables

- `tests/test_integration.py`, a passing test output (screenshot or pasted into the report), and an updated `docs/manual_tests.md`.

---

## Phase 6 — GitHub and Render Deployment

### Tasks

- [ ] `git init`, make meaningful incremental commits, and push to a GitHub repository. *(Pushed to `main`; only 1 commit so far.)*
- [x] Confirm the repository contains no secrets, virtualenvs, or cache files.
- [x] Make the repository accessible to the grader (public, or shared as the course requires).
- [x] Create a Render Web Service connected to the repository:
  - [ ] Runtime: Python 3. Build command: `pip install -r requirements.txt` *(Confirm in the Render dashboard.)*
  - [ ] Start command: `gunicorn server:app --workers 1 --bind 0.0.0.0:$PORT` (one worker, because games are stored in memory) *(Confirm in the Render dashboard.)*
  - [x] Optional: pin the Python version (`.python-version` or the `PYTHON_VERSION` environment variable).
- [x] Note in the README that free-tier restarts and idle spin-down erase in-memory games and that the first load may be slow.

### Acceptance Criteria

- The public **HTTPS** Render URL (`https://<name>.onrender.com`) loads the browser client, and a full game can be won and lost there.
- The site loads in an incognito window with no login and no mixed-content warnings.
- Pushing to `main` triggers a successful redeploy.
- The GitHub repository contains all source, tests, docs, and the unchanged `Specification.md`.

### Tests

- [x] Smoke test against the deployed URL with `curl`: create a game → guess → get state.
- [x] Deployed error responses (400/404/409) match local behavior.
- [ ] Re-run the key Phase 4 checks (play, New Game, DevTools no-leak, mobile width) on the deployed site.

### Deliverables

- GitHub repository URL (source code, word lists, tests, docs) and the public HTTPS Render URL.

---

## Phase 7 — Documentation and Submission

### Tasks

- [ ] `README.md`:
  - [x] Project overview and features.
  - [x] Live Render URL and GitHub URL.
  - [ ] Tech stack and dependencies (`requirements.txt`).
  - [x] Local setup: virtualenv, install, and run (`python server.py` / `flask run`).
  - [x] How to run tests (`pytest -v`).
  - [ ] API documentation with example `curl` requests and JSON responses, including errors.
  - [ ] Game rules and the duplicate/invalid-guess and post-game behavior.
  - [x] Project structure.
  - [ ] Scope decisions: what was excluded from `Specification.md` and why. Any deviations.
  - [x] Deployment notes (Render, one worker, in-memory state).
  - [ ] Links to the report and the demo video.
- [ ] `docs/report.pdf`: a 1–2 page development report covering design and architecture, the engine/API/client split, the testing approach and results, deployment, challenges and bugs fixed, how AI tools were used, and what was learned.
  - [ ] Include 2–3 **actual** AI prompts used during development, quoted verbatim. For each one, give its purpose, what the AI produced, and how you verified or changed the result.
  - [ ] Keep a running log of real prompts during Phases 1–6 so they can be quoted accurately.
- [ ] Demo video (2–3 minutes), link in the README. It must show:
  - [ ] **Gameplay** on the live HTTPS site: all three difficulties, both keyboards, correct and incorrect guesses, and the drawing.
  - [ ] A win and a loss with their messages.
  - [ ] **Replay:** starting another game with New Game, without a page reload.
  - [ ] **Chrome DevTools → Network:** the request and response JSON for create, guess, and get state, the HTTP status codes (including one error), and proof that `word` is absent while playing.
  - [ ] Optional: a brief `pytest -v` run.
- [ ] Verify a fresh clone works by following only the README (new directory, new virtualenv).
- [ ] Final commit and push. Confirm the Render deployment is live at submission time.
- [ ] Submit every item in "Submission Requirements" below by the deadline.

### Acceptance Criteria

- A fresh clone installs, runs, and passes tests using only the README.
- Every submission requirement is present, linked, and accessible to the grader.

### Tests

- [ ] Fresh-clone run-through completed.
- [ ] Every link in the README (Render, GitHub, video, report) opens correctly in a private/incognito window.
- [ ] The report PDF is 1–2 pages and contains 2–3 actual prompts. The video is 2–3 minutes.

### Deliverables

- `README.md`, `docs/report.pdf` (with AI prompts), the demo video link, and the final submission.

---

## Rubric-Compliance Checklist

Tick an item only after it is verified.

### Required Features

- [x] Python game engine independent of Flask (`game.py`)
- [x] Random word selection (`WordManager.random_word`)
- [x] Easy, Medium, Hard difficulty
- [x] Single-letter validation
- [x] Correct and incorrect guess tracking
- [x] Six incorrect guesses allowed
- [x] Masked word display
- [x] Win/loss detection
- [x] Guesses prevented after game completion (409)
- [x] Unique game IDs and separate game states
- [x] Three REST endpoints: create, get state, guess
- [x] JSON requests and responses
- [x] Appropriate HTTP error codes (400/404/405/409)
- [x] Hidden word never exposed during active gameplay
- [x] HTML/CSS/JavaScript browser interface
- [x] Difficulty selection in the browser
- [x] On-screen keyboard input
- [x] Physical keyboard input
- [x] Previous guesses displayed
- [x] Remaining attempts displayed
- [x] Hangman drawing updated after wrong guesses
- [x] Win/loss messages
- [x] New Game without page reload
- [x] Responsive browser interface
- [x] Automated tests (pytest)
- [ ] Manual tests (documented)
- [x] GitHub repository
- [x] Public Render deployment

### Testing Requirements

- [x] All difficulty levels (words, API, browser)
- [x] Correct guesses
- [x] Incorrect guesses
- [x] Duplicate guesses
- [x] Invalid guesses
- [x] Win scenario
- [x] Loss scenario
- [x] New Game functionality
- [x] Invalid API requests (bad JSON, missing fields, unknown ID, wrong method, game over)
- [ ] Hidden-word protection (API and browser/DevTools)
- [x] Browser/API integration

### Submission Requirements

- [ ] GitHub repository with the complete source code and word lists (`words/*.txt`)
- [x] Original `Specification.md`, unchanged
- [ ] Revised `TODO.md` (original kept as `TODO_original.md`)
- [ ] `README.md`
- [x] `requirements.txt`
- [x] Public HTTPS deployment URL (Render)
- [ ] 1–2 page PDF development report
- [ ] 2–3 actual AI prompts, included in the PDF report
- [ ] 2–3 minute demonstration video: gameplay
- [ ] Demo video: replay (New Game without reload)
- [ ] Demo video: Chrome DevTools HTTP requests/responses (JSON, status codes, no hidden word while playing)

### Out of Scope (confirmed not implemented)

- [ ] No terminal client
- [ ] No automated bots
- [ ] No evaluation system
- [ ] No scoring or leaderboard
- [ ] No logging/replay system (`/log`, `/replay`, `replay.py`)
