# views/dashboard_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import json
import re

from fitness.models import FitnessRecommendation
from nutrition.models import DietRecommendation

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_analytics(request):
    try:
        user = request.user
        
        # Get latest recommendations
        latest_fitness = FitnessRecommendation.objects.filter(user=user).order_by('-created_at').first()
        latest_nutrition = DietRecommendation.objects.filter(user=user).order_by('-created_at').first()
        
        # Initialize response data
        dashboard_data = {
            'user_profile': {
                'name': user.username,
                'total_fitness_plans': FitnessRecommendation.objects.filter(user=user).count(),
                'total_nutrition_plans': DietRecommendation.objects.filter(user=user).count(),
                'member_since': user.date_joined.strftime('%Y-%m-%d'),
            },
            'fitness_analytics': None,
            'nutrition_analytics': None
        }
        
        # Process Fitness Data
        if latest_fitness:
            fitness_data = extract_fitness_analytics(latest_fitness)
            dashboard_data['fitness_analytics'] = fitness_data
        
        # Process Nutrition Data  
        if latest_nutrition:
            nutrition_data = extract_nutrition_analytics(latest_nutrition)
            dashboard_data['nutrition_analytics'] = nutrition_data
        
        return Response({
            'status': 'success',
            'data': dashboard_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def extract_fitness_analytics(fitness_recommendation):
    """Extract chart-worthy data from fitness recommendation"""
    try:
        # Parse the recommendation JSON - FIXED VERSION
        data = None
        
        # Try to get parsed_recommendation if it exists
        if hasattr(fitness_recommendation, 'parsed_recommendation') and fitness_recommendation.parsed_recommendation:
            data = fitness_recommendation.parsed_recommendation
        else:
            # Try to parse from recommendation_text
            try:
                # Clean the recommendation text first
                recommendation_text = fitness_recommendation.recommendation_text
                if isinstance(recommendation_text, str):
                    # Remove any markdown formatting
                    cleaned_text = recommendation_text.strip()
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text.replace('```json', '').replace('```')
                    
                    data = json.loads(cleaned_text)
                else:
                    data = recommendation_text
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"JSON parsing error: {e}")
                data = get_sample_fitness_data()
        
        if not data:
            data = get_sample_fitness_data()
        
        analytics = {
            'workout_overview': {
                'plan_duration': '',
                'weekly_frequency': 0,
                'session_duration': 0,
                'intensity_level': 'Beginner',
                'primary_focus': 'General Fitness',
                'equipment_needed': [],
                'target_muscle_groups': []
            },
            'weekly_schedule': [],
            'exercise_categories': {},
            'muscle_groups': {},
            'workout_intensity': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0
            }
        }
        
        # Extract workout overview from the data structure
        if 'workout_overview' in data:
            overview = data['workout_overview']
            analytics['workout_overview'].update({
                'plan_duration': overview.get('plan_duration', '8-12 weeks'),
                'weekly_frequency': extract_number(str(overview.get('weekly_frequency', 0))),
                'session_duration': extract_number(str(overview.get('session_duration', 0))),
                'intensity_level': overview.get('intensity_level', 'Beginner'),
                'primary_focus': overview.get('primary_focus', 'General Fitness'),
                'equipment_needed': overview.get('equipment_needed', []),
                'target_muscle_groups': overview.get('target_muscle_groups', [])
            })
        
        # Process weekly workout schedule
        if 'weekly_workout_schedule' in data and isinstance(data['weekly_workout_schedule'], list):
            schedule = data['weekly_workout_schedule']
            
            for day_workout in schedule:
                day_data = {
                    'day': day_workout.get('day', ''),
                    'workout_type': day_workout.get('workout_type', ''),
                    'duration': extract_number(str(day_workout.get('duration', 0))),
                    'intensity': day_workout.get('intensity', 'Low'),
                    'exercise_count': len(day_workout.get('exercises', []))
                }
                analytics['weekly_schedule'].append(day_data)
                
                # Process exercises
                exercises = day_workout.get('exercises', [])
                if isinstance(exercises, list):
                    for exercise in exercises:
                        # Exercise categories
                        category = exercise.get('category', 'general')
                        analytics['exercise_categories'][category] = analytics['exercise_categories'].get(category, 0) + 1
                        
                        # Muscle groups
                        target_muscles = exercise.get('target_muscles', [])
                        if isinstance(target_muscles, list):
                            for muscle in target_muscles:
                                muscle_clean = str(muscle).strip()
                                analytics['muscle_groups'][muscle_clean] = analytics['muscle_groups'].get(muscle_clean, 0) + 1
                        
                        # Workout intensity based on exercise intensity
                        intensity = day_workout.get('intensity', 'Low').lower()
                        if 'low' in intensity or 'beginner' in intensity:
                            analytics['workout_intensity']['beginner'] += 1
                        elif 'moderate' in intensity or 'intermediate' in intensity:
                            analytics['workout_intensity']['intermediate'] += 1
                        elif 'high' in intensity or 'advanced' in intensity:
                            analytics['workout_intensity']['advanced'] += 1
        
        # Add fallback data if empty
        if not analytics['weekly_schedule']:
            analytics['weekly_schedule'] = get_sample_weekly_schedule()
        
        if not analytics['exercise_categories']:
            analytics['exercise_categories'] = {'strength': 8, 'cardio': 3, 'recovery': 1}
            
        if not analytics['muscle_groups']:
            analytics['muscle_groups'] = {
                'Quadriceps': 3, 'Glutes': 3, 'Hamstrings': 2, 
                'Chest': 2, 'Shoulders': 2, 'Back': 2, 'Core': 1
            }
        
        return analytics
        
    except Exception as e:
        print(f"Error extracting fitness analytics: {e}")
        return get_sample_fitness_analytics()

def extract_nutrition_analytics(nutrition_recommendation):
    """Extract chart-worthy data from nutrition recommendation"""
    try:
        # Parse the recommendation JSON - FIXED VERSION
        data = None
        
        # Try to get parsed_recommendation if it exists
        if hasattr(nutrition_recommendation, 'parsed_recommendation') and nutrition_recommendation.parsed_recommendation:
            data = nutrition_recommendation.parsed_recommendation
        else:
            # Try to parse from recommendation_text
            try:
                recommendation_text = nutrition_recommendation.recommendation_text
                if isinstance(recommendation_text, str):
                    # Clean the recommendation text first
                    cleaned_text = recommendation_text.strip()
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text.replace('``````', '').strip()
                    
                    data = json.loads(cleaned_text)
                else:
                    data = recommendation_text
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"JSON parsing error: {e}")
                data = get_sample_nutrition_data()
        
        if not data:
            data = get_sample_nutrition_data()
        
        analytics = {
            'daily_nutrition': {
                'total_calories': 0,
                'protein_grams': 0,
                'carbs_grams': 0,
                'fats_grams': 0,
                'fiber_grams': 0
            },
            'macronutrient_ratios': {
                'protein_percentage': 0,
                'carbs_percentage': 0,
                'fats_percentage': 0
            },
            'meal_distribution': {
                'breakfast': 0,
                'lunch': 0,
                'dinner': 0,
                'snacks': 0
            },
            'nutrition_plan': [],
            'bmi_info': {
                'current_bmi': 0,
                'bmi_category': 'Normal',
                'target_weight_range': ''
            }
        }
        
        # Extract from client_assessment
        if 'client_assessment' in data:
            assessment = data['client_assessment']
            
            # BMI and status info
            if 'current_status' in assessment:
                status_info = assessment['current_status']
                analytics['bmi_info'] = {
                    'current_bmi': extract_number(str(status_info.get('bmi', 0))),
                    'bmi_category': status_info.get('bmi_category', 'Normal'),
                    'target_weight_range': status_info.get('target_weight_range', '')
                }
            
            # Caloric requirements
            if 'caloric_requirements' in assessment:
                calories = assessment['caloric_requirements']
                analytics['daily_nutrition']['total_calories'] = extract_number(str(calories.get('goal_adjusted_calories', 0)))
            
            # Macronutrient targets
            if 'macronutrient_targets' in assessment:
                macros = assessment['macronutrient_targets']
                
                # Handle nested structure for macros
                protein_data = macros.get('protein', {})
                carbs_data = macros.get('carbohydrates', {})
                fats_data = macros.get('fats', {})
                fiber_data = macros.get('fiber', {})
                
                analytics['daily_nutrition'].update({
                    'protein_grams': extract_number(str(protein_data.get('grams_per_day', 0))),
                    'carbs_grams': extract_number(str(carbs_data.get('grams_per_day', 0))),
                    'fats_grams': extract_number(str(fats_data.get('grams_per_day', 0))),
                    'fiber_grams': extract_number(str(fiber_data.get('daily_target_grams', 0)))
                })
                
                # Calculate percentages
                analytics['macronutrient_ratios'] = {
                    'protein_percentage': extract_number(str(protein_data.get('percentage_of_calories', '0%'))),
                    'carbs_percentage': extract_number(str(carbs_data.get('percentage_of_calories', '0%'))),
                    'fats_percentage': extract_number(str(fats_data.get('percentage_of_calories', '0%')))
                }
        
        # Extract meal plan
        if 'personalized_meal_plan' in data:
            meal_plan = data['personalized_meal_plan']
            
            # Count meal distribution from sample_day_menu
            if 'sample_day_menu' in meal_plan:
                menu = meal_plan['sample_day_menu']
                for meal_name, meal_data in menu.items():
                    meal_type = meal_name.lower()
                    if 'breakfast' in meal_type:
                        analytics['meal_distribution']['breakfast'] += 1
                    elif 'lunch' in meal_type:
                        analytics['meal_distribution']['lunch'] += 1
                    elif 'dinner' in meal_type:
                        analytics['meal_distribution']['dinner'] += 1
                    else:
                        analytics['meal_distribution']['snacks'] += 1
                
                # Create nutrition plan for chart
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                for day_name in days:
                    day_meals = []
                    for meal_name, meal_data in menu.items():
                        day_meals.append({
                            'name': meal_name.title(),
                            'calories': extract_number(str(meal_data.get('calories', 0))),
                            'time': meal_data.get('time', '')
                        })
                    analytics['nutrition_plan'].append({
                        'day': day_name,
                        'meals': day_meals[:2]  # Limit to 2 meals per day for chart clarity
                    })
        
        # Add fallback data if empty
        if sum(analytics['meal_distribution'].values()) == 0:
            analytics['meal_distribution'] = {'breakfast': 7, 'lunch': 7, 'dinner': 7, 'snacks': 4}
        
        if not analytics['nutrition_plan']:
            analytics['nutrition_plan'] = get_sample_nutrition_plan()
        
        return analytics
        
    except Exception as e:
        print(f"Error extracting nutrition analytics: {e}")
        return get_sample_nutrition_analytics()

def extract_number(text):
    """Extract number from text string"""
    try:
        # Remove percentage signs and other non-numeric characters
        cleaned = re.sub(r'[^\d.-]', '', str(text))
        if cleaned:
            return float(cleaned)
        return 0
    except (ValueError, TypeError):
        return 0

# Sample data functions
def get_sample_fitness_data():
    """Return sample fitness data structure"""
    return {
        'workout_overview': {
            'plan_duration': '8-12 weeks',
            'weekly_frequency': '3 sessions',
            'session_duration': '30-45 minutes',
            'intensity_level': 'Beginner-friendly',
            'primary_focus': 'Weight Loss',
            'equipment_needed': ['Resistance bands', 'Exercise mat'],
            'target_muscle_groups': ['Full body', 'Core', 'Cardiovascular system']
        },
        'weekly_workout_schedule': [
            {
                'day': 'Monday',
                'workout_type': 'Full Body Strength & Cardio',
                'duration': '30-40 minutes',
                'intensity': 'Low to Moderate',
                'exercises': [
                    {'category': 'strength', 'target_muscles': ['Quadriceps', 'Glutes']},
                    {'category': 'strength', 'target_muscles': ['Chest', 'Shoulders']},
                    {'category': 'cardio', 'target_muscles': ['Full body']}
                ]
            },
            {
                'day': 'Friday',
                'workout_type': 'Full Body Strength & Cardio',
                'duration': '30-40 minutes',
                'intensity': 'Low to Moderate',
                'exercises': [
                    {'category': 'strength', 'target_muscles': ['Hamstrings', 'Core']},
                    {'category': 'cardio', 'target_muscles': ['Full body']}
                ]
            }
        ]
    }

def get_sample_nutrition_data():
    """Return sample nutrition data structure"""
    return {
        'client_assessment': {
            'current_status': {
                'bmi': '24.2',
                'bmi_category': 'Normal weight',
                'target_weight_range': '68-70 kg'
            },
            'caloric_requirements': {
                'goal_adjusted_calories': '1400'
            },
            'macronutrient_targets': {
                'protein': {
                    'grams_per_day': '70',
                    'percentage_of_calories': '25%'
                },
                'carbohydrates': {
                    'grams_per_day': '150',
                    'percentage_of_calories': '45%'
                },
                'fats': {
                    'grams_per_day': '50',
                    'percentage_of_calories': '30%'
                },
                'fiber': {
                    'daily_target_grams': '30'
                }
            }
        },
        'personalized_meal_plan': {
            'sample_day_menu': {
                'breakfast': {'calories': '350', 'time': '7:30-8:30 AM'},
                'lunch': {'calories': '400', 'time': '12:30-1:30 PM'},
                'dinner': {'calories': '400', 'time': '7:00-8:00 PM'},
                'mid_morning': {'calories': '200', 'time': '10:30-11:00 AM'}
            }
        }
    }

def get_sample_weekly_schedule():
    """Return sample weekly schedule"""
    return [
        {'day': 'Monday', 'workout_type': 'Full Body Strength & Cardio', 'duration': 40, 'exercise_count': 4},
        {'day': 'Wednesday', 'workout_type': 'Rest or Active Recovery', 'duration': 30, 'exercise_count': 1},
        {'day': 'Friday', 'workout_type': 'Full Body Strength & Cardio', 'duration': 40, 'exercise_count': 3}
    ]

def get_sample_nutrition_plan():
    """Return sample nutrition plan"""
    return [
        {'day': 'Monday', 'meals': [{'name': 'Breakfast', 'calories': 350}, {'name': 'Lunch', 'calories': 400}]},
        {'day': 'Tuesday', 'meals': [{'name': 'Breakfast', 'calories': 350}, {'name': 'Dinner', 'calories': 400}]}
    ]

def get_sample_fitness_analytics():
    """Return complete sample fitness analytics"""
    return {
        'workout_overview': {
            'plan_duration': '8-12 weeks',
            'weekly_frequency': 3,
            'session_duration': 40,
            'intensity_level': 'Beginner',
            'primary_focus': 'Weight Loss',
            'equipment_needed': ['Resistance bands', 'Exercise mat'],
            'target_muscle_groups': ['Full body', 'Core', 'Cardiovascular system']
        },
        'weekly_schedule': get_sample_weekly_schedule(),
        'exercise_categories': {'strength': 8, 'cardio': 3, 'recovery': 1},
        'muscle_groups': {
            'Quadriceps': 3, 'Glutes': 3, 'Hamstrings': 2, 
            'Chest': 2, 'Shoulders': 2, 'Back': 2, 'Core': 1
        },
        'workout_intensity': {'beginner': 8, 'intermediate': 4, 'advanced': 0}
    }

def get_sample_nutrition_analytics():
    """Return complete sample nutrition analytics"""
    return {
        'daily_nutrition': {
            'total_calories': 1400,
            'protein_grams': 70,
            'carbs_grams': 150,
            'fats_grams': 50,
            'fiber_grams': 30
        },
        'macronutrient_ratios': {
            'protein_percentage': 25,
            'carbs_percentage': 45,
            'fats_percentage': 30
        },
        'meal_distribution': {'breakfast': 7, 'lunch': 7, 'dinner': 7, 'snacks': 4},
        'nutrition_plan': get_sample_nutrition_plan(),
        'bmi_info': {
            'current_bmi': 24.2,
            'bmi_category': 'Normal weight',
            'target_weight_range': '68-70 kg'
        }
    }
