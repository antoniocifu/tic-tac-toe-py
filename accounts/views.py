"""User registration endpoint.

Login is delegated to DRF's built-in ``obtain_auth_token`` view, which
takes ``username`` + ``password`` and returns a token.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from games.serializers import RegisterSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        body = RegisterSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        username = body.validated_data["username"]
        password = body.validated_data["password"]

        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "username already taken"},
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"username": user.username, "token": token.key},
            status=status.HTTP_201_CREATED,
        )
