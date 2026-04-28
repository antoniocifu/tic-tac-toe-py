"""The two marks a player can place on the board."""

from enum import StrEnum


class Mark(StrEnum):
    """A player's mark.

    ``StrEnum`` makes the value serialize naturally to JSON and compare
    cleanly against literals like ``"X"``.
    """

    X = "X"
    O = "O"  # noqa: E741 - the letter O is part of the game's vocabulary

    def opponent(self) -> "Mark":
        return Mark.O if self is Mark.X else Mark.X
