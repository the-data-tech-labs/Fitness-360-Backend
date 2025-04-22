from rest_framework import serializers
from .models import DailyExperience, MeditationRecommendation

class MeditationRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationRecommendation
        fields = ['id', 'meditation_type', 'duration_minutes', 'how_to_perform', 'benefits']

class DailyExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyExperience
        fields = ['id', 'experience_text', 'created_at']

class ExperienceWithRecommendationsSerializer(serializers.ModelSerializer):
    recommendations = MeditationRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = DailyExperience
        fields = ['id', 'experience_text', 'created_at', 'recommendations']