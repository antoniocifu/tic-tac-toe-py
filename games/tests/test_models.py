"""Smoke tests for the persistence models.

The point here is not to retest the ORM but to make sure the constraints
we declared actually fire and the small helpers work as expected.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from games.domain.marks import Mark
from games.models import Game, Move

User = get_user_model()


@pytest.fixture
def alice(db):
    return User.objects.create_user(username="alice", password="x")


@pytest.fixture
def bob(db):
    return User.objects.create_user(username="bob", password="x")


def test_a_player_cannot_play_against_themselves(alice):
    with pytest.raises(IntegrityError):
        Game.objects.create(player_x=alice, player_o=alice)


def test_mark_for_player_returns_the_right_side(alice, bob):
    game = Game.objects.create(player_x=alice, player_o=bob)

    assert game.mark_for_player(alice) is Mark.X
    assert game.mark_for_player(bob) is Mark.O
    assert game.mark_for_player(User(username="charlie")) is None


def test_two_moves_cannot_share_the_same_number(alice, bob):
    game = Game.objects.create(player_x=alice, player_o=bob)
    Move.objects.create(game=game, number=0, mark="X", row=0, col=0, played_by=alice)

    with pytest.raises(IntegrityError):
        Move.objects.create(game=game, number=0, mark="O", row=1, col=1, played_by=bob)


def test_two_moves_cannot_share_the_same_cell(alice, bob):
    game = Game.objects.create(player_x=alice, player_o=bob)
    Move.objects.create(game=game, number=0, mark="X", row=1, col=1, played_by=alice)

    with pytest.raises(IntegrityError):
        Move.objects.create(game=game, number=1, mark="O", row=1, col=1, played_by=bob)
