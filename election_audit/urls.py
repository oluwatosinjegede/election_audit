# main urls.py

from django.urls import path, include

urlpatterns = [
    path('', include('audit_app.urls')),
]