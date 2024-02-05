import csv
from django.core.files.uploadedfile import UploadedFile

from django.db import IntegrityError
from django.db import connection

from invoices.models import Invoice


class IngestionEngine:

    def parse_csv(self, csv_file: UploadedFile):

        errors = []
        warnings = []
        success = 0
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)

        for i, row in enumerate(reader):
            print(i, row)
            if i == 0:
                continue
            try:
                # using get or create will not be a problem if lines are a duplicate, but will throw an error
                # but will if there are other differences, based on teh invoice being unique
                #with transaction.atomic():
                kwargs= {
                    "date": row[0],
                    "invoice_number": row[1],
                    "value": row[2],
                    "haircut_percent": row[3],
                    "daily_fee_percent": row[4],
                    "currency": row[5].strip(),
                    "revenue_source": row[6].strip(),
                    "customer": row[7].strip(),
                    "payment_duration": row[8],
                    }
                #if not Invoice.objects.filter(**kwargs).exists():
                invoice = Invoice.objects.create(**kwargs)
                success += 1
            except IntegrityError as e:
                warnings.append(f"Integrity error at line {i + 1}, is the line a duplicate entry?: {str(e)}")

            except Exception as e:
                if i == 0:
                    warnings.append(f"Couldn't parse line first line, assuming it is a header")
                else:
                    errors.append(f"error importing line { i + 1 }: {str(e)}")

        return {"warnings": warnings, "success_count": success, "errors": errors}


    def totals_raw_sql(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    currency,
                    revenue_source, 
                    customer, 
                    SUM(value * haircut_percent * 0.01) as haircut_total,
                    SUM(value - (value * haircut_percent * 0.01))  as advance_total, 
                    SUM((value - (value * haircut_percent * 0.01))) * daily_fee_percent * 0.01  as expected_fee_total
                FROM invoices_invoice inv
                GROUP BY customer, revenue_source
            """)
            result_dict = self.dictfetchall(cursor)
        return result_dict

    def dictfetchall(self, cursor):
        """
        Return all rows from a cursor as a dict.
        Assume the column names are unique.
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # except Exception as e:
    #     form.add_error(None, f"Error parsing csv file on line {i}: {str(e)}\n{row}")
    #     return self.form_invalid(form=form)






    # def __init__(self):
    #     self.invoices = []

    # def add_invoice(self, invoice_data):
    #     # This method will add invoice data to the engine
    #     # For simplicity, this assumes invoice_data is a dictionary matching the Invoice model fields
    #     self.invoices.append(invoice_data)
    #
    # def calculate_totals(self):
    #     # Calculates totals for each revenue source
    #     totals = {}
    #     for invoice in self.invoices:
    #         revenue_source = invoice['revenue_source']
    #         if revenue_source not in totals:
    #             totals[revenue_source] = {'value': 0, 'advance': 0, 'expected_fee': 0}
    #         totals[revenue_source]['value'] += invoice['value']
    #         totals[revenue_source]['advance'] += invoice['advance']
    #         totals[revenue_source]['expected_fee'] += invoice['expected_fee']
    #     return totals


# invoice = Invoice.objects.create(
#     date=row[0],
#     invoice_number=row[1],
#     value=row[2],
#     haircut_percent=row[3],
#     daily_fee_percent=row[4],
#     currency=row[5].strip(),
#     revenue_source=row[6].strip(),
#     customer=row[7].strip(),
#     payment_duration=row[8],
#     )