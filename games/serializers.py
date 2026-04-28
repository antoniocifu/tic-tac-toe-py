"""DRF serializers for the games API."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from games import services
from games.models import Game, Move

User = get_user_model()


class MoveSerializer(serializers.ModelSerializer):
    played_by = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = Move
        fields = ["number", "mark", "row", "col", "played_by", "played_at"]
        read_only_fields = fields


class MoveInputSerializer(serializers.Serializer):
    """Body for ``POST /api/games/{id}/moves/``."""

    row = serializers.IntegerField(min_value=0, max_value=2)
    col = serializers.IntegerField(min_value=0, max_value=2)


class GameListSerializer(serializers.ModelSerializer):
    player_x = serializers.SlugRelatedField(read_only=True, slug_field="username")
    player_o = serializers.SlugRelatedField(read_only=True, slug_field="username")
    winner = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = Game
        fields = [
            "id",
            "player_x",
            "player_o",
            "status",
            "winner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class GameDetailSerializer(GameListSerializer):
    board = serializers.SerializerMethodField()
    next_player = serializers.SerializerMethodField()
    rendered = serializers.SerializerMethodField()

    class Meta(GameListSerializer.Meta):
        fields = [*GameListSerializer.Meta.fields, "board", "next_player", "rendered"]
        read_only_fields = fields

    def get_board(self, game: Game):
        board = services.board_for(game)
        return [[cell.value if cell else None for cell in row] for row in board.as_rows()]

    def get_next_player(self, game: Game):
        if game.is_finished:
            return None
        next_user = services.mark_to_user(game, services.board_for(game).next_mark)
        return next_user.username if next_user else None

    def get_rendered(self, game: Game):
        return services.board_for(game).render()


class GameCreateSerializer(serializers.Serializer):
    """Body for ``POST /api/games/``."""

    opponent = serializers.CharField()

    def validate_opponent(self, value: str):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("opponent not found") from exc


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=4)


class ScoreboardEntrySerializer(serializers.Serializer):
    username = serializers.CharField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    draws = serializers.IntegerField()
    games_played = serializers.IntegerField()
