from django.urls import path

from parser.views import (
    home_page,
    CustomCreateJWTView,
    CustomTokenRefreshView,
    accounts_page,
    profile,
    run_scraper,
    stop_scraper,
)

urlpatterns = [
    path("", home_page, name="home"),
    path("api/token/", CustomCreateJWTView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("accounts/", accounts_page, name="accounts"),
    path("accounts/profile/<str:username>/", profile, name="profile"),
    path("start-scraper/", run_scraper, name="start_scraper"),
    path("stop-scraper/", stop_scraper, name="stop_scraper"),
]
