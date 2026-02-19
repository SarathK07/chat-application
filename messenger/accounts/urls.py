from django.urls import path
from .views import LoginRegisterView, VerifyOTPView, UserListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginRegisterView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("users/", UserListView.as_view()),

]
