"use strict";

// Browser client for the Hangman API. All game rules live on the server:
// this file only sends requests and renders the state the server returns.

const LETTERS = "abcdefghijklmnopqrstuvwxyz";

const els = {
  form: document.getElementById("new-game-form"),
  difficulty: document.getElementById("difficulty"),
  newGame: document.getElementById("new-game"),
  error: document.getElementById("error"),
  board: document.querySelector(".board"),
  parts: document.querySelectorAll("#drawing .part"),
  drawingLabel: document.getElementById("drawing-label"),
  gameDifficulty: document.getElementById("game-difficulty"),
  pattern: document.getElementById("pattern"),
  message: document.getElementById("message"),
  remaining: document.getElementById("remaining"),
  maxIncorrect: document.getElementById("max-incorrect"),
  correct: document.getElementById("correct-letters"),
  incorrect: document.getElementById("incorrect-letters"),
  keyboard: document.getElementById("keyboard"),
};

let gameId = null;
let playing = false;
let busy = false;

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    });
  } catch {
    throw new Error("Cannot reach the server. Check your connection and try again.");
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`Unexpected response from the server (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    const error = new Error(data.error || `Request failed (HTTP ${response.status}).`);
    error.status = response.status;
    throw error;
  }
  return data;
}

function showError(text) {
  els.error.textContent = text;
  els.error.hidden = false;
}

function clearError() {
  els.error.hidden = true;
  els.error.textContent = "";
}

function setKeyboardEnabled(enabled) {
  for (const key of els.keyboard.children) {
    key.disabled = !enabled || key.classList.contains("correct") || key.classList.contains("incorrect");
  }
}

function buildKeyboard() {
  for (const letter of LETTERS) {
    const key = document.createElement("button");
    key.type = "button";
    key.className = "key";
    key.textContent = letter;
    key.dataset.letter = letter;
    key.setAttribute("aria-label", `Guess ${letter.toUpperCase()}`);
    key.disabled = true;
    key.addEventListener("click", () => submitGuess(letter));
    els.keyboard.append(key);
  }
}

function render(state) {
  playing = state.status === "playing";
  const incorrect = state.incorrect_letters;
  const correct = state.guessed_letters.filter((l) => !incorrect.includes(l));

  // Word tiles. After a loss, fill in the missed letters from the revealed word.
  els.pattern.replaceChildren();
  state.pattern.split(" ").forEach((char, i) => {
    const tile = document.createElement("span");
    tile.className = "tile";
    if (char === "_" && state.word) {
      tile.textContent = state.word[i];
      tile.classList.add("missed");
    } else {
      tile.textContent = char === "_" ? "" : char;
    }
    els.pattern.append(tile);
  });
  els.pattern.setAttribute("aria-label", `Word: ${state.pattern.replaceAll("_", "blank")}`);

  els.gameDifficulty.textContent = state.difficulty[0].toUpperCase() + state.difficulty.slice(1);
  els.remaining.textContent = state.remaining_guesses;
  els.maxIncorrect.textContent = state.max_incorrect;
  els.correct.textContent = correct.length ? correct.join(" ") : "—";
  els.incorrect.textContent = incorrect.length ? incorrect.join(" ") : "—";

  els.parts.forEach((part, i) => part.classList.toggle("shown", i < incorrect.length));
  els.drawingLabel.textContent = `Hangman drawing: ${incorrect.length} of ${els.parts.length} parts`;

  for (const key of els.keyboard.children) {
    const letter = key.dataset.letter;
    key.classList.toggle("correct", correct.includes(letter));
    key.classList.toggle("incorrect", incorrect.includes(letter));
  }
  setKeyboardEnabled(playing);

  els.board.classList.toggle("won", state.status === "won");
  els.board.classList.toggle("lost", state.status === "lost");
  els.message.className = `message ${state.status}`;
  if (state.status === "won") {
    els.message.textContent = `You won! The word was "${state.word.toUpperCase()}".`;
  } else if (state.status === "lost") {
    els.message.textContent = `You lost. The word was "${state.word.toUpperCase()}".`;
  } else {
    els.message.textContent = "";
  }
}

async function newGame() {
  if (busy) return;
  busy = true;
  clearError();
  els.newGame.disabled = true;
  setKeyboardEnabled(false);
  try {
    const state = await api("/api/games", {
      method: "POST",
      body: JSON.stringify({ difficulty: els.difficulty.value }),
    });
    gameId = state.game_id;
    render(state);
  } catch (error) {
    showError(`Could not start a new game: ${error.message}`);
    setKeyboardEnabled(playing);
  } finally {
    busy = false;
    els.newGame.disabled = false;
  }
}

async function submitGuess(letter) {
  if (!gameId || !playing || busy) return;
  const key = els.keyboard.querySelector(`[data-letter="${letter}"]`);
  if (key.disabled) return;
  busy = true;
  clearError();
  try {
    render(await api(`/api/games/${encodeURIComponent(gameId)}/guess`, {
      method: "POST",
      body: JSON.stringify({ letter }),
    }));
  } catch (error) {
    if (error.status === 404) {
      // The server no longer has this game (for example, it restarted).
      gameId = null;
      playing = false;
      setKeyboardEnabled(false);
      showError("This game is no longer available on the server. Press New Game to start again.");
    } else {
      showError(error.message);
    }
  } finally {
    busy = false;
  }
}

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  newGame();
});

document.addEventListener("keydown", (event) => {
  if (event.ctrlKey || event.metaKey || event.altKey || event.repeat) return;
  if (event.target.closest("select, input, textarea")) return;
  const letter = event.key.toLowerCase();
  if (letter.length === 1 && LETTERS.includes(letter)) {
    event.preventDefault();
    submitGuess(letter);
  }
});

buildKeyboard();
newGame();
