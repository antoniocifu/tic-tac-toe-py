"""The Tic-Tac-Toe board.

The board is **immutable**: ``apply_move`` returns a new instance instead
of mutating the receiver. That keeps reasoning simple, makes history
trivial to keep around, and plays nicely with frameworks that prefer
pure functions (e.g. when reconstructing a game from its move log).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from games.domain.exceptions import (
    CellAlreadyTakenError,
    GameAlreadyFinishedError,
    OutOfBoundsError,
)
from games.domain.marks import Mark
from games.domain.rules import find_winner
from games.domain.status import Status

SIZE = 3
Row = tuple[Mark | None, Mark | None, Mark | None]
Grid = tuple[Row, Row, Row]


def _empty_grid() -> Grid:
    empty_row: Row = (None, None, None)
    return (empty_row, empty_row, empty_row)


@dataclass(frozen=True)
class Board:
    """Snapshot of a Tic-Tac-Toe game at a given point in time."""

    grid: Grid = field(default_factory=_empty_grid)
    next_mark: Mark = Mark.X

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    @classmethod
    def new(cls) -> Board:
        """Return an empty board where X plays first."""
        return cls()

    @classmethod
    def from_moves(cls, moves: list[tuple[int, int]]) -> Board:
        """Replay a list of ``(row, col)`` moves and return the result.

        Useful to rebuild a game from its persisted move log.
        """
        board = cls.new()
        for row, col in moves:
            board = board.apply_move(row, col)
        return board

    # ------------------------------------------------------------------
    # Read-only views
    # ------------------------------------------------------------------
    def cell(self, row: int, col: int) -> Mark | None:
        return self.grid[row][col]

    def as_rows(self) -> Grid:
        return self.grid

    def is_empty(self) -> bool:
        return all(cell is None for row in self.grid for cell in row)

    def is_full(self) -> bool:
        return all(cell is not None for row in self.grid for cell in row)

    @property
    def winner(self) -> Mark | None:
        return find_winner(self.grid)

    @property
    def status(self) -> Status:
        winner = self.winner
        if winner is Mark.X:
            return Status.X_WON
        if winner is Mark.O:
            return Status.O_WON
        if self.is_full():
            return Status.DRAW
        return Status.IN_PROGRESS

    # ------------------------------------------------------------------
    # Mutation (returns a new Board)
    # ------------------------------------------------------------------
    def apply_move(self, row: int, col: int) -> Board:
        if self.status.is_finished:
            raise GameAlreadyFinishedError("the game is already over")
        if not (0 <= row < SIZE and 0 <= col < SIZE):
            raise OutOfBoundsError(f"({row}, {col}) is outside the 3x3 grid")
        if self.grid[row][col] is not None:
            raise CellAlreadyTakenError(f"cell ({row}, {col}) is already taken")

        new_grid = tuple(
            tuple(self.next_mark if (r, c) == (row, col) else self.grid[r][c] for c in range(SIZE))
            for r in range(SIZE)
        )
        return Board(grid=new_grid, next_mark=self.next_mark.opponent())  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Pretty printing (handy for the CLI and for debugging)
    # ------------------------------------------------------------------
    def render(self) -> str:
        def cell(mark: Mark | None) -> str:
            return mark.value if mark else " "

        lines = [" | ".join(cell(c) for c in row) for row in self.grid]
        separator = "\n---+---+---\n".replace("---", "-" * 3)
        return separator.join(f" {line} " for line in lines)
