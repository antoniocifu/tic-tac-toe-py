"""Application service: bridges the pure domain with the ORM.

Views call this module; the module never calls views. It is the single
place where a move turns from "user input" into a persisted ``Move``
and an updated ``Game``.
"""

from __future__ import annotations

from django.db import transaction

from games.domain.board import Board
from games.domain.exceptions import (
    NotAPlayerError,
    NotYourTurnError,
)
from games.domain.marks import Mark
from games.domain.status import Status
from games.models import Game, Move


def create_game(player_x, player_o) -> Game:
    """Start a new game between two distinct users."""
    if player_x == player_o:
        # The DB constraint also catches this, but failing fast gives a
        # readable error before hitting the database.
        raise ValueError("a player cannot challenge themselves")
    return Game.objects.create(player_x=player_x, player_o=player_o)


def rebuild_board(game: Game) -> Board:
    """Replay every persisted move to obtain the current board."""
    moves = game.moves.order_by("number").values_list("row", "col")
    return Board.from_moves(list(moves))


@transaction.atomic
def play_move(game: Game, user, row: int, col: int) -> Move:
    """Validate, apply and persist a move performed by ``user``.

    May raise any of the domain's :class:`InvalidMoveError` subclasses,
    plus :class:`NotYourTurnError` and :class:`NotAPlayerError`.
    """
    mark = game.mark_for_player(user)
    if mark is None:
        raise NotAPlayerError("you are not a player in this game")

    # Lock the row to prevent two concurrent moves landing at the same number.
    game = Game.objects.select_for_update().get(pk=game.pk)
    board = rebuild_board(game)

    if board.next_mark is not mark:
        raise NotYourTurnError("it is not your turn")

    new_board = board.apply_move(row, col)  # may raise domain errors

    move = Move.objects.create(
        game=game,
        number=game.moves.count(),
        mark=mark.value,
        row=row,
        col=col,
        played_by=user,
    )

    # Update denormalised status / winner.
    game.status = new_board.status.value
    if new_board.status is Status.X_WON:
        game.winner = game.player_x
    elif new_board.status is Status.O_WON:
        game.winner = game.player_o
    game.save(update_fields=["status", "winner", "updated_at"])

    return move


def board_for(game: Game) -> Board:
    """Public read-only accessor used by serializers."""
    return rebuild_board(game)


def mark_to_user(game: Game, mark: Mark | None):
    if mark is None:
        return None
    return game.player_for_mark(mark)
