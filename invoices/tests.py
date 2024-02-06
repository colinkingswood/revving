from unittest import skip

from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from invoices.ingestion import IngestionEngine
from invoices.models import Invoice
class IngestionEngineTestCase(TestCase):
    """
    These tests will test the ingestion engine  directly
    """


    test_file_path = 'test_files/example.csv'

    def test_totals(self):
        pass

    def test_ingestion_csv_parser(self):
        """
        Test the ingestion engine directly, by reading the file
        """
        ingestion = IngestionEngine()

        with open(self.test_file_path, 'rb') as file:
#            csv_file = file.read()
            results = ingestion.parse_csv(csv_file=file)
            self.assertEqual(results['success_count'], 2161)
            print(results['errors'])
            #self.assertEqual()

    def test_pasre_csv(self):
        """
        Test posting the data to the endpoint, to emulate file upload
        """
        ingestion = IngestionEngine()

        with open(self.test_file_path, 'rb') as f:
            upload_file = File(f)
            results = ingestion.parse_csv(upload_file)
            self.assertEqual(2161, Invoice.objects.all().count())

            print(results)
            print(results['errors'])


class UploadTestCase(TestCase):
    """
    This class will test the endpoints by emulating the form upload
    from a webpage
    """

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

    def test_upload_without_csv(self):
        """
        test that we get a 400 error code when the csv file isn't supplied
        """
        url = reverse('upload_view')

        response = self.client.post(url,
                                    {},
                                    format='multipart')

        # Check that the response is 400
        self.assertEqual(response.status_code, 400)
