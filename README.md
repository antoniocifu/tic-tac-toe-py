# Tic-Tac-Toe Backend

A small Django + DRF backend that lets two players play Tic-Tac-Toe over a REST API or from the command line.

> Status: work in progress. This README will grow as endpoints and the CLI  are completed.

---

## Requirements

- Python **3.12**
- SQLite (bundled with Python — no external services required)

## Setup

```bash
git clone https://github.com/antoniocifu/tic-tac-toe-py
cd tic-tac-toe-py

python -m venv .venv
source .venv/bin/activate            # Linux / macOS
# .\.venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -e ".[dev]"
```

> The single source of truth for dependencies is `pyproject.toml`.
> A pinned `requirements.txt` is generated at the end of development for
> environments that prefer it.

## Running the server

```bash
python manage.py migrate
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/`. While the game
endpoints are still being built, the following are already wired up:

| Method | URL | Description |
| --- | --- | --- |
| `GET` | `/api/health/` | Liveness probe, returns `{"status": "ok"}` |
| `GET` | `/api/schema/swagger-ui/` | Swagger UI (auto-generated) |
| `POST` | `/api/auth/register/` | Create a user, returns an auth token |
| `POST` | `/api/auth/login/` | Exchange username + password for an auth token |
| `POST` | `/api/games/` | Start a game against an opponent |
| `GET` | `/api/games/` | List your games |
| `GET` | `/api/games/{id}/` | Game state and rendered board |
| `POST` | `/api/games/{id}/moves/` | Play `{"row": r, "col": c}` |
| `GET` | `/api/games/{id}/moves/` | Move log of the game |
| `GET` | `/admin/` | Django admin (requires `createsuperuser`) |

### Trying it from Swagger UI

The Swagger page at `/api/schema/swagger-ui/` lets you call every endpoint
from the browser. To use the protected ones:

1. Call `POST /api/auth/register/` with a username and password.
2. Copy the `token` from the response.
3. Click the green **Authorize** button (top right) and paste:
   `Token <your-token>` (note the `Token ` prefix and the space).
4. Now every "Try it out" call will be authenticated.

## CLI mode

Besides the REST API, the project also includes a small interactive CLI:

```bash
python manage.py play
```

You can also provide both players up front:

```bash
python manage.py play --player-x alice --player-o bob
```

Moves are entered as `row,col`, using zero-based coordinates:

```text
0,0
1,1
0,1
2,2
0,2
```

Type `q` at any time to stop the game. The current state is stored in
SQLite, so the same game data is still visible from the API and the admin.

### Playing a quick game with `curl`

```bash
# Register two players
ALICE=$(curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret123"}' | jq -r .token)

BOB=$(curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"bob","password":"secret123"}' | jq -r .token)

# Alice opens a game against Bob
GAME=$(curl -s -X POST http://localhost:8000/api/games/ \
  -H "Authorization: Token $ALICE" \
  -H 'Content-Type: application/json' \
  -d '{"opponent":"bob"}' | jq -r .id)

# Alice plays
curl -X POST http://localhost:8000/api/games/$GAME/moves/ \
  -H "Authorization: Token $ALICE" \
  -H 'Content-Type: application/json' \
  -d '{"row":0,"col":0}'

# Inspect the board (ASCII included)
curl http://localhost:8000/api/games/$GAME/ \
  -H "Authorization: Token $ALICE"
```

## Running the tests

```bash
pytest                  # full suite
pytest games/tests/     # domain only (fast, no database)
```

---

## Project layout

```
config/         Django project: split settings (base/dev/prod), urls, wsgi
games/          Game app
  domain/      Pure game logic, framework-agnostic
  models.py    Persistence (Game, Move)
accounts/       Users and authentication
manage.py
pyproject.toml
```

The split between `domain/` and `models.py` is intentional: the rules of the game are pure Python and can be tested without booting Django or  hitting the database.
