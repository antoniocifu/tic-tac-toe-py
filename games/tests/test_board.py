"""Board tests. Pure logic, no Django involved."""

import pytest

from games.domain.board import Board
from games.domain.exceptions import (
    CellAlreadyTakenError,
    GameAlreadyFinishedError,
    OutOfBoundsError,
)
from games.domain.marks import Mark
from games.domain.status import Status


class TestNewBoard:
    def test_starts_empty(self):
        board = Board.new()
        assert board.is_empty()
        assert board.next_mark is Mark.X
        assert board.status is Status.IN_PROGRESS
        assert board.winner is None

    def test_renders_three_empty_rows(self):
        rows = Board.new().as_rows()
        assert rows == ((None, None, None),) * 3


class TestApplyMove:
    def test_first_move_places_x(self):
        board = Board.new().apply_move(0, 0)

        assert board.cell(0, 0) is Mark.X
        assert board.next_mark is Mark.O

    def test_alternates_marks(self):
        board = Board.new().apply_move(0, 0).apply_move(1, 1)

        assert board.cell(0, 0) is Mark.X
        assert board.cell(1, 1) is Mark.O
        assert board.next_mark is Mark.X

    @pytest.mark.parametrize(("row", "col"), [(-1, 0), (0, 3), (3, 3), (5, 1)])
    def test_rejects_coordinates_outside_the_board(self, row: int, col: int):
        with pytest.raises(OutOfBoundsError):
            Board.new().apply_move(row, col)

    def test_rejects_cell_already_taken(self):
        board = Board.new().apply_move(1, 1)

        with pytest.raises(CellAlreadyTakenError):
            board.apply_move(1, 1)

    def test_returns_a_new_board_each_time(self):
        original = Board.new()
        original.apply_move(0, 0)

        # Original is untouched: apply_move returns a new instance.
        assert original.is_empty()


class TestWinning:
    @pytest.mark.parametrize("row", [0, 1, 2])
    def test_horizontal_win(self, row: int):
        # X plays the chosen row; O plays harmless cells elsewhere.
        other_row = (row + 1) % 3
        board = (
            Board.new()
            .apply_move(row, 0)
            .apply_move(other_row, 0)
            .apply_move(row, 1)
            .apply_move(other_row, 1)
            .apply_move(row, 2)
        )

        assert board.winner is Mark.X
        assert board.status is Status.X_WON

    @pytest.mark.parametrize("col", [0, 1, 2])
    def test_vertical_win(self, col: int):
        other_col = (col + 1) % 3
        board = (
            Board.new()
            .apply_move(0, col)
            .apply_move(0, other_col)
            .apply_move(1, col)
            .apply_move(1, other_col)
            .apply_move(2, col)
        )

        assert board.winner is Mark.X
        assert board.status is Status.X_WON

    def test_main_diagonal_win(self):
        board = (
            Board.new()
            .apply_move(0, 0)
            .apply_move(0, 1)
            .apply_move(1, 1)
            .apply_move(0, 2)
            .apply_move(2, 2)
        )

        assert board.winner is Mark.X

    def test_anti_diagonal_win(self):
        board = (
            Board.new()
            .apply_move(0, 2)
            .apply_move(0, 0)
            .apply_move(1, 1)
            .apply_move(0, 1)
            .apply_move(2, 0)
        )

        assert board.winner is Mark.X

    def test_o_can_win(self):
        # X plays poorly and lets O complete a diagonal.
        board = (
            Board.new()
            .apply_move(0, 0)  # X
            .apply_move(0, 2)  # O
            .apply_move(1, 0)  # X
            .apply_move(1, 1)  # O
            .apply_move(0, 1)  # X
            .apply_move(2, 0)  # O wins anti-diagonal
        )

        assert board.winner is Mark.O
        assert board.status is Status.O_WON


class TestDraw:
    def test_draw_when_board_is_full_with_no_winner(self):
        # A classic draw layout:
        #  X | O | X
        # ---+---+---
        #  X | O | O
        # ---+---+---
        #  O | X | X
        moves = [
            (0, 0),  # X
            (0, 1),  # O
            (0, 2),  # X
            (1, 1),  # O
            (1, 0),  # X
            (1, 2),  # O
            (2, 1),  # X
            (2, 0),  # O
            (2, 2),  # X
        ]
        board = Board.from_moves(moves)

        assert board.winner is None
        assert board.is_full()
        assert board.status is Status.DRAW


class TestGameAlreadyFinished:
    def test_cannot_play_after_a_win(self):
        winning_board = (
            Board.new()
            .apply_move(0, 0)
            .apply_move(1, 0)
            .apply_move(0, 1)
            .apply_move(1, 1)
            .apply_move(0, 2)  # X wins top row
        )

        with pytest.raises(GameAlreadyFinishedError):
            winning_board.apply_move(2, 2)


class TestRender:
    def test_rendering_an_empty_board(self):
        rendered = Board.new().render()
        # 3 lines, each cell is a single space, separated by '|' and '---+---+---'.
        assert "|" in rendered
        assert rendered.count("\n") == 4  # 3 rows + 2 separators add 4 newlines total

    def test_rendering_after_a_few_moves(self):
        board = Board.new().apply_move(0, 0).apply_move(1, 1)
        rendered = board.render()
        assert " X " in rendered
        assert " O " in rendered
