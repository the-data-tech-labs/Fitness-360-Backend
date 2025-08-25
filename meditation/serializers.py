from rest_framework import serializers

class MeditationExperienceSerializer(serializers.Serializer):
    experience_text = serializers.CharField(
        max_length=1000,
        help_text="Describe your current state of mind, feelings, or what you're going through"
    )
    
    def validate_experience_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Experience text cannot be empty")
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a more detailed description (at least 10 characters)")
            
        return value.strip()

class MeditationRecommendationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    meditation_type = serializers.CharField()
    duration_minutes = serializers.IntegerField()
    benefits = serializers.CharField()
    how_to_perform = serializers.CharField()
    difficulty_level = serializers.CharField(required=False)
    best_time = serializers.CharField(required=False)
