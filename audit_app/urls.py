# audit_app/urls.py

from django.urls import path
from .views import upload_files, export_invalid, export_duplicates

urlpatterns = [
    path('', upload_files, name='upload'),

    # Add here
    path('export/invalid/', export_invalid, name='export_invalid'),
    path('export/duplicates/', export_duplicates, name='export_duplicates'),

    path('export/fuzzy/', export_fuzzy, name='export_fuzzy'),
]