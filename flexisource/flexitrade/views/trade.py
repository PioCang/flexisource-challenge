"""Trading-related Views"""

import os
import random
from copy import deepcopy
from datetime import datetime
from pprint import pprint
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
    """Veiw that loads a user's entire portofolio"""

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
        msg = (
            f"{params['quantity']} share(s) of {params['symbol']} {verb} "
            f"for {params['owner'].username}"
        )
        return msg


class PlaceSingleTradeView(APIView, TradeExecutionMixin):
    """Place a trade as a User"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """The view that places a trade on behalf of a user"""

        params = deepcopy(request.data)
        params["username"] = request.user.username
        trade_validator = TradeValidator(params)

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

    LOCAL_CSV_FILE_PATH = f"{os.getcwd()}/bulk_order_local.csv"

    parser_classes = [FileUploadParser]
    permission_classes = [permissions.IsAuthenticated]

    def _validate_file(self, csv_file):
        """Initial checks on a file before attempting to read it"""
        if not csv_file:
            raise ValueError("No file provided")

        if not csv_file.name.endswith(".csv"):
            raise ValueError("File is not CSV type")

    def _parse_file_for_trades(self, df, username) -> Tuple[Dict, Dict]:
        """Parse the provided dataframe for trades and perform validation"""

        headers = ["symbol", "quantity", "action", "username"]
        valid_trades: List[Dict] = []
        errors: Dict[str, str] = {}

        for index, row_data in df.iterrows():
            params = {key: row_data.get(key) for key in headers}
            if username is not None:
                params["username"] = username
            trade_validator = TradeValidator(params)

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
        valid_trades, errors = self._parse_file_for_trades(
            df, request.user.username
        )

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        is_ok, payload = self.bulk_execute_trades(valid_trades)
        if not is_ok:
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        return Response(payload, status=status.HTTP_201_CREATED)

    def bulk_execute_trades(self, trades_to_execute) -> Tuple[bool, Dict]:
        """Execute the trades in one atomic DB transaction"""
        executed_trades: Dict[str] = {}
        try:
            with transaction.atomic():
                for index, params in enumerate(trades_to_execute):
                    msg = self.execute_trade(params)
                    executed_trades[index] = msg
        except Exception as err:
            return (False, {"error": f"Write failure {str(err)}"})

        return (True, executed_trades)

    def process_from_local_file(self):
        """Process a csv file locally"""
        with open(self.LOCAL_CSV_FILE_PATH) as csv_file:
            self._validate_file(csv_file)
            df = pd.read_csv(csv_file, delimiter=",", dtype=str)
            df = df.where(pd.notnull(df), None)
            valid_trades, errors = self._parse_file_for_trades(
                df, username=None
            )

        if errors:
            print(f"\n\n[{datetime.now().isoformat()}] ", end="")
            print("Bulk parse from local file failed")
            pprint(errors)
            return

        is_ok, payload = self.bulk_execute_trades(valid_trades)
        if not is_ok:
            print(f"\n\n[{datetime.now().isoformat()}] ", end="")
            print("Bulk trade from local file failed")
            pprint(payload)

        else:
            print(f"\n\n[{datetime.now().isoformat()}] ", end="")
            print("Bulk trade successful")
            pprint(payload)
