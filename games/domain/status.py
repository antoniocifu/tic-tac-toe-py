"""Possible outcomes of a game."""

from enum import StrEnum


class Status(StrEnum):
    IN_PROGRESS = "in_progress"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"

    @property
    def is_finished(self) -> bool:
        return self is not Status.IN_PROGRESS
