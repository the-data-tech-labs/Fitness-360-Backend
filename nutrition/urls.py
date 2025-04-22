from django.urls import path
from .views import DietRecommendationAPI

urlpatterns = [
    path('',DietRecommendationAPI.as_view(), name='diet_recommendation'),
]