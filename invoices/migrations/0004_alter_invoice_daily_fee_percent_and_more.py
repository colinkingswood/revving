# Generated by Django 5.0.1 on 2024-02-06 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_alter_invoice_daily_fee_percent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='daily_fee_percent',
            field=models.DecimalField(decimal_places=4, max_digits=8),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='haircut_percent',
            field=models.DecimalField(decimal_places=3, max_digits=6),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='value',
            field=models.DecimalField(decimal_places=8, max_digits=16),
        ),
    ]