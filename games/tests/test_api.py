import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from games.models import Game

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def alice(db):
    return User.objects.create_user(username="alice", password="secret123")


@pytest.fixture
def bob(db):
    return User.objects.create_user(username="bob", password="secret123")


@pytest.fixture
def alice_client(api_client, alice):
    token, _ = Token.objects.get_or_create(user=alice)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def bob_client(bob):
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=bob)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


def test_register_returns_token(api_client, db):
    response = api_client.post(
        "/api/auth/register/",
        {"username": "charlie", "password": "secret123"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["username"] == "charlie"
    assert response.data["token"]


def test_create_game(alice_client, bob):
    response = alice_client.post("/api/games/", {"opponent": bob.username}, format="json")

    assert response.status_code == 201
    assert response.data["player_x"] == "alice"
    assert response.data["player_o"] == "bob"
    assert response.data["status"] == "in_progress"


@pytest.mark.django_db
def test_play_full_game_and_detect_winner(alice_client, bob_client, alice, bob):
    game = Game.objects.create(player_x=alice, player_o=bob)

    assert (
        alice_client.post(
            f"/api/games/{game.id}/moves/", {"row": 0, "col": 0}, format="json"
        ).status_code
        == 201
    )
    assert (
        bob_client.post(
            f"/api/games/{game.id}/moves/", {"row": 1, "col": 0}, format="json"
        ).status_code
        == 201
    )
    assert (
        alice_client.post(
            f"/api/games/{game.id}/moves/", {"row": 0, "col": 1}, format="json"
        ).status_code
        == 201
    )
    assert (
        bob_client.post(
            f"/api/games/{game.id}/moves/", {"row": 1, "col": 1}, format="json"
        ).status_code
        == 201
    )
    assert (
        alice_client.post(
            f"/api/games/{game.id}/moves/", {"row": 0, "col": 2}, format="json"
        ).status_code
        == 201
    )

    detail = alice_client.get(f"/api/games/{game.id}/")
    assert detail.status_code == 200
    assert detail.data["status"] == "x_won"
    assert detail.data["winner"] == "alice"
    assert detail.data["next_player"] is None
    assert detail.data["board"][0] == ["X", "X", "X"]


@pytest.mark.django_db
def test_cannot_play_out_of_turn(alice_client, bob_client, alice, bob):
    game = Game.objects.create(player_x=alice, player_o=bob)

    response = bob_client.post(f"/api/games/{game.id}/moves/", {"row": 0, "col": 0}, format="json")

    assert response.status_code == 403
    assert "turn" in response.data["detail"].lower()


@pytest.mark.django_db
def test_non_player_cannot_access_foreign_game(api_client, alice, bob):
    outsider = User.objects.create_user(username="mallory", password="secret123")
    token, _ = Token.objects.get_or_create(user=outsider)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    game = Game.objects.create(player_x=alice, player_o=bob)

    response = api_client.get(f"/api/games/{game.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_move_log_endpoint(alice_client, bob_client, alice, bob):
    game = Game.objects.create(player_x=alice, player_o=bob)
    alice_client.post(f"/api/games/{game.id}/moves/", {"row": 2, "col": 2}, format="json")
    bob_client.post(f"/api/games/{game.id}/moves/", {"row": 1, "col": 1}, format="json")

    response = alice_client.get(f"/api/games/{game.id}/moves/")

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["mark"] == "X"
    assert response.data[1]["mark"] == "O"
