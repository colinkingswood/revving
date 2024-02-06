from django import forms
from django.forms.widgets import ClearableFileInput


class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(required=True,
                               widget=ClearableFileInput(attrs={"class": "from-control"})
                               )
