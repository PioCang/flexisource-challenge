"""The models used by the Flexitrade app.
As echoed in the README file, these premises are esoteric only.

1. Users have unlimited purchasing power.
2. Stocks have an unlimited number for shares for trading.
3. The value of the stocks remain constant.
4. A user can unilaterally buy or sell a stock anytime i.e., no counterparty.
5. Fractional shares cannot be bought or sold.
6. The market is always open for trading.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from flexitrade.enums import TradeActionChoices


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating `created` and
    `modified` fields.
    """

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta info"""

        abstract = True


class Stock(TimeStampedModel):
    """The model that represents a Stock.

    Will use the auto-incremented Django-provided `id` as the primary key
    instead of manually defining it, so there's a backup surrogate key if need
    be. The ticker symbol is limited to 5 characters, as in the Nasdaq.
    """

    ticker_symbol = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=256)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        default=Decimal(0.0),
    )

    def __str__(self):
        return str(self.ticker_symbol)


class Trade(TimeStampedModel):
    """The model that represents a trade by a User on a given Stock.

    This should answer the question: Who did what to which stock, in what
    quantity, and when?
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="trades",
        on_delete=models.PROTECT,
    )
    stock = models.ForeignKey(
        Stock, related_name="traded_in", on_delete=models.PROTECT
    )
    action = models.CharField(
        max_length=1,
        choices=TradeActionChoices,
        default=TradeActionChoices.BUY,
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], default=1
    )
