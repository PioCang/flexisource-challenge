"""Trading-related Views"""

import random

from flexitrade.enums import TradeActionChoices
from flexitrade.models import Stock, Trade
from flexitrade.queries import load_portfolio
from flexitrade.validators import TradeValidator
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class PortfolioView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get the whole porfolio of the user"""
        portfolio_data = load_portfolio(request.user)
        return Response(portfolio_data, status=status.HTTP_200_OK)


class PlaceSingleTradeView(APIView):
    """Place a trade as a User"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """The view that places a trade on behalf of a user"""

        trade_validator = TradeValidator(request.user, request.data)

        if not trade_validator.is_valid():
            return Response(
                trade_validator.error_dict, status=status.HTTP_400_BAD_REQUEST
            )

        msg = self.execute_trade(trade_validator.cleaned_params())
        return Response({"message": msg}, status=status.HTTP_201_CREATED)

    def execute_trade(self, params):
        """Create a Trade objects after validating that it can execute

        If the stock doesn't yet exist, create it
        """
        random_price = random.uniform(1, 1000)
        stock_obj, _ = Stock.objects.get_or_create(
            ticker_symbol=params["symbol"],
            defaults={"price": random_price},
        )

        Trade.objects.create(
            actor=params["owner"],
            stock=stock_obj,
            action=params["action"],
            quantity=params["quantity"],
        )

        verb = (
            "bought" if params["action"] == TradeActionChoices.BUY else "sold"
        )
        msg = f"{params['quantity']} shares of {params['symbol']} {verb}"
        return msg
