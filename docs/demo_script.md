# Demo Video Script (target 2:30–2:50)

**Status:** Not yet recorded. Add the video link to `README.md` after uploading.

## Before Recording

1. **Wake the server.** Open <https://hangman-web-0je9.onrender.com> 2–3 minutes before recording. The free tier
   sleeps when idle, and the first load can take up to a minute.
2. **Browser setup (Chrome):**
   - Use a clean window: hide bookmarks and close other tabs.
   - Zoom to 110–125% so text is readable.
   - Open DevTools (`Cmd+Option+I` / `Ctrl+Shift+I`) and dock it to the **bottom**.
   - In the **Network** tab, select the **Fetch/XHR** filter and tick **Preserve log**.
   - Press the clear button (⊘) so the log starts empty.
3. **Console snippet.** Have this ready to paste (Console tab). On the first paste, Chrome may ask you to type
   `allow pasting`. Every call below is read-only or rejected by the server, so none of them change the game shown on screen.

   ```js
   const id = "PASTE_GAME_ID_HERE";
   const show = async (r) => console.log(r.status, await r.json());
   const guess = (letter) => fetch(`/api/games/${id}/guess`, { method: "POST",
     headers: { "Content-Type": "application/json" }, body: JSON.stringify({ letter }) }).then(show);
   ```

4. **Recorder:** on macOS, `Cmd+Shift+5` → *Record Selected Portion* (or *Entire Screen*) and enable the microphone
   under *Options*. On Windows, use the Xbox Game Bar (`Win+G`) or OBS. Record at 1080p if possible.
5. **Rehearse once** so the run fits in 3 minutes. Then reload the page and clear the Network log before the real take.

## Script

| Time | Show on screen | Say (suggested) |
|---|---|---|
| **0:00–0:15** | The live site with the HTTPS address bar visible. DevTools Network tab open. | "This is my Hangman web app for CSE 4095, deployed on Render at this HTTPS URL. The game engine is Python, the API is Flask, and the front end is plain HTML, CSS, and JavaScript." |
| **0:15–0:35** | Choose **Easy** in the difficulty menu and click **New Game**. Click the new `games` request → **Headers** (`POST`, status **201**) → **Payload** → **Preview**. | "Starting a game sends `POST /api/games` with the difficulty. The server returns 201 Created and a game ID. The pattern is all blanks, and there's no `word` field, so the hidden word never reaches the browser." |
| **0:35–0:55** | Click a likely **correct** letter on the on-screen keyboard (e.g. a vowel). Click the `guess` request → status **200** → **Preview**. | "A correct guess calls `POST /api/games/<id>/guess`. The response has the updated pattern, and the key turns green." |
| **0:55–1:10** | Type an **incorrect** letter on the physical keyboard (e.g. `Q` or `Z`). Point to the drawing part, the remaining attempts, and `incorrect_letters` in the Preview. | "The physical keyboard works too. A wrong guess adds a part to the drawing and lowers the remaining attempts from 6 to 5." |
| **1:10–1:30** | Copy `game_id` from the Preview. Open the **Console**, paste the snippet with the ID, and run `fetch(`/api/games/${id}`).then(show)`. Switch back to **Network** and show the `GET` request with status **200**. | "`GET /api/games/<id>` returns the current state. It's a read-only call, so the game on screen doesn't change." |
| **1:30–1:50** | In the Console, run `guess("<a letter already guessed>")` → **400**. Then run `fetch("/api/games/doesnotexist").then(show)` → **404**. Show both in Network. | "Errors come back as JSON with the right status codes: 400 for a repeated guess and 404 for an unknown game." |
| **1:50–2:15** | Finish the game by **winning or losing** with the keyboard. Show the message, the full drawing on a loss, and the final `guess` Preview with `status` and `word`. | "When the game ends, the server finally includes the `word`, and the page shows the result. The keyboard is now disabled." |
| **2:15–2:25** | In the Console, run `guess("m")` (any letter) → **409**. | "Guessing after the game is over returns 409 Conflict." |
| **2:25–2:45** | Choose **Hard** and click **New Game**. Show that the Network log has only a new `POST /api/games`, with no page reload, and that the board resets. | "New Game starts a fresh game at the chosen difficulty without refreshing the page. Only one API request is sent, and everything resets." |
| **2:45–2:55** | *(Optional)* Toggle the DevTools device toolbar (`Cmd+Shift+M`) for the mobile view, then show the GitHub repository. | "The layout also works on mobile. The source code, tests, and documentation are on GitHub. Thanks for watching." |

## Required Items Checklist

- [ ] Live Render site with HTTPS visible
- [ ] Choosing a difficulty and starting a game
- [ ] Correct guess
- [ ] Incorrect guess
- [ ] On-screen keyboard
- [ ] Physical keyboard
- [ ] Winning or losing, with the message
- [ ] New Game without refreshing
- [ ] Chrome DevTools Network tab open throughout
- [ ] `POST /api/games` — status 201 and JSON response
- [ ] `GET /api/games/<id>` — status 200 and JSON response
- [ ] `POST /api/games/<id>/guess` — status 200 and JSON response
- [ ] Error status codes (400, 404, 409) with JSON bodies
- [ ] No `word` field while playing. `word` appears at game end.
- [ ] Total length 2–3 minutes

## After Recording

1. Trim the start and end, and check the length is 2–3 minutes.
2. Upload it to an accessible host, such as YouTube (Unlisted) or Google Drive (*Anyone with the link can view*).
3. Open the link in a private/incognito window to confirm it plays without signing in.
4. Replace `_link to be added after recording_` in `README.md` with the URL. Tick the demo items in `TODO.md`.
