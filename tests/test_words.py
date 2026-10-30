import random
import re

import pytest

from words import DIFFICULTIES, WordManager, normalize_difficulty


@pytest.fixture
def manager():
    return WordManager()


def write_lists(directory, easy="cat\n", medium="garden\n", hard="rhythm\n"):
    (directory / "easy.txt").write_text(easy)
    (directory / "medium.txt").write_text(medium)
    (directory / "hard.txt").write_text(hard)


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_each_list_loads_non_empty_and_lowercase_alpha(manager, difficulty):
    words = manager.words(difficulty)
    assert words
    assert all(re.fullmatch(r"[a-z]+", w) for w in words)
    assert len(words) == len(set(words))


def test_cleans_duplicates_blanks_case_and_invalid_entries(tmp_path):
    write_lists(tmp_path, easy="cat\n\n  Dog \nCAT\ndog\nice-cream\nr2d2\ncafé\n   \nsun\n")
    assert WordManager(tmp_path).words("easy") == ["cat", "dog", "sun"]


def test_list_with_no_valid_words_raises(tmp_path):
    write_lists(tmp_path, hard="\n123\n  \n")
    with pytest.raises(ValueError):
        WordManager(tmp_path)


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_random_word_comes_from_that_list(manager, difficulty):
    for _ in range(20):
        assert manager.random_word(difficulty) in manager.words(difficulty)


def test_difficulty_is_case_insensitive(manager):
    assert manager.random_word("EASY") in manager.words("easy")
    assert normalize_difficulty("Hard") == "hard"


def test_random_word_varies(manager):
    random.seed(4095)
    picks = {manager.random_word("medium") for _ in range(50)}
    assert len(picks) > 1


def test_random_word_uses_random_choice(manager, monkeypatch):
    monkeypatch.setattr(random, "choice", lambda seq: seq[-1])
    assert manager.random_word("easy") == manager.words("easy")[-1]


@pytest.mark.parametrize("bad", ["extreme", "", None, 3, " easy"])
def test_unknown_difficulty_raises(manager, bad):
    with pytest.raises(ValueError):
        manager.random_word(bad)


def test_words_returns_a_copy(manager):
    manager.words("easy").clear()
    assert manager.words("easy")
