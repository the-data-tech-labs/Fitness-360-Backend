from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

from .models import FitnessInput, FitnessRecommendation, UserFitnessPlan
from .serializers import FitnessInputSerializer, FitnessRecommendationSerializer, UserFitnessPlanSerializer

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
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Focused fitness-only prompt
            prompt = f"""
            As an expert fitness trainer, create a comprehensive workout plan in JSON format for the following user profile:

            User Profile:
            - Age: {profile.age}
            - Gender: {profile.gender}
            - Weight: {profile.weight} kg
            - Height: {profile.height} cm
            - BMI: {bmi:.1f} ({bmi_category})
            - Primary Goal: {profile.goal}
            - Current Fitness Level: {profile.fitness_level}
            - Activity Level: {profile.activity_level}
            - Preferred Exercise Setting: {profile.exercise_setting}
            - Focus Areas: {profile.specific_area or 'Full body'}
            - Target Timeline: {profile.target_timeline or '8-12 weeks'}
            - Medical Conditions: {profile.medical_conditions or 'None specified'}
            - Injuries/Limitations: {profile.injuries_or_physical_limitation or 'None specified'}

            Create a structured workout plan focusing ONLY on fitness and exercise. Provide the response in the following JSON structure:

            {{
                "workout_overview": {{
                    "plan_duration": "8-12 weeks",
                    "weekly_frequency": "4-5 sessions",
                    "session_duration": "45-60 minutes",
                    "intensity_level": "Progressive from moderate to high",
                    "primary_focus": "{profile.goal.replace('_', ' ').title()}",
                    "equipment_needed": ["Dumbbells", "Resistance bands", "Exercise mat"],
                    "target_muscle_groups": ["Full body", "Core", "Cardiovascular system"]
                }},
                "weekly_workout_schedule": [
                    {{
                        "day": "Monday",
                        "workout_type": "Upper Body Strength",
                        "duration": "45-50 minutes",
                        "intensity": "Moderate to High",
                        "exercises": [
                            {{
                                "name": "Push-ups",
                                "category": "strength",
                                "target_muscles": ["Chest", "Shoulders", "Triceps"],
                                "sets": "3-4",
                                "reps": "8-12",
                                "rest_between_sets": "60-90 seconds",
                                "technique_notes": "Keep core engaged, full range of motion, controlled movement",
                                "beginner_modification": "Wall push-ups or knee push-ups",
                                "advanced_variation": "Decline push-ups or one-arm push-ups",
                                "common_mistakes": ["Sagging hips", "Incomplete range of motion"]
                            }},
                            {{
                                "name": "Dumbbell Rows",
                                "category": "strength",
                                "target_muscles": ["Back", "Biceps"],
                                "sets": "3",
                                "reps": "10-12",
                                "rest_between_sets": "60 seconds",
                                "technique_notes": "Pull elbow back, squeeze shoulder blades",
                                "beginner_modification": "Lighter weights, focus on form",
                                "advanced_variation": "Single-arm rows with pause",
                                "common_mistakes": ["Using momentum", "Rounding shoulders"]
                            }}
                        ]
                    }},
                    {{
                        "day": "Tuesday",
                        "workout_type": "Lower Body & Core",
                        "duration": "45-50 minutes", 
                        "intensity": "Moderate to High",
                        "exercises": [
                            {{
                                "name": "Bodyweight Squats",
                                "category": "strength",
                                "target_muscles": ["Quadriceps", "Glutes", "Hamstrings"],
                                "sets": "3-4",
                                "reps": "12-15",
                                "rest_between_sets": "60 seconds",
                                "technique_notes": "Feet hip-width apart, knees track over toes",
                                "beginner_modification": "Chair-assisted squats",
                                "advanced_variation": "Jump squats or pistol squats",
                                "common_mistakes": ["Knees caving in", "Not going deep enough"]
                            }}
                        ]
                    }}
                ],
                "warm_up_routine": [
                    {{
                        "exercise": "Light cardio",
                        "duration": "5-10 minutes",
                        "description": "Walking, jogging in place, or stationary bike",
                        "purpose": "Increase heart rate and blood flow"
                    }},
                    {{
                        "exercise": "Dynamic stretching",
                        "duration": "5 minutes",
                        "description": "Arm circles, leg swings, hip rotations",
                        "purpose": "Prepare joints and muscles for movement"
                    }},
                    {{
                        "exercise": "Activation exercises",
                        "duration": "3-5 minutes",
                        "description": "Glute bridges, band pull-aparts, bodyweight squats",
                        "purpose": "Activate target muscle groups"
                    }}
                ],
                "cool_down_routine": [
                    {{
                        "exercise": "Light walking",
                        "duration": "5 minutes",
                        "description": "Gradually decrease heart rate",
                        "purpose": "Recovery and circulation"
                    }},
                    {{
                        "exercise": "Static stretching",
                        "duration": "10-15 minutes",
                        "description": "Hold stretches for 30 seconds each",
                        "purpose": "Improve flexibility and prevent stiffness"
                    }},
                    {{
                        "exercise": "Deep breathing",
                        "duration": "2-3 minutes",
                        "description": "Controlled breathing to relax",
                        "purpose": "Mental relaxation and stress relief"
                    }}
                ],
                "progression_guidelines": {{
                    "week_1_2": {{
                        "focus": "Form and technique mastery",
                        "intensity": "60-70% effort",
                        "progression_rule": "Perfect form over heavy weights"
                    }},
                    "week_3_4": {{
                        "focus": "Gradual intensity increase",
                        "intensity": "70-80% effort",
                        "progression_rule": "Increase weight by 5-10% or add 2-3 reps"
                    }},
                    "week_5_6": {{
                        "focus": "Strength and endurance building",
                        "intensity": "80-85% effort",
                        "progression_rule": "Add advanced variations or reduce rest time"
                    }},
                    "week_7_8": {{
                        "focus": "Peak performance and challenge",
                        "intensity": "85-90% effort",
                        "progression_rule": "Maximum effort with proper form"
                    }}
                }},
                "exercise_modifications": {{
                    "for_injuries": [
                        "Replace high-impact exercises with low-impact alternatives",
                        "Use supported versions of exercises when needed",
                        "Focus on pain-free range of motion"
                    ],
                    "for_beginners": [
                        "Start with bodyweight versions before adding weights",
                        "Use assisted variations when needed",
                        "Focus on 2-3 sets instead of 4"
                    ],
                    "for_advanced": [
                        "Add plyometric variations for power",
                        "Incorporate single-limb exercises for stability",
                        "Use tempo variations (slow negatives, pauses)"
                    ]
                }},
                "workout_safety_guidelines": [
                    "Always warm up for at least 10 minutes before intense exercise",
                    "Stop immediately if you feel sharp pain or discomfort",
                    "Maintain proper form throughout all exercises",
                    "Stay hydrated during workouts",
                    "Allow at least 48 hours rest between working the same muscle groups",
                    "Listen to your body and adjust intensity as needed"
                ],
                "recovery_recommendations": [
                    "Schedule 1-2 complete rest days per week",
                    "Include light active recovery (walking, gentle yoga) on rest days",
                    "Prioritize 7-9 hours of quality sleep for muscle recovery",
                    "Consider foam rolling or self-massage after workouts"
                ],
                "tracking_metrics": [
                    "Record weights used and reps completed for each exercise",
                    "Track workout duration and perceived exertion (1-10 scale)",
                    "Monitor progress photos and body measurements weekly",
                    "Note energy levels and recovery between sessions"
                ]
            }}

            Generate a comprehensive fitness plan specifically designed for someone at the {profile.fitness_level} level with the primary goal of {profile.goal.replace('_', ' ')} in a {profile.exercise_setting} setting. 

            Consider the following guidelines:
            - If medical conditions or injuries are mentioned, provide appropriate exercise modifications
            - Scale the intensity and complexity based on the fitness level
            - Include both strength and cardiovascular components unless contraindicated
            - Provide clear progression from beginner-friendly to more challenging variations
            - Focus on functional movements that support the stated goal
            
            IMPORTANT: Return ONLY the JSON object without any additional text, markdown formatting, or code blocks.
            """

            try:
                response = model.generate_content(prompt)
                if not response.text:
                    return Response({"error": "No recommendation generated."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Clean up the response text
                recommendation_text = response.text.strip()
                
                # Remove potential markdown code blocks
                if recommendation_text.startswith('```json'):
                    recommendation_text = recommendation_text[7:]
                if recommendation_text.startswith('```'):
                    recommendation_text = recommendation_text[3:]
                if recommendation_text.endswith('```'):
                    recommendation_text = recommendation_text[:-3]
                
                recommendation_text = recommendation_text.strip()
                
                # Try to parse JSON to validate structure
                try:
                    import json
                    parsed_json = json.loads(recommendation_text)
                    # Re-stringify to ensure clean JSON
                    recommendation_text = json.dumps(parsed_json, indent=2)
                except json.JSONDecodeError as e:
                    # Fallback to plain text if JSON parsing fails
                    recommendation_text = f"Error parsing AI response as JSON: {str(e)}\n\nRaw response:\n{recommendation_text}"  
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


        


class FitnessRecommendationListAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            filter_by = request.GET.get('filter', 'all')  # all, this_week, this_month, last_3_months
            
            # Base queryset - only user's recommendations
            queryset = FitnessRecommendation.objects.filter(
                user=request.user
            ).select_related('user', 'profile').order_by('-created_at')
            
            # Apply search filter if provided
            if search:
                queryset = queryset.filter(
                    Q(profile__goal__icontains=search) |
                    Q(bmi_category__icontains=search) |
                    Q(profile__fitness_level__icontains=search) |
                    Q(profile__activity_level__icontains=search)
                )
            
            # Apply date filters
            today = datetime.now()
            
            if filter_by == 'this_week':
                week_ago = today - timedelta(days=7)
                queryset = queryset.filter(created_at__gte=week_ago)
            elif filter_by == 'this_month':
                month_ago = today - timedelta(days=30)
                queryset = queryset.filter(created_at__gte=month_ago)
            elif filter_by == 'last_3_months':
                three_months_ago = today - timedelta(days=90)
                queryset = queryset.filter(created_at__gte=three_months_ago)
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Paginate results
            paginator = Paginator(queryset, page_size)
            
            if page > paginator.num_pages:
                page = paginator.num_pages if paginator.num_pages > 0 else 1
            
            page_obj = paginator.get_page(page)
            recommendations = page_obj.object_list
            
            # Serialize data
            serialized_data = []
            for recommendation in recommendations:
                try:
                    # Parse the recommendation_text JSON if it exists
                    parsed_recommendation = None
                    if recommendation.recommendation_text:
                        try:
                            parsed_recommendation = json.loads(recommendation.recommendation_text)
                        except json.JSONDecodeError:
                            parsed_recommendation = None
                    
                    recommendation_data = {
                        'id': recommendation.id,
                        'created_at': recommendation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'created_date': recommendation.created_at.strftime('%B %d, %Y'),
                        'created_time': recommendation.created_at.strftime('%I:%M %p'),
                        'bmi': round(float(recommendation.bmi), 1) if recommendation.bmi else None,
                        'bmi_category': recommendation.bmi_category,
                        'profile_data': {
                            'age': recommendation.profile.age,
                            'gender': recommendation.profile.gender,
                            'weight': float(recommendation.profile.weight),
                            'height': float(recommendation.profile.height),
                            'fitness_level': recommendation.profile.fitness_level,
                            'activity_level': recommendation.profile.activity_level,
                            'goal': recommendation.profile.goal,
                            'specific_area': recommendation.profile.specific_area,
                            'target_timeline': recommendation.profile.target_timeline,
                            'medical_conditions': recommendation.profile.medical_conditions,
                            'injuries_or_physical_limitation': recommendation.profile.injuries_or_physical_limitation,
                            'exercise_setting': recommendation.profile.exercise_setting,
                            'sleep_pattern': recommendation.profile.sleep_pattern,
                            'stress_level': recommendation.profile.stress_level,
                        },
                        'recommendation_summary': self.get_recommendation_summary(parsed_recommendation),
                        'recommendation_text': recommendation.recommendation_text,
                        'parsed_recommendation': parsed_recommendation,
                        'has_workout_plan': bool(parsed_recommendation and parsed_recommendation.get('weekly_workout_schedule')),
                        'workout_frequency': self.get_workout_frequency(parsed_recommendation),
                        'plan_duration': self.get_plan_duration(parsed_recommendation),
                    }
                    serialized_data.append(recommendation_data)
                    
                except Exception as e:
                    print(f"Error processing recommendation {recommendation.id}: {str(e)}")
                    continue
            
            # Calculate statistics
            stats = self.get_user_stats(request.user)
            
            return Response({
                'status': 'success',
                'data': {
                    'recommendations': serialized_data,
                    'pagination': {
                        'current_page': page,
                        'total_pages': paginator.num_pages,
                        'total_count': total_count,
                        'page_size': page_size,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                        'next_page': page + 1 if page_obj.has_next() else None,
                        'previous_page': page - 1 if page_obj.has_previous() else None,
                    },
                    'filters': {
                        'current_filter': filter_by,
                        'search_query': search,
                        'available_filters': [
                            {'value': 'all', 'label': 'All Time'},
                            {'value': 'this_week', 'label': 'This Week'},
                            {'value': 'this_month', 'label': 'This Month'},
                            {'value': 'last_3_months', 'label': 'Last 3 Months'},
                        ]
                    },
                    'statistics': stats
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Failed to fetch fitness recommendations',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_recommendation_summary(self, parsed_recommendation):
        """Extract key summary information from the recommendation"""
        if not parsed_recommendation:
            return None
        
        summary = {}
        
        # Extract workout overview
        if 'workout_overview' in parsed_recommendation:
            overview = parsed_recommendation['workout_overview']
            summary.update({
                'weekly_frequency': overview.get('weekly_frequency', 'N/A'),
                'session_duration': overview.get('session_duration', 'N/A'),
                'intensity_level': overview.get('intensity_level', 'N/A'),
                'plan_duration': overview.get('plan_duration', 'N/A'),
            })
        
        # Count total exercises
        total_exercises = 0
        if 'weekly_workout_schedule' in parsed_recommendation:
            for day in parsed_recommendation['weekly_workout_schedule']:
                if 'exercises' in day:
                    total_exercises += len(day['exercises'])
        
        summary['total_exercises'] = total_exercises
        summary['total_workout_days'] = len(parsed_recommendation.get('weekly_workout_schedule', []))
        
        return summary
    
    def get_workout_frequency(self, parsed_recommendation):
        """Get workout frequency from recommendation"""
        if not parsed_recommendation:
            return None
        
        if 'workout_overview' in parsed_recommendation:
            return parsed_recommendation['workout_overview'].get('weekly_frequency')
        
        return None
    
    def get_plan_duration(self, parsed_recommendation):
        """Get plan duration from recommendation"""
        if not parsed_recommendation:
            return None
        
        if 'workout_overview' in parsed_recommendation:
            return parsed_recommendation['workout_overview'].get('plan_duration')
        
        return None
    
    def get_user_stats(self, user):
        """Get user fitness statistics"""
        try:
            recommendations = FitnessRecommendation.objects.filter(user=user)
            total_count = recommendations.count()
            
            if total_count == 0:
                return {
                    'total_plans': 0,
                    'this_month': 0,
                    'most_common_goal': None,
                    'latest_bmi': None,
                    'progress_trend': None
                }
            
            # Get this month's count
            month_ago = datetime.now() - timedelta(days=30)
            this_month_count = recommendations.filter(created_at__gte=month_ago).count()
            
            # Get most common goal
            most_common_goal = recommendations.values('profile__goal').annotate(
                count=Count('profile__goal')
            ).order_by('-count').first()
            
            # Get latest BMI
            latest_recommendation = recommendations.order_by('-created_at').first()
            latest_bmi = None
            if latest_recommendation and latest_recommendation.bmi:
                latest_bmi = {
                    'value': round(float(latest_recommendation.bmi), 1),
                    'category': latest_recommendation.bmi_category
                }
            
            # Calculate progress trend (compare last 2 BMI values)
            progress_trend = None
            if recommendations.count() >= 2:
                recent_recommendations = recommendations.order_by('-created_at')[:2]
                if recent_recommendations.bmi and recent_recommendations[1].bmi:
                    current_bmi = float(recent_recommendations.bmi)
                    previous_bmi = float(recent_recommendations[1].bmi)
                    
                    if current_bmi < previous_bmi:
                        progress_trend = 'improving'
                    elif current_bmi > previous_bmi:
                        progress_trend = 'needs_attention'
                    else:
                        progress_trend = 'stable'
            
            return {
                'total_plans': total_count,
                'this_month': this_month_count,
                'most_common_goal': most_common_goal['profile__goal'] if most_common_goal else None,
                'latest_bmi': latest_bmi,
                'progress_trend': progress_trend
            }
            
        except Exception as e:
            print(f"Error calculating user stats: {str(e)}")
            return {
                'total_plans': 0,
                'this_month': 0,
                'most_common_goal': None,
                'latest_bmi': None,
                'progress_trend': None
            }


class FitnessRecommendationDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, recommendation_id):
        try:
            # Get specific recommendation for the user
            recommendation = FitnessRecommendation.objects.get(
                id=recommendation_id,
                user=request.user
            )
            
            # Parse the recommendation JSON
            parsed_recommendation = None
            if recommendation.recommendation_text:
                try:
                    parsed_recommendation = json.loads(recommendation.recommendation_text)
                except json.JSONDecodeError:
                    parsed_recommendation = None
            
            recommendation_data = {
                'id': recommendation.id,
                'created_at': recommendation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'created_date': recommendation.created_at.strftime('%B %d, %Y'),
                'created_time': recommendation.created_at.strftime('%I:%M %p'),
                'bmi': round(float(recommendation.bmi), 1) if recommendation.bmi else None,
                'bmi_category': recommendation.bmi_category,
                'profile_data': {
                    'age': recommendation.profile.age,
                    'gender': recommendation.profile.gender,
                    'weight': float(recommendation.profile.weight),
                    'height': float(recommendation.profile.height),
                    'fitness_level': recommendation.profile.fitness_level,
                    'activity_level': recommendation.profile.activity_level,
                    'goal': recommendation.profile.goal,
                    'specific_area': recommendation.profile.specific_area,
                    'target_timeline': recommendation.profile.target_timeline,
                    'medical_conditions': recommendation.profile.medical_conditions,
                    'injuries_or_physical_limitation': recommendation.profile.injuries_or_physical_limitation,
                    'exercise_setting': recommendation.profile.exercise_setting,
                    'sleep_pattern': recommendation.profile.sleep_pattern,
                    'stress_level': recommendation.profile.stress_level,
                },
                'recommendation_text': recommendation.recommendation_text,
                'parsed_recommendation': parsed_recommendation,
            }
            
            return Response({
                'status': 'success',
                'data': recommendation_data
            }, status=status.HTTP_200_OK)
            
        except FitnessRecommendation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Fitness recommendation not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Failed to fetch fitness recommendation details',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteFitnessRecommendationAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, recommendation_id):
        try:
            # Get and delete specific recommendation for the user
            recommendation = FitnessRecommendation.objects.get(
                id=recommendation_id,
                user=request.user
            )
            
            recommendation.delete()
            
            return Response({
                'status': 'success',
                'message': 'Fitness recommendation deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except FitnessRecommendation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Fitness recommendation not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Failed to delete fitness recommendation',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)