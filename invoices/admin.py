from django.contrib import admin
from invoices.models import Invoice

# Register your models here.

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['date' ,
                    'invoice_number',
                    'value',
                    'haircut_percent',
                    'daily_fee_percent',
                    'currency',
                    'revenue_source',
                    'customer',
                    'payment_duration']


