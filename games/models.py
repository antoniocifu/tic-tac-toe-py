"""Persistence layer for the game.

The board state is not stored: it is rebuilt on the fly from the move
log via :class:`games.domain.board.Board.from_moves`. ``Game.status``
and ``Game.winner`` are denormalised copies kept only to make listings
and the scoreboard cheap to query.
"""

from django.conf import settings
from django.db import models

from games.domain.marks import Mark
from games.domain.status import Status


class Game(models.Model):
    STATUS_CHOICES = [(s.value, s.value) for s in Status]

    player_x = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="games_as_x",
        on_delete=models.PROTECT,
    )
    player_o = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="games_as_o",
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=Status.IN_PROGRESS.value,
    )
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="games_won",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(player_x=models.F("player_o")),
                name="game_players_must_differ",
            ),
        ]

    def __str__(self) -> str:
        return f"Game #{self.pk} ({self.player_x} vs {self.player_o}) — {self.status}"

    # Convenience helpers used by the service / views.
    @property
    def is_finished(self) -> bool:
        return Status(self.status).is_finished

    def player_for_mark(self, mark: Mark):
        return self.player_x if mark is Mark.X else self.player_o

    def mark_for_player(self, user) -> Mark | None:
        if user == self.player_x:
            return Mark.X
        if user == self.player_o:
            return Mark.O
        return None


class Move(models.Model):
    MARK_CHOICES = [(m.value, m.value) for m in Mark]

    game = models.ForeignKey(Game, related_name="moves", on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    mark = models.CharField(max_length=1, choices=MARK_CHOICES)
    row = models.PositiveSmallIntegerField()
    col = models.PositiveSmallIntegerField()
    played_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["game", "number"], name="unique_move_number"),
            models.UniqueConstraint(fields=["game", "row", "col"], name="unique_move_cell"),
        ]

    def __str__(self) -> str:
        return (
            f"Move #{self.number} of game {self.game_id}: {self.mark} at ({self.row}, {self.col})"
        )
