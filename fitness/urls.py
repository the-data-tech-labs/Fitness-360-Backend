from django.urls import path
from .views import FitnessRecommendationAPI, UserFitnessPlansAPI

urlpatterns = [
    path('fitness-recommendation/', FitnessRecommendationAPI.as_view(), name='fitness-recommendation'),
    path('user-plans/', UserFitnessPlansAPI.as_view(), name='user-plans'),
]