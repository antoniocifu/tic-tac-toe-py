from io import StringIO

import pytest
from django.core.management import call_command

from games.models import Game


@pytest.mark.django_db
def test_cli_can_play_a_full_game(monkeypatch):
    answers = iter(["alice", "bob", "0,0", "1,0", "0,1", "1,1", "0,2"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    stdout = StringIO()

    call_command("play", stdout=stdout)

    game = Game.objects.get()
    assert game.status == "x_won"
    assert game.winner.username == "alice"
    assert game.moves.count() == 5


@pytest.mark.django_db
def test_cli_can_abort_and_keep_progress(monkeypatch):
    answers = iter(["alice", "bob", "0,0", "q"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    stdout = StringIO()

    call_command("play", stdout=stdout)

    game = Game.objects.get()
    assert game.status == "in_progress"
    assert game.moves.count() == 1
    assert "aborted" in stdout.getvalue().lower()
