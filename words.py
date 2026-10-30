"""Word list loading and random word selection by difficulty."""

import random
from pathlib import Path

DIFFICULTIES = ("easy", "medium", "hard")
DEFAULT_WORDS_DIR = Path(__file__).parent / "words"


def normalize_difficulty(difficulty):
    """Return the lowercase difficulty name, or raise ValueError if unknown."""
    if not isinstance(difficulty, str) or difficulty.lower() not in DIFFICULTIES:
        raise ValueError(f"Unknown difficulty: {difficulty!r}. Choose one of {', '.join(DIFFICULTIES)}.")
    return difficulty.lower()


class WordManager:
    """Loads the easy, medium, and hard word lists and picks random words."""

    def __init__(self, words_dir=DEFAULT_WORDS_DIR):
        words_dir = Path(words_dir)
        self._words = {d: self._load(words_dir / f"{d}.txt") for d in DIFFICULTIES}

    @staticmethod
    def _load(path):
        """Read one word per line: trim, lowercase, skip blanks, non a-z entries, and duplicates."""
        words = []
        seen = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip().lower()
            if word and word.isascii() and word.isalpha() and word not in seen:
                seen.add(word)
                words.append(word)
        if not words:
            raise ValueError(f"No valid words found in {path}")
        return words

    def words(self, difficulty):
        """Return a copy of the word list for a difficulty."""
        return list(self._words[normalize_difficulty(difficulty)])

    def random_word(self, difficulty):
        """Return a random word from the given difficulty's list."""
        return random.choice(self._words[normalize_difficulty(difficulty)])
