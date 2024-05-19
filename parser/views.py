import csv
import os
import re
from datetime import datetime

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from tqdm import tqdm

from parser.models import JWToken
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


scraper_running = False


def run_scraper(request):
    global scraper_running

    if request.method == "POST":
        if scraper_running:
            return JsonResponse({"error": "Scraper is already running."})

        scraper_running = True

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "scraped_results")
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(script_dir, "links_to_download.xlsx")
        df = pd.read_excel(file_path)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_file_name = f"result_{timestamp}.csv"
        csv_file_path = os.path.join(output_dir, csv_file_name)

        driver = webdriver.Chrome()

        with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Title", "Price", "Availability", "Producer"])

            for index, row in tqdm(df.iterrows(), total=len(df), desc="Urls parsed", colour="green"):
                if not scraper_running:
                    break

                url = row["Links"]
                driver.get(url)

                try:
                    title = driver.find_element(
                        By.CSS_SELECTOR, "body > div.site-wrapper > h1"
                    ).text
                except NoSuchElementException:
                    title = "Not available"

                try:
                    price_raw = driver.find_element(
                        By.CSS_SELECTOR,
                        "div.product-price-group > div.price-wrapper > div > div",
                    ).text
                    price = "".join(re.findall(r"\d+", price_raw))
                except NoSuchElementException:
                    price = "Not available"

                try:
                    availability = driver.find_element(
                        By.CSS_SELECTOR,
                        "div.product-price-group > div.product-stats > ul > li.product-stock.in-stock > span",
                    ).text
                except NoSuchElementException:
                    availability = "Not available"

                try:
                    producer_element = driver.find_element(
                        By.CSS_SELECTOR,
                        "div.product-price-group > div.product-stats > div > a",
                    )
                    producer_page = producer_element.get_attribute("href")
                    driver.get(producer_page)
                    producer = driver.find_element(
                        By.CSS_SELECTOR, "body > div.site-wrapper > h1"
                    ).text
                except (NoSuchElementException, WebDriverException):
                    producer = "Not available"

                csv_writer.writerow([title, price, availability, producer])

            print("Correctly finished work")

        driver.quit()
        scraper_running = False
        return JsonResponse({"message": "Scraper finished successfully."})

    return JsonResponse({"error": "Invalid request method."})


def stop_scraper(request):
    global scraper_running
    scraper_running = False
    return JsonResponse({"message": "Scraper stopped."})
