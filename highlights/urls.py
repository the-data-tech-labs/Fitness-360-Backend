# highlights/urls.py

from django.urls import path
from .views import GenerateHighlightsAPI

urlpatterns = [
    path('generate/', GenerateHighlightsAPI.as_view(), name='generate_highlights'),
]




