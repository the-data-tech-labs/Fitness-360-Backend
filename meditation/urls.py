from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyExperienceViewSet

router = DefaultRouter()
router.register(r'experiences', DailyExperienceViewSet, basename='experience')

urlpatterns = [
    path('', include(router.urls)),
]