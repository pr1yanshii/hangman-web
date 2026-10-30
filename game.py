"""Hangman game engine. Independent of any web framework or user interface."""

import string

PLAYING = "playing"
WON = "won"
LOST = "lost"

MAX_INCORRECT = 6


class GameError(Exception):
    """Base class for rejected guesses."""


class InvalidGuess(GameError):
    """The guess is not exactly one letter a-z."""


class DuplicateGuess(GameError):
    """The letter has already been guessed."""


class GameOver(GameError):
    """The game has already been won or lost."""


class HangmanGame:
    """A single Hangman game. The hidden word is only exposed once the game ends."""

    def __init__(self, word, max_incorrect=MAX_INCORRECT):
        if not isinstance(word, str) or not word.isascii() or not word.isalpha():
            raise ValueError("Word must be a non-empty string of letters a-z.")
        self._word = word.lower()
        self.max_incorrect = max_incorrect
        self._guessed = []      # every accepted guess, in order
        self._incorrect = []    # accepted guesses not in the word, in order

    @property
    def guessed_letters(self):
        return list(self._guessed)

    @property
    def correct_letters(self):
        return [c for c in self._guessed if c not in self._incorrect]

    @property
    def incorrect_letters(self):
        return list(self._incorrect)

    @property
    def remaining_guesses(self):
        return self.max_incorrect - len(self._incorrect)

    @property
    def pattern(self):
        return " ".join(c if c in self._guessed else "_" for c in self._word)

    @property
    def status(self):
        if all(c in self._guessed for c in self._word):
            return WON
        if len(self._incorrect) >= self.max_incorrect:
            return LOST
        return PLAYING

    def guess(self, letter):
        """Apply a guess. Returns True if the letter is in the word.

        Raises GameOver, InvalidGuess, or DuplicateGuess without changing state.
        """
        if self.status != PLAYING:
            raise GameOver("The game is over. Start a new game.")
        if not isinstance(letter, str) or len(letter) != 1 or letter.lower() not in string.ascii_lowercase:
            raise InvalidGuess("Guess must be a single letter a-z.")
        letter = letter.lower()
        if letter in self._guessed:
            raise DuplicateGuess(f"'{letter}' has already been guessed.")
        self._guessed.append(letter)
        if letter in self._word:
            return True
        self._incorrect.append(letter)
        return False

    def to_dict(self):
        """Client-safe state. Includes the word only after the game has ended."""
        state = {
            "pattern": self.pattern,
            "guessed_letters": self.guessed_letters,
            "incorrect_letters": self.incorrect_letters,
            "remaining_guesses": self.remaining_guesses,
            "max_incorrect": self.max_incorrect,
            "status": self.status,
        }
        if state["status"] != PLAYING:
            state["word"] = self._word
        return state
