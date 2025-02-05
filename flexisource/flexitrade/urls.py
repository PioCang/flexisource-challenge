from django.urls import path

from .views.auth import UserLoginView, UserLogoutView, UserRegistrationView
from .views.trade import PlaceSingleTradeView

urlpatterns = [
    path("auth/signup/", UserRegistrationView.as_view(), name="signup"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/logout/", UserLogoutView.as_view(), name="logout"),
    # path("portfolio/", LoadUserPortfolioView.as_view(), name="portfolio"),
    # path("bulk_trade/", PlaceBulkTrade.as_view(), name="bulk_trade"),
    path("trade/", PlaceSingleTradeView.as_view(), name="single_trade"),
]
