"""Class for validating trades"""
from collections import defaultdict

from django.db.models import Model

from .enums import TradeActionChoices
from .queries import calculate_owned_shares


class TradeValidator:
    def __init__(self, user, params):
        self.owner: Model = user
        self.symbol: str = params.get("symbol") or ""
        self.quantity: int = params.get("quantity") or 0
        self.action: str = params.get("action") or ""

        self.errors = defaultdict(list)

    @property
    def error_dict(self):
        """Return all listed errors"""
        return self.errors

    def cleaned_params(self):
        """Return the parameters cleaned"""
        return {
            "owner": self.owner,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "action": self.action,
        }

    def validate_raw_inputs(self):
        """Validate inputs based on given values alone"""

        self.validate_symbol()
        self.validate_quantity()
        self.validate_action()

    def is_valid(self) -> dict:
        """Determine the validity of the trade itself

        No validations are done against BUY orders because a design decision
        was made that a user could buy out of thin air, with an unlimited purse
        """
        self.validate_raw_inputs()
        if self.errors:
            # We want to know immediately if the raw inputs are bad
            return False

        if self.action == TradeActionChoices.SELL:
            self.validate_sell_order()
            if self.errors:
                return False

        return True

    def validate_symbol(self) -> None:
        """Validate the raw value of symbol"""
        key = "symbol"

        if not self.symbol:
            msg = "no symbol provided"
            self.errors[key].append(msg)

        self.symbol = self.symbol.strip()
        if len(self.symbol) > 5:
            msg = "symbol should be max 5 characters"
            self.errors[key].append(msg)

    def validate_quantity(self) -> None:
        """Validate the raw value of quantity"""
        key = "quantity"

        try:
            self.quantity = int(self.quantity)
        except (TypeError, ValueError):
            msg = "quantity must be a number"
            self.errors[key].append(msg)
            return

        if self.quantity < 1:
            msg = "quantity must be minimum 1 share"
            self.errors[key].append(msg)

    def validate_action(self) -> None:
        """Validate the raw value of action"""
        key = "action"

        self.action = self.action.strip()
        if not self.action or self.action not in ["buy", "sell"]:
            msg = "action should be only one of ['buy', 'sell']"
            self.errors[key].append(msg)

        if len(self.action) > 1:
            self.action = self.action[:1]

    def validate_sell_order(self):
        """Verify a sell order is valid with respect to shares owned by user"""
        owned_shares = calculate_owned_shares(self.owner, self.symbol)
        if self.quantity > owned_shares:
            msg = (
                f"Trying to sell {self.quantity} shares of {self.symbol}, "
                f"but user only owns {owned_shares} shares"
            )
            self.errors["sell"].append(msg)
