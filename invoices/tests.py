from unittest import skip

from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from invoices.ingestion import IngestionEngine
from invoices.models import Invoice
class IngestionEngineTestCase(TestCase):
    def test_pasre_csv(self):
        with open('test_files/example.csv', 'rb') as f:
            upload_file = File(f)
            ingestion = IngestionEngine()
            results = ingestion.parse_csv(upload_file)
            self.assertEqual(2161, Invoice.objects.all().count())
            print(len(results['warnings']))


    # def test_parse_json(self):
    #     with open('test_files/example.csv', 'rb') as f:


class UploadTestCase(TestCase):

    @skip
    def test_upload_csv_file(self):
        """
        Test that the example file is uploaded and returns a 302 redirect
        """
        url = reverse('upload_view')

        # Create a simple CSV file in memory
        with open('test_files/example.csv', 'rb') as f:
            upload_file = File(f)

            # Simulate a POST request to the 'uploads/' endpoint with the file
            response = self.client.post(url,
                                       {'csv_file': upload_file},
                                       format='multipart')

            # Check that the response is 200 OK
            self.assertEqual(response.status_code, 302)


    @skip
    def test_upload_without_csv(self):
        """
        test that we get a 400 error code when the csv file isn't supplied
        """
        url = reverse('upload_view')

        response = self.client.post(url,
                                    {},
                                    format='multipart')


        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 400)
