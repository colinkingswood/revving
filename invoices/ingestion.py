import csv
from django.core.files.base import File
from django.db import transaction
from django.db import IntegrityError
from django.db import connection

from invoices.models import Invoice


class IngestionEngine:

    def parse_csv(self, csv_file: File):

        errors = {}
        success = 0
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)

        for i, row in enumerate(reader):
            # skip the first header row
            if i == 0:
                continue
            try:
                # using get or create will not be a problem if lines are a duplicate, but will throw an error
                # but will if there are other differences, based on teh invoice being unique
                with transaction.atomic():
                    kwargs = {
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
                    invoice = Invoice.objects.create(**kwargs)
                    success += 1
            except IntegrityError as e:
                error_msg = str(e)+ ". Duplicate entry?"

                if not error_msg in errors:
                    errors[error_msg] = []
                errors[error_msg].append(i+1)

            except Exception as e:
                if not str(e) in errors:
                    errors[str(e)] = []
                errors[str(e)].append(i+1)

        return {"success_count": success, "errors": errors}


    def totals_raw_sql(self):
        """
        This will calculate teh totals in a raw SQL query.
        It is probably easier to read that converting it to Django's ORM using F expressions,
        Though it will have the disadvantage that it will be harder to add sorting to it afterwards
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    currency,
                    revenue_source, 
                    customer, 
                    strftime('%Y', date) AS year,  
                    strftime('%m', date) AS month, 
                    SUM(value * haircut_percent * 0.01) as haircut_total,
                    SUM(value - (value * haircut_percent * 0.01))  as advance_total, 
                    SUM((value - (value * haircut_percent * 0.01))) * daily_fee_percent * 0.01 * payment_duration 
                        AS expected_fee_total
                FROM invoices_invoice inv
                GROUP BY customer, 
                         revenue_source, 
                         strftime('%Y', date), 
                         strftime('%m', date) 
                         
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