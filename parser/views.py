from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from parser.models import JWToken


def home_page(request):
    context = {
        "title": "Agroparser",
        "content": "Home page",
    }

    return render(request, "home.html", context)


class CustomCreateJWTView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data["username"])
            token = response.data["access"]
            JWToken.objects.create(user=user, token=token)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            refresh_token = request.data.get("refresh")
            try:
                refresh_token_obj = RefreshToken(refresh_token)
                user_id = refresh_token_obj["user_id"]
                user = User.objects.get(id=user_id)
                token = response.data["access"]
                JWToken.objects.create(user=user, token=token)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response
