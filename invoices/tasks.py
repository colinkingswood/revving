
import os
from celery import shared_task
from invoices.ingestion import IngestionEngine
from django.core.files.base import File


@shared_task
def test_task(file_name):
    # todo, add the ingestion task here if I get time.
    print(f"Celery task! {file_name}")

    file_size = os.path.getsize(file_name)

    print(f"The size of '{file_name}' is {file_size} bytes.")

    with open(file_name, "rb") as file:
        csv_file = File(file)

        ingestion = IngestionEngine()
        results = ingestion.parse_csv(csv_file=csv_file)
        print(results)

