from django import forms


from django.forms.widgets import ClearableFileInput

# class BootstrapClearableFileInput(ClearableFileInput):
#     def __init__(self, attrs=None, include_preview=True):
#         # Ensure the base class __init__ is called with the updated attrs
#         super().__init__(attrs={'class': 'btn btn-primary'} if attrs is None else attrs)
#         self.include_preview = include_preview

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(required=True,
                               widget=forms.ClearableFileInput(attrs={"class": "from-control"})
#                               widget=BootstrapClearableFileInput(attrs={"class": "btn btn-primary"})
                               )




