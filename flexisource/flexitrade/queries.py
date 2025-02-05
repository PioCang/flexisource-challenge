import re

from django.db import connection
from django.db.models import F, IntegerField, QuerySet, Sum
from django.db.models.expressions import Case, Value, When

from .enums import TradeActionChoices
from .models import Trade


@staticmethod
def calculate_owned_shares(owner, symbol):
    """Calculate the shares user owns of a stock by replaying trade history"""

    total_sum = (
        Trade.objects.filter(
            stock__ticker_symbol=symbol,
            actor=owner,
        )
        .annotate(
            effective_quantity=Case(
                When(action=TradeActionChoices.BUY, then=F("quantity")),
                When(
                    action=TradeActionChoices.SELL,
                    then=(F("quantity") * Value(-1)),
                ),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .aggregate(total_sum=Sum("effective_quantity"))["total_sum"]
    )

    return total_sum or 0


def queryset_to_sql(queryset_to_explain: QuerySet) -> str:
    """Given a QuerySet, translate to the actual SQL sent to the database."""
    # The explanation of QuerySet.query does not reveal the actual SQL sent to
    # the database after adapter-specific substitutions are made  this one does
    # https://code.djangoproject.com/ticket/17741#comment:4

    naive_sql, params = queryset_to_explain.query.sql_with_params()
    sql_to_interpolate = f"EXPLAIN {naive_sql}"
    cursor = connection.cursor()
    cursor.execute(sql_to_interpolate, params)

    translated_sql = cursor.db.ops.last_executed_query(
        cursor, naive_sql, params
    )

    translated_sql = translated_sql.replace("EXPLAIN ", "")

    joins_regex = r"(([A-Z]+\s)*JOIN)"
    translated_sql = re.sub(joins_regex, r"\n\1", translated_sql)

    keywords_just_newline = (
        "FROM",
        "WHERE",
        "ORDER",
        "GROUP",
        "HAVING",
        "WHEN",
    )
    for keyword in keywords_just_newline:
        translated_sql = translated_sql.replace(keyword, f"\n{keyword}")

    keywords_newline_indent = ("AND", "OR", "ON", "THEN")
    for keyword in keywords_newline_indent:
        translated_sql = translated_sql.replace(keyword, f"\n    {keyword}")

    translated_sql = translated_sql.replace('",', '",\n       ')

    return translated_sql + "\n"
