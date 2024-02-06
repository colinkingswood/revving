from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from invoices.forms import CsvUploadForm
from invoices.ingestion import IngestionEngine
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .tasks import test_task


@method_decorator(csrf_exempt, name='dispatch')
class CsvUploadView(FormView):
    """
    This will give the form to upload a csv file and have it parsed.
    """
    template_name = "upload.html"
    form_class = CsvUploadForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        # Process the CSV file
        ingestion = IngestionEngine()
        results = ingestion.parse_csv(csv_file=csv_file)
        if self.request.GET.get('format') == 'json' or self.request.headers.get('Accept') == 'application/json':
            resp_data = {"success": True, "totals": results}
            return JsonResponse(resp_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        # update the status code to indicate an error
        if self.request.GET.get('format') == 'json' or self.request.headers.get('Accept') == 'application/json':
            resp_data = {"success": False, "errors": form.errors}
            return JsonResponse(resp_data)
        resp = self.render_to_response(self.get_context_data(form=form), status=400)
        return resp

    def get_success_url(self):
        return reverse("totals_view")


class CsvUploadCeleryTask(CsvUploadView):
    """
    This is the same as the CSV Upload View, but sends teh task to celery
    """
    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        test_task.delay()
        return super().form_valid(form)


class TotalsView(TemplateView):
    template_name = "totals.html"

    def get_context_data(self, **kwargs):
        ingestion = IngestionEngine()
        context = super().get_context_data(**kwargs)
        context.update({"totals": ingestion.totals_raw_sql()})
        return context

    def render_to_response(self, context, **response_kwargs):
        # check if the request is looking for as JSON return type
        if self.request.GET.get('format') == 'json' or self.request.headers.get('Accept') == 'application/json':
            totals = context['totals']
            resp_data = {"success": True, "totals": totals}
            return JsonResponse(resp_data)

        # otherwise return a standard webpage
        return super().render_to_response(context, **response_kwargs)
