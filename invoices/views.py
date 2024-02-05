from django.shortcuts import render
import csv
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from invoices.forms import CsvUploadForm
from invoices.ingestion import IngestionEngine
from invoices.models import Invoice


class CvsUploadView(FormView):
    template_name = "upload.html"
    form_class = CsvUploadForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        # Process the CSV file
        ingestion = IngestionEngine()
        results = ingestion.parse_csv(csv_file=csv_file)
        return super().form_valid(form)


    def get_success_url(self):
        return reverse("totals_view")

    def form_invalid(self, form):
        # update the status code to indicate an error
        resp = self.render_to_response(self.get_context_data(form=form), status=400)
        return resp

class TotalsView(TemplateView):
    template_name = "totals.html"

    def get_context_data(self, **kwargs):

        ingestion = IngestionEngine()

        context = super().get_context_data(**kwargs)
        context.update({"totals": ingestion.totals_raw_sql()})
        return context