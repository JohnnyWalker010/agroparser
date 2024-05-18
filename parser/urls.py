from django.urls import path

from parser.views import home_page, CustomCreateJWTView, CustomTokenRefreshView

urlpatterns = [
    path("", home_page, name="home"),
    path("api/token/", CustomCreateJWTView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
