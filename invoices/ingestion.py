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
                error_msg = "Duplicate entry?"

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
        This will calculate the totals in a raw SQL query.
        It is probably easier to read that converting it to Django's ORM using F expressions,
        and should be faster than processing in python.
        Though it will have the disadvantage that it will be harder to add sorting, pagination and filter
        to it afterwards.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    currency,
                    revenue_source, 
                    customer, 
                    payment_duration,
                    daily_fee_percent,
                    EXTRACT(MONTH FROM date) || ' - ' || EXTRACT(YEAR FROM date) AS month, 
                    SUM(value) as value_total, 
                    SUM(value * haircut_percent * 0.01) as haircut_total,
                    SUM(value - (value * haircut_percent * 0.01))  as advance_total, 
                    (
                    SUM((value - (value * haircut_percent * 0.01)))
                     * daily_fee_percent * 0.01 * payment_duration)  AS expected_fee_total
                FROM invoices_invoice inv
                GROUP BY customer, 
                         revenue_source, 
                         EXTRACT(YEAR FROM date), 
                         EXTRACT(MONTH FROM date),
                         currency,
                         haircut_percent,
                         daily_fee_percent,
                         payment_duration  
                ORDER BY customer, 
                         revenue_source, 
                         EXTRACT(YEAR FROM date) DESC, 
                         EXTRACT(MONTH FROM date) DESC
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


# query for SQLite, but I am using postgres now
"""
        SELECT 
            currency,
            revenue_source, 
            customer, 
            strftime('%m', date) || ' - ' || strftime('%Y', date) AS month, 
            SUM(value) as value_total, 
            SUM(value * haircut_percent * 0.01) as haircut_total,
            SUM(value - (value * haircut_percent * 0.01))  as advance_total, 
            SUM((value - (value * haircut_percent * 0.01))) * daily_fee_percent * 0.01 * payment_duration 
                AS expected_fee_total
        FROM invoices_invoice inv
        GROUP BY customer, 
                 revenue_source, 
                 strftime('%Y', date), 
                 strftime('%m', date) 

        ORDER BY customer, 
                 revenue_source, 
                 strftime('%Y', date) DESC, 
                 strftime('%m', date) DESC
"""
