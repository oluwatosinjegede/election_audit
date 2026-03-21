# audit_app/models.py

from django.db import models

class AuditFile(models.Model):
    voters_register = models.FileField(upload_to='uploads/')
    vote_cast = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)