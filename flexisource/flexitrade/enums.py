"""Enums for Choices used in the app"""

from django.db import models


class TradeActionChoices(models.TextChoices):
    """Allowed actions for Trades"""

    BUY = ("b", "User buys.")
    SELL = ("s", "User sells.")
