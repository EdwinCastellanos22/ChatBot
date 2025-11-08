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

            logger.info(f"Solicitud login: {username}")

            user = authenticate(username=username, password=password)

            if user is None:
                logger.warning(f"Intento de login fallido para el usuario: {username}")
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            token, created = Token.objects.get_or_create(user=user)

            logger.info(f"Login exitoso para el usuario: {username}")

            return Response({"token": token.key}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Solicitud de logout para el usuario: {request.user.username}")
        try:
            request.user.auth_token.delete()
            logger.info(f"Logout exitoso para el usuario: {request.user.username}")
            return Response(
                {"message": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(
                f"Error durante el logout para el usuario {request.user.username}: {e}"
            )
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
