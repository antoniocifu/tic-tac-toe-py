"""HTTP views for the games API."""

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games import services
from games.domain.status import Status
from games.models import Game
from games.serializers import (
    GameCreateSerializer,
    GameDetailSerializer,
    GameListSerializer,
    MoveInputSerializer,
    MoveSerializer,
    ScoreboardEntrySerializer,
)

User = get_user_model()


class GameViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """List your games, peek into one, create one or play a move."""

    def get_queryset(self):
        user = self.request.user
        return Game.objects.filter(Q(player_x=user) | Q(player_o=user)).select_related(
            "player_x", "player_o", "winner"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return GameCreateSerializer
        if self.action == "retrieve":
            return GameDetailSerializer
        return GameListSerializer

    def create(self, request, *args, **kwargs):
        serializer = GameCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        opponent = serializer.validated_data["opponent"]
        game = services.create_game(player_x=request.user, player_o=opponent)
        return Response(GameDetailSerializer(game).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="moves")
    def moves(self, request, pk=None):
        game = self.get_object()
        if request.method == "GET":
            return Response(MoveSerializer(game.moves.all(), many=True).data)

        body = MoveInputSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        move = services.play_move(
            game=game,
            user=request.user,
            row=body.validated_data["row"],
            col=body.validated_data["col"],
        )
        return Response(MoveSerializer(move).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def scoreboard_view(request):
    queryset = (
        User.objects.annotate(
            wins=Count("games_won", distinct=True),
            draws=Count(
                "games_as_x",
                filter=Q(games_as_x__status=Status.DRAW.value),
                distinct=True,
            )
            + Count(
                "games_as_o",
                filter=Q(games_as_o__status=Status.DRAW.value),
                distinct=True,
            ),
            losses=Count(
                "games_as_x",
                filter=Q(games_as_x__status=Status.O_WON.value),
                distinct=True,
            )
            + Count(
                "games_as_o",
                filter=Q(games_as_o__status=Status.X_WON.value),
                distinct=True,
            ),
            games_played=Count("games_as_x", distinct=True) + Count("games_as_o", distinct=True),
        )
        .filter(games_played__gt=0)
        .order_by("-wins", "username")
    )

    payload = []
    for user in queryset:
        payload.append(
            {
                "username": user.username,
                "wins": user.wins,
                "losses": user.losses,
                "draws": user.draws,
                "games_played": user.games_played,
            }
        )

    return Response(ScoreboardEntrySerializer(payload, many=True).data)
