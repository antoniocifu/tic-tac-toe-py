"""Winning rules of the game.

Kept separate from ``Board`` so that adapting the game (different size,
different victory conditions) only requires touching this module.
"""

from collections.abc import Sequence

from games.domain.marks import Mark

Cell = tuple[int, int]
Line = tuple[Cell, Cell, Cell]


def _build_lines() -> tuple[Line, ...]:
    rows: list[Line] = [tuple((r, c) for c in range(3)) for r in range(3)]  # type: ignore[misc]
    cols: list[Line] = [tuple((r, c) for r in range(3)) for c in range(3)]  # type: ignore[misc]
    diagonals: list[Line] = [
        tuple((i, i) for i in range(3)),  # type: ignore[misc]
        tuple((i, 2 - i) for i in range(3)),  # type: ignore[misc]
    ]
    return tuple(rows + cols + diagonals)


WINNING_LINES: tuple[Line, ...] = _build_lines()


def find_winner(grid: Sequence[Sequence[Mark | None]]) -> Mark | None:
    """Return the winning mark, or ``None`` if no line is complete."""
    for line in WINNING_LINES:
        first = grid[line[0][0]][line[0][1]]
        if first is None:
            continue
        if all(grid[r][c] is first for r, c in line):
            return first
    return None
