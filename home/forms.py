from django import forms
from django.forms import ClearableFileInput

from .models import Document
from .util import PdfValidator


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )
        labels = {
            'document': (),
        }
        widgets = {
            'document': ClearableFileInput(attrs={
                'class': 'form-control form-control-lg', 
                'id': 'formFileLg',
                'aria-label': 'Upload'
            })
        }

    def clean_document(self, *args, **kwargs):
        doc = self.cleaned_data.get('document')

        validator = PdfValidator(doc, 30)
        if not validator.is_pdf():
            raise forms.ValidationError("Please upload pdf file only")
        
        if not validator.valid_size():
            raise forms.ValidationError(f"Pdf file should be below {validator.max_mb}MB")
        return doc