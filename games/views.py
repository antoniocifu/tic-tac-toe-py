"""HTTP views for the games API."""

from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from games import services
from games.models import Game
from games.serializers import (
    GameCreateSerializer,
    GameDetailSerializer,
    GameListSerializer,
    MoveInputSerializer,
    MoveSerializer,
)


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
