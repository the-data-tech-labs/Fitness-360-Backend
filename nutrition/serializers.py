
# diet_recommendation/serializers.py
from rest_framework import serializers
from .models import UserInput, DietRecommendation

class UserInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInput
        exclude = ['created_at']

class DietRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietRecommendation
        fields = '__all__'
