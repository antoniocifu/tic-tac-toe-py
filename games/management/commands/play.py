from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from games import services
from games.domain.exceptions import InvalidMoveError
from games.domain.status import Status

User = get_user_model()


class Command(BaseCommand):
    help = "Play Tic-Tac-Toe from the command line"

    def add_arguments(self, parser):
        parser.add_argument("--player-x", dest="player_x")
        parser.add_argument("--player-o", dest="player_o")

    def handle(self, *args, **options):
        player_x = self._get_or_create_user(
            options.get("player_x") or input("Player X username: ").strip()
        )
        player_o = self._get_or_create_user(
            options.get("player_o") or input("Player O username: ").strip()
        )

        if player_x == player_o:
            raise CommandError("Player X and Player O must be different users.")

        game = services.create_game(player_x=player_x, player_o=player_o)
        self.stdout.write(self.style.SUCCESS(f"Started game #{game.pk}: {player_x} vs {player_o}"))
        self.stdout.write(services.board_for(game).render())

        while True:
            game.refresh_from_db()
            board = services.board_for(game)

            if board.status is Status.X_WON:
                self.stdout.write(self.style.SUCCESS(f"\n{player_x} wins as X."))
                break
            if board.status is Status.O_WON:
                self.stdout.write(self.style.SUCCESS(f"\n{player_o} wins as O."))
                break
            if board.status is Status.DRAW:
                self.stdout.write(self.style.WARNING("\nDraw."))
                break

            current_user = game.player_for_mark(board.next_mark)
            raw_move = input(
                f"\n{current_user.username} ({board.next_mark.value}) move [row,col or q]: "
            ).strip()
            if raw_move.lower() in {"q", "quit", "exit"}:
                self.stdout.write(self.style.WARNING("Game aborted. State was preserved."))
                break

            try:
                row, col = self._parse_move(raw_move)
                services.play_move(game=game, user=current_user, row=row, col=col)
            except InvalidMoveError as exc:
                self.stdout.write(self.style.ERROR(str(exc)))
                continue
            except ValueError as exc:
                self.stdout.write(self.style.ERROR(str(exc)))
                continue

            game.refresh_from_db()
            self.stdout.write("\n" + services.board_for(game).render())

    def _get_or_create_user(self, username: str):
        username = username.strip()
        if not username:
            raise CommandError("Username cannot be empty.")
        user, _ = User.objects.get_or_create(username=username)
        return user

    def _parse_move(self, raw_move: str) -> tuple[int, int]:
        try:
            row_str, col_str = (chunk.strip() for chunk in raw_move.split(",", maxsplit=1))
        except ValueError as exc:
            raise ValueError("Please enter the move as row,col (for example: 1,2).") from exc

        try:
            return int(row_str), int(col_str)
        except ValueError as exc:
            raise ValueError("Row and column must be integers.") from exc
