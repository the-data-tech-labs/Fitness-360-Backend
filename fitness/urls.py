from django.urls import path
from .views import FitnessRecommendationAPI, FitnessRecommendationListAPI, FitnessRecommendationDetailAPI, DeleteFitnessRecommendationAPI

urlpatterns = [
    path('fitness-recommendation/', FitnessRecommendationAPI.as_view(), name='fitness-recommendation'),
    path('recommendations/', FitnessRecommendationListAPI.as_view(), name='fitness-recommendations-list'),
    path('recommendations/<int:recommendation_id>/', FitnessRecommendationDetailAPI.as_view(), name='fitness-recommendation-detail'),
    path('recommendations/<int:recommendation_id>/delete/', DeleteFitnessRecommendationAPI.as_view(), name='delete-fitness-recommendation'),
]