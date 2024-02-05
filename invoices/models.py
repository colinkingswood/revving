from django.db import models

# example line from csv
# 2023-03-27	3531	519.5	10	0.125	USD	Happy Playcrows	RunUp INC	65

# Create your models here.
class Invoice(models.Model):
    date = models.DateField()
    invoice_number = models.IntegerField()
    value = models.DecimalField(max_digits=16, decimal_places=8)
    haircut_percent = models.DecimalField(max_digits=6, decimal_places=3)
    daily_fee_percent = models.DecimalField(max_digits=8, decimal_places=4)
    currency = models.CharField(max_length=4)
    revenue_source = models.CharField(max_length=100)
    customer = models.CharField(max_length=100)
    payment_duration = models.PositiveSmallIntegerField(verbose_name="expected payment duration")

    def __str__(self):
        return str(self.invoice_number)

    class Meta:
        unique_together = ('invoice_number', "customer")













