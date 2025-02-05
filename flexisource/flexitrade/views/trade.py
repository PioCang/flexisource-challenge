"""Trading-related Views"""

import random
from typing import Dict, List, Tuple

import pandas as pd
from django.db import transaction
from flexitrade.enums import TradeActionChoices
from flexitrade.models import Stock, Trade
from flexitrade.queries import load_portfolio
from flexitrade.validators import TradeValidator
from rest_framework import permissions, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


class PortfolioView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get the whole porfolio of the user"""
        portfolio_data = load_portfolio(request.user)
        return Response(portfolio_data, status=status.HTTP_200_OK)


class TradeExecutionMixin:
    """Mixin that allows implementing classes to execute trades."""

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


class PlaceSingleTradeView(APIView, TradeExecutionMixin):
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


class PlaceBulkTrade(APIView, TradeExecutionMixin):
    """Place multiple trades by taking a CSV

    Since the database write will be done all at once, each line must be
    validated the trades are executed.

    Reference:
    https://dev.to/frankezenwanne/how-to-upload-a-csv-file-to-django-rest-28fo
    """

    parser_classes = [FileUploadParser]
    permission_classes = [permissions.IsAuthenticated]

    def _validate_file(self, csv_file):
        """Initial checks on a file before attempting to read it"""
        if not csv_file:
            raise ValueError("No file provided")

        if not csv_file.name.endswith(".csv"):
            raise ValueError("File is not CSV type")

    def _parse_file_for_trades(self, df, owner) -> Tuple[Dict, Dict]:
        """Parse the provided dataframe for trades and perform validation

        To speed up validation, the user's portfolio is loaded so the execution
        doesn't end up selling more shares than the user owns.
        """
        headers = ["symbol", "quantity", "action"]
        portfolio_data = load_portfolio(owner)

        valid_trades: List[Dict] = []
        errors: Dict[str, str] = {}
        for index, row_data in df.iterrows():
            params = {key: row_data[key] for key in headers}
            ticker = params["symbol"]
            if ticker in portfolio_data:
                existing_shares = int(portfolio_data[ticker]["total_quantity"])
                params["existing_shares"] = existing_shares

            trade_validator = TradeValidator(owner, params)

            if not trade_validator.is_valid():
                errors[index] = trade_validator.error_dict
            else:
                valid_trades.append(trade_validator.cleaned_params())

        return (valid_trades, errors)

    def post(self, request):
        csv_file = request.FILES.get("file")
        try:
            self._validate_file(csv_file)
        except ValueError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        df = pd.read_csv(csv_file, delimiter=",", dtype=str)
        df = df.where(pd.notnull(df), None)
        valid_trades, errors = self._parse_file_for_trades(df, request.user)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return self.bulk_execute_trades(valid_trades)

    def bulk_execute_trades(self, trades_to_execute):
        """Execute the trades in one atomic DB transaction"""
        executed_trades: Dict[str] = {}
        try:
            with transaction.atomic():
                for index, params in enumerate(trades_to_execute):
                    msg = self.execute_trade(params)
                    executed_trades[index] = msg
        except Exception as err:
            return Response(
                {"error": f"Write failure {str(err)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(executed_trades, status=status.HTTP_201_CREATED)
