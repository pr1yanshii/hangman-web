# Manual Browser Tests

**Status:** Not yet performed. 0 of 18 checks have recorded results. Every row below still needs a human tester.

## How to test

- **Local:** `PORT=8000 python server.py`, then open <http://127.0.0.1:8000>
- **Deployed:** <https://hangman-web-0je9.onrender.com> (the first load after idle may take up to a minute)

Record **Pass** or **Fail** in each column you test. Add details in **Notes**, especially for failures.
Tick a matching TODO.md item only after its row here passes.

**Tester:** ____________  **Date:** ____________  **Browsers/versions:** ____________

## A. Gameplay

| # | Check | Local | Deployed | Notes |
|---|---|---|---|---|
| A1 | Win a game on Easy, Medium, and Hard. | | | |
| A2 | Lose a game on Easy, Medium, and Hard. | | | |
| A3 | A correct guess reveals the letter in every position. | | | |
| A4 | A wrong guess adds exactly one drawing part and lowers remaining attempts by 1. | | | |
| A5 | The drawing shows 0–6 parts and is complete at a loss. | | | |
| A6 | The win/loss message appears with the word. All input is disabled after the game ends. | | | |

## B. Input

| # | Check | Local | Deployed | Notes |
|---|---|---|---|---|
| B1 | The on-screen keyboard works. | | | |
| B2 | The physical keyboard works. | | | |
| B3 | Guessed keys are disabled and colored (green = correct, red = incorrect). | | | |
| B4 | Pressing an already-guessed key, a number, or a symbol does nothing. | | | |

## C. New Game

| # | Check | Local | Deployed | Notes |
|---|---|---|---|---|
| C1 | New Game resets the word, guesses, drawing, keyboard, and message with no page reload (Network tab shows only `POST /api/games`). | | | |
| C2 | Changing the difficulty and then pressing New Game starts a game at the new difficulty. | | | |

## D. Hidden Word and DevTools (Chrome → DevTools → Network → Fetch/XHR)

| # | Check | Local | Deployed | Notes |
|---|---|---|---|---|
| D1 | No `POST /api/games` or `/guess` response contains `word` while `status` is `playing`. | | | |
| D2 | `word` appears only in the response that ends the game. | | | |

## E. Error Handling

| # | Check | Local | Deployed | Notes |
|---|---|---|---|---|
| E1 | Stopping the server mid-game and guessing shows a visible "Cannot reach the server" error. | | n/a | |
| E2 | Restarting the server mid-game and guessing shows "no longer available". New Game recovers. | | n/a | |

## F. Layout and Browsers

| # | Check | Local | Deployed | Notes |
|---|---|---|---|---|
| F1 | Responsive: DevTools device toolbar at ~375px and ~768px, plus a desktop window. No horizontal scrolling. | | | |
| F2 | Works in Chrome and in Safari or Firefox (record versions above). | | | |

## Automated headless checks (not a substitute for the manual checks above)

On 2026-10-29, a Playwright script drove headless Chrome against a **local** server with fixed words
(easy `cat`, medium `python`, hard `rhythm`). It ran 36 checks and all passed. They covered:

- Starting a game on page load, and Easy/Medium/Hard via New Game.
- On-screen clicks, physical keys, duplicate keys, non-letter keys, modifier keys, and typing while the difficulty select is focused.
- The drawing advancing one part per wrong guess up to 6.
- Win and loss messages, missed letters revealed after a loss, and input disabled after the game ends.
- New Game without reload, sending only `POST /api/games`, and fully resetting the UI.
- No horizontal overflow at 375px and 768px.
- 404 after a server restart, network errors when the server is down, and no JavaScript errors.
- No hidden word in any API response or the DOM while playing.

On 2026-10-29, an HTTP script also checked the **deployed** API and passed 12 of 12 checks. It covered:

- Creating games on all three difficulties.
- Getting the current state.
- Error responses 400/404/405/409.
- No `word` field while playing, and the word revealed at game end.

Neither automated check covered Safari/Firefox, real touch devices, or visual judgment of the layout.
