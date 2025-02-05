from django.urls import path

from .views.auth import UserLoginView, UserLogoutView, UserRegistrationView

urlpatterns = [
    path("auth/signup/", UserRegistrationView.as_view(), name="signup"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/logout/", UserLogoutView.as_view(), name="logout"),
]
