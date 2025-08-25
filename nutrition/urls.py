from django.urls import path
from .views import (
    DietRecommendationAPI,
    NutritionRecommendationListAPI,
    NutritionRecommendationDetailAPI,
    DeleteNutritionRecommendationAPI
)

urlpatterns = [
    path('',DietRecommendationAPI.as_view(), name='diet_recommendation'),
     path('recommendations/', NutritionRecommendationListAPI.as_view(), name='nutrition-recommendations-list'),
    path('recommendations/<int:recommendation_id>/', NutritionRecommendationDetailAPI.as_view(), name='nutrition-recommendation-detail'),
    path('recommendations/<int:recommendation_id>/delete/', DeleteNutritionRecommendationAPI.as_view(), name='delete-nutrition-recommendation'),
]