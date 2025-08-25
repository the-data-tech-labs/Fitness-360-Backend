# highlights/urls.py

from django.urls import path
# from .views import GenerateHighlightsAPI
from highlights.views import dashboard_analytics

urlpatterns = [
    # path('generate/', GenerateHighlightsAPI.as_view(), name='generate_highlights'),
    path('analytics/', dashboard_analytics, name='dashboard_analytics'),
]




