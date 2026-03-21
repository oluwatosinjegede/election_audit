# audit_app/# audit_app/forms.py

from django import forms
from .models import AuditFile

class AuditUploadForm(forms.ModelForm):
    class Meta:
        model = AuditFile
        fields = ['voters_register', 'vote_cast']

from django.db import models
