
from celery import shared_task
from invoices.ingestion import IngestionEngine

@shared_task
def test_task():
    print("Celery task!")


