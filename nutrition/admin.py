from django.contrib import admin

# Register your models here.
from .models import UserInput
from .models import DietRecommendation

# Register the model
admin.site.register(UserInput)
admin.site.register(DietRecommendation)