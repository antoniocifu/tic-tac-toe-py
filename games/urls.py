from django.urls import path
from rest_framework.routers import DefaultRouter

from games.views import GameViewSet, scoreboard_view

router = DefaultRouter()
router.register("games", GameViewSet, basename="game")

urlpatterns = [
    path("scoreboard/", scoreboard_view, name="scoreboard"),
    *router.urls,
]
