"""Production settings.

Both SECRET_KEY and the allowed hosts are read from environment
variables; never commit them to the repository.
"""

import os

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
