"""Map domain errors to clean HTTP responses.

Wired in DRF settings via ``EXCEPTION_HANDLER``.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

from games.domain.exceptions import (
    CellAlreadyTakenError,
    GameAlreadyFinishedError,
    InvalidMoveError,
    NotAPlayerError,
    NotYourTurnError,
    OutOfBoundsError,
)

_ERROR_MAP = {
    OutOfBoundsError: status.HTTP_400_BAD_REQUEST,
    CellAlreadyTakenError: status.HTTP_400_BAD_REQUEST,
    GameAlreadyFinishedError: status.HTTP_409_CONFLICT,
    NotYourTurnError: status.HTTP_403_FORBIDDEN,
    NotAPlayerError: status.HTTP_403_FORBIDDEN,
    InvalidMoveError: status.HTTP_400_BAD_REQUEST,  # catch-all for new subtypes
}


def domain_aware_exception_handler(exc, context):
    for exc_type, status_code in _ERROR_MAP.items():
        if isinstance(exc, exc_type):
            return Response({"detail": str(exc) or exc.__class__.__name__}, status=status_code)
    return drf_default_handler(exc, context)
