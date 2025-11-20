from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate

import logging

logger = logging.getLogger("api")


class LoginAPIView(APIView):

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            # Validate missing fields explicitly
            if not username or not password:
                return Response(
                    {"error": "Username and password are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(f"Solicitud login: {username}")

            user = authenticate(username=username, password=password)

            if user is None:
                logger.warning(f"Intento de login fallido para usuario: {username}")
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            token, created = Token.objects.get_or_create(user=user)

            logger.info(f"Login exitoso para usuario: {username}")

            return Response({"token": token.key}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error en LoginAPIView: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"Solicitud de logout para usuario: {request.user.username}")

            # Algunas veces el usuario puede no tener token (caso poco común)
            if hasattr(request.user, "auth_token"):
                request.user.auth_token.delete()

            logger.info(f"Logout exitoso para usuario: {request.user.username}")

            return Response(
                {"message": "Successfully logged out."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(
                f"Error durante logout para usuario {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
