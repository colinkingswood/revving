from django.shortcuts import render
from django.views.generic import FormView

# Create your views here.

class CvsUploadView(FormView):
    template_name = "upload.html"
