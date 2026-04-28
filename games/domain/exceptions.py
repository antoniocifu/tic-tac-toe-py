"""Domain-level errors.

Anything that the rules of the game disallow ends up here. The web layer
maps these to HTTP responses; the CLI maps them to readable messages.
"""


class DomainError(Exception):
    """Base class for every error raised by the game's domain."""


class InvalidMoveError(DomainError):
    """Parent class for any move that breaks the rules."""


class OutOfBoundsError(InvalidMoveError):
    """The (row, column) pair falls outside the 3x3 grid."""


class CellAlreadyTakenError(InvalidMoveError):
    """The target cell already holds a mark."""


class GameAlreadyFinishedError(InvalidMoveError):
    """A move was attempted after the game ended (win or draw)."""


class NotYourTurnError(InvalidMoveError):
    """The user tried to play out of turn."""


class NotAPlayerError(DomainError):
    """The user is not part of this game."""
