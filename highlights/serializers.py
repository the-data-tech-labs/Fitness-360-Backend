# highlights/serializers.py

from rest_framework import serializers
from .models import Highlight

class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = ['id', 'user', 'fitness_highlights', 'nutrition_highlights', 'created_at']
