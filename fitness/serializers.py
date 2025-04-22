from rest_framework import serializers
from .models import (
    FitnessInput, 
    FitnessRecommendation, 
    UserFitnessPlan, 
    Exercise,  # Import the Exercise model
    Routine,  # Import the Routine model
    RoutineExercise,  # Import the RoutineExercise model
    FitnessPlan,  # Import the FitnessPlan model
    Progress  # Import the Progress model
)
class FitnessInputSerializer(serializers.ModelSerializer):
    """Serializer for fitness input data."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Auto-assign logged-in user

    class Meta:
        model = FitnessInput
        exclude = ['created_at']  # Exclude created_at from API responses

    def create(self, validated_data):
        """Ensures the logged-in user is assigned properly when saving."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class FitnessRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for fitness recommendations."""
    
    class Meta:
        model = FitnessRecommendation
        fields = "__all__"  # ✅ Corrected the mistake

class UserFitnessPlanSerializer(serializers.ModelSerializer):
    """Serializer for user's fitness plans."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Assigns logged-in user automatically
    recommendation = FitnessRecommendationSerializer(read_only=True)  # Nested recommendation details

    class Meta:
        model = UserFitnessPlan
        fields = ['id', 'user', 'recommendation', 'completed_exercises', 'updated_at']

    def create(self, validated_data):
        """Assigns logged-in user when saving a new fitness plan."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# serializers.py

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer()

    class Meta:
        model = RoutineExercise
        fields = '__all__'

class RoutineSerializer(serializers.ModelSerializer):
    exercises = RoutineExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Routine
        fields = '__all__'

class FitnessPlanSerializer(serializers.ModelSerializer):
    routine = RoutineSerializer()

    class Meta:
        model = FitnessPlan
        fields = '__all__'

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = '__all__'