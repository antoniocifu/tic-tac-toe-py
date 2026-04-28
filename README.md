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

The API will be available at `http://127.0.0.1:8000/`.

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
