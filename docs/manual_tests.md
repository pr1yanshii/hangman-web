# Manual Browser Tests

Run the server locally (`PORT=8000 python server.py`, then open <http://127.0.0.1:8000>) or use the deployed site.
Fill in the **Result** (Pass/Fail) and **Notes** columns as each check is performed by hand.

**Tester:** ____________  **Date:** ____________  **Browsers/versions:** ____________

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Win a game on Easy, Medium, and Hard. | | |
| 2 | Lose a game on Easy, Medium, and Hard. | | |
| 3 | A correct guess reveals the letter in every position. A wrong guess adds one drawing part and lowers remaining attempts by 1. | | |
| 4 | The on-screen keyboard works. | | |
| 5 | The physical keyboard works. | | |
| 6 | Guessed keys are disabled and colored (green = correct, red = incorrect). | | |
| 7 | Pressing an already-guessed key, a number, or a symbol does nothing. | | |
| 8 | The drawing shows 0–6 parts and is complete at a loss. | | |
| 9 | The win/loss message appears with the word. Input is disabled after the game ends. | | |
| 10 | New Game resets the word, guesses, drawing, keyboard, and message with no page reload (Network tab shows only `POST /api/games`). | | |
| 11 | Changing the difficulty and then pressing New Game starts a game at the new difficulty. | | |
| 12 | Chrome DevTools → Network: no `word` field in any response while playing. `word` appears only after the game ends. | | |
| 13 | Stopping the server mid-game and guessing shows a visible error message. | | |
| 14 | Restarting the server mid-game and guessing shows "no longer available". New Game recovers. | | |
| 15 | Responsive: DevTools device toolbar at ~375px and ~768px, plus a desktop window. No horizontal scrolling. | | |
| 16 | Works in Chrome. | | |
| 17 | Works in Safari or Firefox. | | |

## Automated headless checks (not a substitute for the manual checks above)

On 2026-10-29, a Playwright script drove headless Chrome against a local server
with fixed words (easy `cat`, medium `python`, hard `rhythm`). It ran 36 checks and all passed.
They covered:

- Starting a game on page load, and Easy/Medium/Hard via New Game.
- On-screen clicks, physical keys, duplicate keys, non-letter keys, modifier keys, and typing while the difficulty select is focused.
- The drawing advancing one part per wrong guess up to 6.
- Win and loss messages, missed letters revealed after a loss, and input disabled after the game ends.
- New Game without reload, sending only `POST /api/games`, and fully resetting the UI.
- No horizontal overflow at 375px and 768px.
- 404 after a server restart, network errors when the server is down, and no JavaScript errors.
- No hidden word in any API response or the DOM while playing.

Not covered by the automated checks: Safari/Firefox, real touch devices, and visual judgment of the layout.
