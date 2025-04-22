from django.contrib import admin

# Register your models here.
from .models import FitnessRecommendation, FitnessInput

# Register the model
admin.site.register(FitnessInput)
admin.site.register(FitnessRecommendation)