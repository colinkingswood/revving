from django.db import models

#2023-03-27	3531	519.5	10	0.125	USD	Happy Playcrows	RunUp INC	65

# Create your models here.
class Invoice(models.Model):
    date = models.DateField()
    invoice_number = models.IntegerField()
    # value = models.DecimalField(max_length=, decimal_places=)
    # haircut_percent = models.DecimalField()
    # daily_fee_percent = models.DecimalField(decimal_places=)
    # currency = models.CharField(max_length=4)
    # revenue_source = models.CharField(max_length=100)
    # customer = models.CharField(max_length=100)
    # payment_duration = models.PositiveSmallIntegerField(verbose_name="expected payment duration")

    def __str__(self):
        return self.invoice_number















