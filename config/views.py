"""Project-wide views (infrastructure, not tied to any app)."""

from django.http import JsonResponse


def healthcheck(_request):
    """Lightweight liveness probe used by orchestration and smoke tests."""
    return JsonResponse({"status": "ok"})
