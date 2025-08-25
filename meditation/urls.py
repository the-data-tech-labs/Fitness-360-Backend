from django.urls import path
from .views import MeditationExperienceView

urlpatterns = [
    path('experiences/', MeditationExperienceView.as_view(), name='meditation-experiences'),
]
