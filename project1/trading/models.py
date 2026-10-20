from unicodedata import name

from django.db import models



# each class represents a table in the database
# run 'python manage.py makemigrations' and 'python manage.py migrate' to apply changes to the database
class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    sector = models.CharField(max_length= 100, blank=True)
    market_cap = models.BigIntegerField(null=True, blank= True) # allows you(admin) to submit blank values in those forms
    is_active =  models.BooleanField(default=True) # makes it automatically active
    created_at = models.DateTimeField(auto_now_add=True) # Time and date automatically added
    updated_at = models.DateTimeField(auto_now=True) # Time and date automatically updated whenever the object is saved


class PriceData(models.Model):
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="price_data"
    )
    date = models.DateField(db_index=True) # adds an index to the date field for faster queries
    open_price = models.DecimalField(max_digits=12, decimal_places=4)
    high = models.DecimalField(max_digits=12, decimal_places=4)
    low = models.DecimalField(max_digits=12, decimal_places=4)
    close = models.DecimalField(max_digits=12, decimal_places=4)
    volume = models.BigIntegerField()
    adjusted_close = models.DecimalField(
        max_digits=12, decimal_places=4
        )


class MomentumScore(models.Model):
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="momentum_scores"
    )
    calculation_date = models.DateField(db_index=True)
    momentum_score = models.DecimalField(max_digits=10, decimal_places=6)
    rank = models.IntegerField(null=True, blank=True)
    quintile = models.IntegerField(null=True, blank=True)
    is_top_quintile = models.BooleanField(default=False)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class TradingSignal(models.Model):
    SIGNAL_TYPES = [
        ("BUY", "buy"),
        ("SELL", "sell"),
        ("HOLD", "hold")
    ]

    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="trading_signals"
    )
    signal_date = models.DateField(db_index=True)
    signal_type = models.CharField(max_length=4, choices=SIGNAL_TYPES) # any row written in the database has to be buy, sell or hold
    momentum_score = models.ForeignKey(
        MomentumScore, on_delete=models.CASCADE, null=True
    )
    target_quantity = models.IntegerField(null=True, blank=True)
    target_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    reason = models.TextField(blank=True)
    is_executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: # add metafields to database fields in Django
        db_table = "trading_signals"
        ordering = ["-signal_date", "-created_at"]
        indexes = [
            models.Index(fields=["signal_date", "signal_type"]),
            models.Index(fields=["is_executed"]),
        ]


class RebalanceEvent(models.Model):
    date = models.DateField(db_index=True)
    total_stocks_analysed = models.IntegerField()
    buy_signals_generated = models.IntegerField()
    sell_signals_generated = models.IntegerField()
    total_portfolio_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    execution_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "pending"),
            ("COMPLETED", "completed"),
            ("FAILED", "failed")
        ],
        default="PENDING"
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

