from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import FitnessInput, FitnessRecommendation,UserFitnessPlan


import google.generativeai as genai
import os
from .serializers import FitnessInputSerializer, FitnessRecommendationSerializer
from dotenv import load_dotenv

load_dotenv()

def calculate_bmi(weight, height):
    """Calculates BMI and returns category."""
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    
    if bmi < 18.5:
        category = 'Underweight'
    elif 18.5 <= bmi < 24.9:
        category = 'Normal weight'
    elif 25 <= bmi < 29.9:
        category = 'Overweight'
    else:
        category = 'Obesity'
    
    return bmi, category

# views.py

class FitnessRecommendationAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FitnessInputSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            profile = serializer.save(user=request.user)
            
            bmi, bmi_category = calculate_bmi(profile.weight, profile.height)

            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-1.5-pro")

            prompt = f"""
            As an expert fitness trainer, create a structured fitness plan for:

            Age: {profile.age}
            Gender: {profile.gender}
            Weight: {profile.weight} kg
            Height: {profile.height} cm
            Goal: {profile.goal}
            Fitness Level: {profile.fitness_level}
            Activity Level: {profile.activity_level}
            Exercise Setting: {profile.exercise_setting}
            Sleep Pattern: {profile.sleep_pattern}
            Focus Areas: {profile.specific_area}
            Target Timeline: {profile.target_timeline}
            Medical Conditions: {profile.medical_conditions}
            Injuries: {profile.injuries_or_physical_limitation}

            Ensure the plan includes:
            - Detailed exercise descriptions
            - Proper warm-up and cool-down routines
            - Safety precautions
            - Modifications for different fitness levels
            - Recovery protocols
            """

            try:
                response = model.generate_content(prompt)
                recommendation_text = response.text if response.text else "No recommendation generated."
                recommendation_text = recommendation_text.replace('*', '').replace('#', '')
            except Exception as e:
                return Response({"error": f"AI generation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            fitness_recommendation = FitnessRecommendation.objects.create(
                user=request.user,
                profile=profile,
                recommendation_text=recommendation_text,
                bmi=bmi,
                bmi_category=bmi_category
            )

            recommendation_serializer = FitnessRecommendationSerializer(fitness_recommendation)
            return Response(recommendation_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFitnessPlansAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the latest fitness plan of the logged-in user
        latest_plan = UserFitnessPlan.objects.filter(user=request.user).order_by('-created_at').first()

        if latest_plan:
            serializer = UserFitnessPlanSerializer(latest_plan)
            return Response(serializer.data, status=200)
        else:
            return Response({"message": "No fitness plan found"},status=404)

# views.py

class UserStatsAPI(APIView):
    """
    API endpoint to fetch stats for the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        fitness_plan = FitnessPlan.objects.filter(user=user).order_by('-start_date').first()

        if not fitness_plan:
            return Response({"message": "No fitness plan found"}, status=404)

        stats = {
            "plan_completion_percentage": calculate_plan_completion(user, fitness_plan),
            "total_calories_burned": calculate_total_calories_burned(user, fitness_plan),
            "progress_over_time": track_progress_over_time(user, fitness_plan),
        }

        return Response(stats, status=200)

# views.py

# Helper functions for stats
def calculate_plan_completion(user, fitness_plan):
    """
    Calculate the percentage of the fitness plan completed by the user.
    """
    total_days = (fitness_plan.end_date - fitness_plan.start_date).days
    completed_days = Progress.objects.filter(fitness_plan=fitness_plan, user=user).count()
    completion_percentage = (completed_days / total_days) * 100 if total_days > 0 else 0
    return completion_percentage

def calculate_total_calories_burned(user, fitness_plan):
    """
    Calculate the total calories burned by the user based on completed exercises.
    """
    progress_records = Progress.objects.filter(fitness_plan=fitness_plan, user=user)
    total_calories = 0
    for progress in progress_records:
        for exercise, completed in progress.completed_exercises.items():
            if completed:
                exercise_obj = Exercise.objects.get(name=exercise)
                total_calories += exercise_obj.calories_burned
    return total_calories

def track_progress_over_time(user, fitness_plan):
    """
    Track the user's progress over time (e.g., completed exercises per day).
    """
    progress_records = Progress.objects.filter(fitness_plan=fitness_plan, user=user).order_by('date')
    progress_data = []
    for progress in progress_records:
        progress_data.append({
            'date': progress.date,
            'completed_exercises': progress.completed_exercises
        })
    return progress_data