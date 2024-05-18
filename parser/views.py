from subprocess import Popen, PIPE

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from parser.models import JWToken
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm


@login_required
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


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"User {username} created!")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "registration/registration.html", {"form": form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "registration/user_profile.html", {"user": user})


@login_required
def accounts_page(request):
    users = User.objects.all()
    return render(request, "registration/accounts.html", {"users": users})


scraper_process = None


def start_scraper(request):
    global scraper_process
    if scraper_process is None or scraper_process.poll() is not None:
        scraper_process = Popen(["python", "main.py"], stdout=PIPE, stderr=PIPE)
        return JsonResponse({"message": "Scraper started."})
    else:
        return JsonResponse({"message": "Scraper is already running."})


def stop_scraper(request):
    global scraper_process
    if scraper_process is not None and scraper_process.poll() is None:
        scraper_process.terminate()
        scraper_process = None
        return HttpResponse("Scraper stopped.")
    else:
        return HttpResponse("No running scraper to stop.")
