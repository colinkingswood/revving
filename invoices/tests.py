from decimal import Decimal
from unittest import skip
import csv
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
        filename = 'totals_test.csv'

        # Data to write
        rows = [
                ["date","invoice number","value","haircut percent","Daily fee percent","currency","Revenue source","customer","Expected payment duration"],

                ["2023-09-18","7090","200.00","10","0.125","USD","SourceA","Customer1","65"],
                ["2023-09-28","3140","200.00","10","0.125","USD","SourceA","Customer1","65"],

                ["2023-05-15","3613","100.00","10","0.125","USD","SourceB","Customer1","65"],

                ["2023-05-01","6840","100.00","10","0.7","USD","SourceC","Customer2","60"],
                ["2023-05-01", "6841", "100.00", "10", "0.7", "USD", "SourceC", "Customer2", "60"],
                ["2023-05-01", "6841", "100.00", "10", "0.7", "USD", "SourceC", "Customer2", "60"],
                ["2023-05-01", "6841", "100.00", "10", "0.7", "USD", "SourceC", "Customer2", "60"]
               ]

        # Open the file and write the test data to it
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        with open(filename, 'rb') as file:
            ingestion = IngestionEngine()
            results = ingestion.parse_csv(file)
            self.assertEqual(results.get("success_count"), 5)
            errors = results.get('errors')
            self.assertListEqual(errors.get("Duplicate entry?"),[7, 8] )

            totals = ingestion.totals_raw_sql()
            print(totals)
            # we should have 2 lines with customer1
            line_1 = totals[0]  # Customer1, SourceA, 09-2023
            line_2 = totals[1]  # Customer1, SourceB, 05-2023
            line_3 = totals[2]  # Customer2, SourceC, 05-2023

            # line 1, Customer1 SourceA, 9 / 2023
            self.assertEqual(line_1['customer'], "Customer1")
            self.assertEqual(line_1['month'], "9 - 2023")
            self.assertEqual(line_1['revenue_source'], "SourceA")
            # values_l_1 = 200 + 200 = 400
            self.assertEqual(line_1['value_total'], 400)
            # haircut = 10, haircut total = 400 * 10 * 0.01 = 40
            self.assertEqual(line_1['haircut_total'], 40)
            # advance total = 400 - 40 = 360
            self.assertEqual(line_1['advance_total'], 360)
            # advance total * daily_fee percent * 0.01 * payment_duration
            # expected fee total = 360 * 0.125  * 0.01 * 65 = 29.25
            self.assertEqual(line_1['expected_fee_total'], Decimal(29.25))


            # line 1, Customer1 SourceB, 5 / 2023
            self.assertEqual(line_2['customer'], "Customer1")
            self.assertEqual(line_2['month'], "5 - 2023")
            self.assertEqual(line_2['revenue_source'], "SourceB")
            # ["2023-05-15", "3613", "100.00", "10", "0.125", "USD", "SourceB", "Customer1", "65"],
            # advance total = 100 * 10 * 0.01 = 10
            self.assertEqual(line_2['haircut_total'], 10)
            # advance_total = 100 - 10 = 90
            self.assertEqual(line_2['advance_total'], 90)
            # expected fee =  90 * 0.125 * 0.01 *65
            self.assertEqual(line_2['expected_fee_total'], Decimal("7.3125"))


            # line 1, Customer2 SourceC, 5 / 2023
            # ["2023-05-01", "6840", "100.00", "10", "0.7", "USD", "SourceC", "Customer2", "60"],
            # ["2023-05-01", "6841", "100.00", "10", "0.7", "USD", "SourceC", "Customer2", "60"],
            self.assertEqual(line_3['customer'], "Customer2")
            self.assertEqual(line_3['month'], "5 - 2023")
            self.assertEqual(line_3['revenue_source'], "SourceC")

            # values_l_1 = 100 + 100 = 200
            self.assertEqual(line_3['value_total'], 200)
            # haircut = 10, haircut total = 200 * 10 * 0.01 = 20
            self.assertEqual(line_3['haircut_total'], 20)
            # advance total = 200 - 20 = 180
            self.assertEqual(line_3['advance_total'], 180)
            # advance total * daily_fee percent * 0.01 * payment_duration
            # expected fee total = 180 * 0.7  * 0.01 * 60 = 75.6
            self.assertEqual(line_3['expected_fee_total'], Decimal("75.6")) # Decimal string as float messes up the comparison


    def test_ingestion_csv_parser(self):
        """
        Test the ingestion engine directly, by reading the file and sending it directly to ingestion engine
        """
        ingestion = IngestionEngine()

        with open(self.test_file_path, 'rb') as file:
            results = ingestion.parse_csv(csv_file=file)
            self.assertEqual(results['success_count'], 2161)

            duplicate_entries = results.get('errors', {}).get("Duplicate entry?", [])
            num_duplicates = len(duplicate_entries)
            self.assertEqual(num_duplicates, 1180)

    def test_parse_csv(self):
        """
        Test posting the data to the endpoint, to emulate file upload from a web browser
        """
        ingestion = IngestionEngine()

        with open(self.test_file_path, 'rb') as f:
            upload_file = File(f)
            results = ingestion.parse_csv(upload_file)
            self.assertEqual(2161, Invoice.objects.all().count())

            print(results)
            print(results['errors'])
            duplicate_entries = results.get('errors', {}).get("Duplicate entry?", [])
            num_duplicates = len(duplicate_entries)
            self.assertEqual(num_duplicates, 1180)


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
