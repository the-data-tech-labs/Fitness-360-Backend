# diet_recommendation/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserProfileSerializer, DietRecommendationSerializer
from .models import UserProfile, DietRecommendation
import google.generativeai as genai
import os

def calculate_bmi(weight, height):
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

class DietRecommendationAPI(APIView):
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()

            # Calculate BMI
            bmi, bmi_category = calculate_bmi(profile.weight, profile.height)

            # Configure Google Gemini API
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-pro")

            # Generate diet recommendation
            prompt = f"""
            You are an expert nutritionist specializing in personalized diet planning. Create a detailed, culturally-appropriate diet plan based on the following profile:

            INDIVIDUAL PROFILE:
            - Age: {profile.age} years
            - Gender: {profile.gender}
            - Current Weight: {profile.weight} kg
            - Height: {profile.height} cm
            - Dietary Preference: {profile.food_type}
            - Health Goal: {profile.goal}
            - Medical Conditions: {profile.disease}
            - Food Allergies/Restrictions: {profile.allergics}
            - Target Timeline: {profile.Target_timeline}

            Please create a highly personalized nutrition plan following this EXACT format:

            1. NUTRITIONAL ANALYSIS
            A. Current Status
                - BMI and healthy weight range
                - Daily caloric requirements
                - Required macro distribution (protein, carbs, fats)
                - Micronutrient focus areas

            B. Goal-Specific Adjustments
                - Adjusted calorie targets for {profile.goal}
                - Special dietary considerations for {profile.disease}
                - Allergy-safe alternatives for {profile.allergics}

            2. PERSONALIZED MEAL PLAN
            A. Daily Nutrition Targets
                - Calories: [exact number] kcal
                - Protein: [x] g
                - Carbohydrates: [x] g
                - Healthy Fats: [x] g
                - Fiber: [x] g
                - Water: [x] liters

            B. Meal Schedule (with exact portions)
                1. Early Morning (6-7 AM)
                    - Detailed items with quantities
                    - Calories and macro breakdown
                
                2. Breakfast (8-9 AM)
                    - Detailed items with quantities
                    - Calories and macro breakdown
                
                3. Mid-Morning (11 AM)
                    - Detailed items with quantities
                    - Calories and macro breakdown
                
                4. Lunch (1-2 PM)
                    - Detailed items with quantities
                    - Calories and macro breakdown
                
                5. Evening Snack (4-5 PM)
                    - Detailed items with quantities
                    - Calories and macro breakdown
                
                6. Dinner (7-8 PM)
                    - Detailed items with quantities
                    - Calories and macro breakdown

            3. FOOD RECOMMENDATIONS
            A. Essential Foods to Include Daily
                - List 10 specific foods with benefits
                - Recommended portions
                - Best times to consume

            B. Foods to Limit/Avoid
                - List specific foods
                - Reasons for avoiding
                - Healthy alternatives

            4. MEAL PREPARATION GUIDELINES
            A. Cooking Methods
                - Recommended cooking techniques
                - Tips for nutrient preservation
                - Meal prep suggestions

            B. Portion Control
                - Visual portion guides
                - Measuring techniques
                - Portion adjustments based on activity

            5. HYDRATION AND SUPPLEMENTS
            A. Hydration Schedule
                - Daily water intake goals
                - Best times to drink water
                - Hydration tips

            B. Recommended Supplements
                - Essential supplements if needed
                - Natural food alternatives
                - Timing and dosage

            6. PROGRESS MONITORING
            A. Weekly Milestones
                - Expected progress markers
                - Measurements to track
                - Adjustment triggers

            B. Success Indicators
                - Physical indicators
                - Energy levels
                - Digestive health markers

            SPECIAL INSTRUCTIONS:
            1. Include local food alternatives
            2. Account for seasonal availability
            3. Provide budget-friendly options
            4. Consider cooking time constraints
            5. Include simple recipes for key meals
            6. List emergency food options
            7. Provide meal prep shortcuts

            Note: This nutrition plan is specifically designed for achieving {profile.goal} within {profile.Target_timeline}, taking into account {profile.food_type} dietary preferences and {profile.disease} health considerations.

            Please format the response in a clean, easy-to-read format without markdown symbols.
            """
            response = model.generate_content(prompt)
            recommendation_text = response.text.replace('*', '').replace('#', '').replace('```', '')

            # Save the recommendation
            diet_recommendation = DietRecommendation.objects.create(
                profile=profile,
                recommendation_text=recommendation_text,
                bmi=bmi,
                bmi_category=bmi_category
            )

            recommendation_serializer = DietRecommendationSerializer(diet_recommendation)
            return Response(recommendation_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)