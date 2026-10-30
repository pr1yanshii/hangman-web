import copy
from pathlib import Path

import pytest

from game import LOST, PLAYING, WON, DuplicateGuess, GameOver, HangmanGame, InvalidGuess

WRONG_SIX = ["z", "q", "x", "j", "k", "v"]


def snapshot(game):
    return copy.deepcopy(game.to_dict())


def test_new_game_initial_state():
    state = HangmanGame("apple").to_dict()
    assert state == {
        "pattern": "_ _ _ _ _",
        "guessed_letters": [],
        "incorrect_letters": [],
        "remaining_guesses": 6,
        "max_incorrect": 6,
        "status": PLAYING,
    }


def test_correct_guess_reveals_every_position():
    game = HangmanGame("apple")
    assert game.guess("p") is True
    assert game.pattern == "_ p p _ _"
    assert game.remaining_guesses == 6
    assert game.correct_letters == ["p"]
    assert game.incorrect_letters == []


def test_incorrect_guess_costs_one_life_and_is_recorded():
    game = HangmanGame("apple")
    assert game.guess("z") is False
    assert game.remaining_guesses == 5
    assert game.incorrect_letters == ["z"]
    assert game.pattern == "_ _ _ _ _"


def test_guesses_recorded_in_order():
    game = HangmanGame("apple")
    for letter in "zapq":
        game.guess(letter)
    assert game.guessed_letters == ["z", "a", "p", "q"]
    assert game.correct_letters == ["a", "p"]
    assert game.incorrect_letters == ["z", "q"]


def test_uppercase_treated_as_lowercase():
    game = HangmanGame("Apple")
    game.guess("A")
    assert game.pattern == "a _ _ _ _"
    assert game.guessed_letters == ["a"]
    with pytest.raises(DuplicateGuess):
        game.guess("a")


@pytest.mark.parametrize("bad", ["", "ab", "1", "!", " ", "é", None, 5, ["a"]])
def test_invalid_input_rejected_without_state_change(bad):
    game = HangmanGame("apple")
    game.guess("z")
    before = snapshot(game)
    with pytest.raises(InvalidGuess):
        game.guess(bad)
    assert snapshot(game) == before


@pytest.mark.parametrize("letter", ["p", "z"])
def test_duplicate_guess_rejected_without_state_change(letter):
    game = HangmanGame("apple")
    game.guess(letter)
    before = snapshot(game)
    with pytest.raises(DuplicateGuess):
        game.guess(letter)
    with pytest.raises(DuplicateGuess):
        game.guess(letter.upper())
    assert snapshot(game) == before


def test_win_path():
    game = HangmanGame("apple")
    for letter in "aple":
        game.guess(letter)
    assert game.status == WON
    assert game.pattern == "a p p l e"
    assert game.remaining_guesses == 6


def test_loss_after_exactly_six_incorrect():
    game = HangmanGame("apple")
    for letter in WRONG_SIX[:5]:
        game.guess(letter)
    assert game.status == PLAYING
    assert game.remaining_guesses == 1
    game.guess(WRONG_SIX[5])
    assert game.status == LOST
    assert game.remaining_guesses == 0


def test_win_on_last_remaining_life():
    game = HangmanGame("apple")
    for letter in WRONG_SIX[:5]:
        game.guess(letter)
    for letter in "aple":
        game.guess(letter)
    assert game.status == WON
    assert game.remaining_guesses == 1


@pytest.mark.parametrize("finish", ["aple", WRONG_SIX])
@pytest.mark.parametrize("next_guess", ["b", "a", "1"])
def test_no_guess_accepted_after_game_over(finish, next_guess):
    game = HangmanGame("apple")
    for letter in finish:
        game.guess(letter)
    before = snapshot(game)
    with pytest.raises(GameOver):
        game.guess(next_guess)
    assert snapshot(game) == before


def test_word_hidden_while_playing_and_revealed_after_win():
    game = HangmanGame("apple")
    for letter in "apl":
        game.guess(letter)
        assert "word" not in game.to_dict()
        assert "apple" not in str(game.to_dict())
    game.guess("e")
    assert game.to_dict()["word"] == "apple"


def test_word_revealed_after_loss():
    game = HangmanGame("apple")
    for letter in WRONG_SIX:
        game.guess(letter)
    assert game.to_dict()["word"] == "apple"
    assert game.to_dict()["status"] == LOST


@pytest.mark.parametrize("bad_word", ["", "two words", "abc1", None])
def test_invalid_word_rejected(bad_word):
    with pytest.raises(ValueError):
        HangmanGame(bad_word)


def test_engine_does_not_depend_on_flask():
    source = (Path(__file__).parent.parent / "game.py").read_text().lower()
    assert "flask" not in source
