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
from .models import UserInput, DietRecommendation
from .serializers import UserInputSerializer, DietRecommendationSerializer
load_dotenv()


    
class DietRecommendationAPI(APIView):
    def calculate_bmi(self, weight, height):
        height_m = height / 100.0
        bmi = weight / (height_m ** 2)
        
        if bmi < 18.5:
            bmi_category = 'Underweight'
        elif 18.5 <= bmi < 24.9:
            bmi_category = 'Normal weight'
        elif 25 <= bmi < 29.9:
            bmi_category = 'Overweight'
        else:
            bmi_category = 'Obesity'
        
        return bmi, bmi_category
    
    def post(self, request):
        try:
            profile_serializer = UserInputSerializer(data=request.data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
                
                # Calculate BMI
                bmi, bmi_category = self.calculate_bmi(
                    float(profile.weight), 
                    float(profile.height)
                )
                
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Enhanced prompt for more relevant responses
                prompt = f"""
                As an expert nutritionist with 15+ years of experience in personalized diet planning, create a comprehensive, evidence-based nutrition plan for the following individual. Focus on practical, culturally appropriate, and scientifically sound recommendations.

                CRITICAL INSTRUCTIONS:
                - Return ONLY a clean JSON object without markdown formatting or code blocks
                - Start response with {{ and end with }}
                - No additional text or explanations outside the JSON
                - Ensure all recommendations are safe, practical, and evidence-based
                - Consider cultural food preferences and local availability
                - Account for any medical conditions and allergies mentioned

                CLIENT PROFILE ANALYSIS:
                Demographics: {profile.age}-year-old {profile.gender}
                Physical Stats: {profile.weight}kg, {profile.height}cm (BMI: {bmi:.1f} - {bmi_category})
                Dietary Style: {profile.food_type}
                Primary Goal: {profile.goal}
                Health Conditions: {profile.disease or 'None reported'}
                Food Allergies/Restrictions: {profile.allergics or 'None reported'}
                Target Timeline: {profile.Target_timeline or '8-12 weeks'}

                {{
                    "client_assessment": {{
                        "current_status": {{
                            "bmi": "{bmi:.1f}",
                            "bmi_category": "{bmi_category}",
                            "health_risk_level": "",
                            "metabolic_rate_estimate": "",
                            "target_weight_range": ""
                        }},
                        "caloric_requirements": {{
                            "bmr_calories": "",
                            "maintenance_calories": "",
                            "goal_adjusted_calories": "",
                            "weekly_deficit_surplus": ""
                        }},
                        "macronutrient_targets": {{
                            "protein": {{
                                "grams_per_day": "",
                                "percentage_of_calories": "",
                                "grams_per_kg_bodyweight": ""
                            }},
                            "carbohydrates": {{
                                "grams_per_day": "",
                                "percentage_of_calories": "",
                                "timing_strategy": ""
                            }},
                            "fats": {{
                                "grams_per_day": "",
                                "percentage_of_calories": "",
                                "quality_focus": ""
                            }},
                            "fiber": {{
                                "daily_target_grams": "",
                                "key_sources": []
                            }}
                        }}
                    }},
                    "personalized_meal_plan": {{
                        "daily_structure": {{
                            "meal_frequency": "",
                            "eating_window": "",
                            "hydration_target": ""
                        }},
                        "sample_day_menu": {{
                            "pre_workout": {{
                                "time": "6:30-7:00 AM",
                                "foods": [],
                                "calories": "",
                                "purpose": "",
                                "preparation_time": ""
                            }},
                            "breakfast": {{
                                "time": "7:30-8:30 AM",
                                "foods": [],
                                "calories": "",
                                "macros": {{"protein": "", "carbs": "", "fats": ""}},
                                "key_nutrients": [],
                                "preparation_time": ""
                            }},
                            "mid_morning": {{
                                "time": "10:30-11:00 AM",
                                "foods": [],
                                "calories": "",
                                "purpose": "",
                                "alternatives": []
                            }},
                            "lunch": {{
                                "time": "12:30-1:30 PM",
                                "foods": [],
                                "calories": "",
                                "macros": {{"protein": "", "carbs": "", "fats": ""}},
                                "portion_guides": [],
                                "preparation_time": ""
                            }},
                            "afternoon_snack": {{
                                "time": "4:00-4:30 PM",
                                "foods": [],
                                "calories": "",
                                "energy_focus": "",
                                "alternatives": []
                            }},
                            "dinner": {{
                                "time": "7:00-8:00 PM",
                                "foods": [],
                                "calories": "",
                                "macros": {{"protein": "", "carbs": "", "fats": ""}},
                                "digestive_considerations": [],
                                "preparation_time": ""
                            }},
                            "post_dinner": {{
                                "time": "9:30-10:00 PM",
                                "foods": [],
                                "calories": "",
                                "sleep_optimization": "",
                                "optional": true
                            }}
                        }}
                    }},
                    "food_recommendations": {{
                        "power_foods": [
                            {{
                                "food_item": "",
                                "nutritional_benefits": [],
                                "recommended_portion": "",
                                "best_consumption_time": "",
                                "preparation_tips": []
                            }}
                        ],
                        "foods_to_minimize": [
                            {{
                                "food_item": "",
                                "reason_to_avoid": "",
                                "healthy_substitutes": [],
                                "transition_strategy": ""
                            }}
                        ],
                        "allergy_safe_alternatives": [
                            {{
                                "allergen": "",
                                "safe_substitutes": [],
                                "nutritional_equivalence": ""
                            }}
                        ]
                    }},
                    "meal_preparation_strategy": {{
                        "weekly_prep_schedule": [
                            {{
                                "day": "",
                                "prep_tasks": [],
                                "time_required": "",
                                "storage_tips": []
                            }}
                        ],
                        "kitchen_essentials": [
                            {{
                                "category": "",
                                "items": [],
                                "budget_estimate": ""
                            }}
                        ],
                        "quick_meal_solutions": [
                            {{
                                "meal_type": "",
                                "prep_time": "",
                                "ingredients": [],
                                "instructions": []
                            }}
                        ]
                    }},
                    "supplementation_guidance": {{
                        "essential_supplements": [
                            {{
                                "supplement": "",
                                "dosage": "",
                                "timing": "",
                                "reason": "",
                                "food_sources_alternative": []
                            }}
                        ],
                        "conditional_supplements": [
                            {{
                                "supplement": "",
                                "condition": "",
                                "consultation_needed": true,
                                "natural_alternatives": []
                            }}
                        ]
                    }},
                    "progress_tracking": {{
                        "weekly_milestones": [
                            {{
                                "week": 1,
                                "weight_target": "",
                                "energy_expectations": "",
                                "behavioral_goals": [],
                                "measurements_to_track": []
                            }},
                            {{
                                "week": 4,
                                "weight_target": "",
                                "habit_consolidation": [],
                                "potential_challenges": [],
                                "adjustment_strategies": []
                            }},
                            {{
                                "week": 8,
                                "expected_progress": "",
                                "lifestyle_integration": [],
                                "long_term_maintenance": []
                            }}
                        ],
                        "success_indicators": {{
                            "physical_markers": [],
                            "energy_improvements": [],
                            "digestive_health": [],
                            "mood_and_mental_clarity": []
                        }}
                    }},
                    "lifestyle_integration": {{
                        "dining_out_strategies": [
                            {{
                                "restaurant_type": "",
                                "ordering_tips": [],
                                "portion_control": []
                            }}
                        ],
                        "travel_nutrition": [
                            {{
                                "travel_type": "",
                                "portable_foods": [],
                                "hydration_strategy": "",
                                "timezone_adjustment": []
                            }}
                        ],
                        "social_eating": [
                            {{
                                "situation": "",
                                "strategies": [],
                                "mindset_tips": []
                            }}
                        ],
                        "budget_optimization": [
                            {{
                                "money_saving_tip": "",
                                "bulk_buying_guide": [],
                                "seasonal_substitutions": [],
                                "estimated_weekly_cost": ""
                            }}
                        ]
                    }},
                    "emergency_protocols": {{
                        "plateau_breakers": [
                            {{
                                "strategy": "",
                                "implementation": "",
                                "duration": "",
                                "expected_outcome": ""
                            }}
                        ],
                        "crisis_management": [
                            {{
                                "scenario": "",
                                "immediate_actions": [],
                                "recovery_plan": [],
                                "prevention_strategy": []
                            }}
                        ]
                    }},
                    "professional_recommendations": {{
                        "follow_up_schedule": "",
                        "specialist_referrals": [],
                        "lab_tests_to_consider": [],
                        "red_flag_symptoms": []
                    }}
                }}

                Generate a nutrition plan that is specifically tailored to help this individual achieve their {profile.goal} goal while considering their {profile.food_type} dietary preference, {bmi_category} BMI status, and any health conditions or allergies mentioned. Focus on sustainable, enjoyable, and culturally appropriate food choices that fit their lifestyle and timeline of {profile.Target_timeline or '8-12 weeks'}.
                """
                
                # Generate response
                response = model.generate_content(prompt)
                
                try:
                    # Clean the response text
                    cleaned_response = response.text.strip()
                    
                    # Remove markdown formatting
                    if cleaned_response.startswith('```json'):
                        cleaned_response = cleaned_response[7:].strip()
                    elif cleaned_response.startswith('```'):
                        cleaned_response = cleaned_response[3:].strip()
                    
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response[:-3].strip()
                    
                    # Parse as JSON
                    recommendation_json = json.loads(cleaned_response)
                    
                    # Save recommendation
                    recommendation = DietRecommendation.objects.create(
                        user=request.user,
                        profile=profile,
                        recommendation_text=json.dumps(recommendation_json, indent=2),  
                        bmi=bmi,
                        bmi_category=bmi_category
                    )
                    
                    return Response({
                        'status': 'success',
                        'data': {
                            'profile': profile_serializer.data,
                            'bmi': round(bmi, 1),
                            'bmi_category': bmi_category,
                            'recommendation': recommendation_json,
                            'recommendation_id': recommendation.id
                        }
                    }, status=status.HTTP_201_CREATED)
                    
                except json.JSONDecodeError as e:
                    # Enhanced error handling
                    return Response({
                        'status': 'error',
                        'message': 'Failed to parse AI response as valid JSON',
                        'error_details': str(e),
                        'debug_info': {
                            'response_length': len(cleaned_response),
                            'starts_with': cleaned_response[:50] if cleaned_response else 'Empty response',
                            'ends_with': cleaned_response[-50:] if len(cleaned_response) > 50 else cleaned_response
                        }
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'status': 'error',
                'message': 'Invalid input data',
                'errors': profile_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Internal server error',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NutritionRecommendationListAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            filter_by = request.GET.get('filter', 'all')
            
            # Base queryset - only user's recommendations
            queryset = DietRecommendation.objects.filter(
                user=request.user
            ).select_related('user', 'profile').order_by('-created_at')
            
            # Apply search filter if provided
            if search:
                queryset = queryset.filter(
                    Q(profile__goal__icontains=search) |
                    Q(bmi_category__icontains=search) |
                    Q(profile__food_type__icontains=search) |
                    Q(profile__veg_or_nonveg__icontains=search)
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
                            'goal': recommendation.profile.goal,
                            'food_type': recommendation.profile.food_type,
                            'veg_or_nonveg': recommendation.profile.veg_or_nonveg,
                            'allergics': recommendation.profile.allergics,
                            'disease': recommendation.profile.disease,
                            'Target_timeline': recommendation.profile.Target_timeline,
                            'country': recommendation.profile.country,
                            'state': recommendation.profile.state,
                        },
                        'recommendation_summary': self.get_recommendation_summary(parsed_recommendation),
                        'recommendation_text': recommendation.recommendation_text,
                        'parsed_recommendation': parsed_recommendation,
                        'has_meal_plan': bool(parsed_recommendation and parsed_recommendation.get('personalized_meal_plan')),
                        'calorie_target': self.get_calorie_target(parsed_recommendation),
                        'meal_count': self.get_meal_count(parsed_recommendation),
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
                'message': 'Failed to fetch nutrition recommendations',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_recommendation_summary(self, parsed_recommendation):
        """Extract key summary information from the recommendation"""
        if not parsed_recommendation:
            return None
        
        summary = {}
        
        # Extract caloric requirements
        if 'client_assessment' in parsed_recommendation:
            assessment = parsed_recommendation['client_assessment']
            if 'caloric_requirements' in assessment:
                cal_req = assessment['caloric_requirements']
                summary.update({
                    'daily_calories': cal_req.get('goal_adjusted_calories', 'N/A'),
                    'bmr_calories': cal_req.get('bmr_calories', 'N/A'),
                })
        
        # Count meals
        meal_count = 0
        if 'personalized_meal_plan' in parsed_recommendation:
            meal_plan = parsed_recommendation['personalized_meal_plan']
            if 'sample_day_menu' in meal_plan:
                meal_count = len(meal_plan['sample_day_menu'])
        
        summary['total_meals'] = meal_count
        
        # Extract macros
        if 'client_assessment' in parsed_recommendation:
            macros = parsed_recommendation['client_assessment'].get('macronutrient_targets', {})
            summary['macros'] = {
                'protein': macros.get('protein', {}).get('grams_per_day', 'N/A'),
                'carbs': macros.get('carbohydrates', {}).get('grams_per_day', 'N/A'),
                'fats': macros.get('fats', {}).get('grams_per_day', 'N/A'),
            }
        
        return summary
    
    def get_calorie_target(self, parsed_recommendation):
        """Get daily calorie target from recommendation"""
        if not parsed_recommendation:
            return None
        
        if 'client_assessment' in parsed_recommendation:
            cal_req = parsed_recommendation['client_assessment'].get('caloric_requirements', {})
            return cal_req.get('goal_adjusted_calories')
        
        return None
    
    def get_meal_count(self, parsed_recommendation):
        """Get number of meals from recommendation"""
        if not parsed_recommendation:
            return 0
        
        if 'personalized_meal_plan' in parsed_recommendation:
            meal_plan = parsed_recommendation['personalized_meal_plan']
            if 'sample_day_menu' in meal_plan:
                return len(meal_plan['sample_day_menu'])
        
        return 0
    
    def get_user_stats(self, user):
        """Get user nutrition statistics"""
        try:
            recommendations = DietRecommendation.objects.filter(user=user)
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


class NutritionRecommendationDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, recommendation_id):
        try:
            # Get specific recommendation for the user
            recommendation = DietRecommendation.objects.get(
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
                    'goal': recommendation.profile.goal,
                    'food_type': recommendation.profile.food_type,
                    'veg_or_nonveg': recommendation.profile.veg_or_nonveg,
                    'allergics': recommendation.profile.allergics,
                    'disease': recommendation.profile.disease,
                    'Target_timeline': recommendation.profile.Target_timeline,
                    'country': recommendation.profile.country,
                    'state': recommendation.profile.state,
                },
                'recommendation_text': recommendation.recommendation_text,
                'parsed_recommendation': parsed_recommendation,
            }
            
            return Response({
                'status': 'success',
                'data': recommendation_data
            }, status=status.HTTP_200_OK)
            
        except DietRecommendation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Nutrition recommendation not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Failed to fetch nutrition recommendation details',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteNutritionRecommendationAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, recommendation_id):
        try:
            # Get and delete specific recommendation for the user
            recommendation = DietRecommendation.objects.get(
                id=recommendation_id,
                user=request.user
            )
            
            recommendation.delete()
            
            return Response({
                'status': 'success',
                'message': 'Nutrition recommendation deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except DietRecommendation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Nutrition recommendation not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Failed to delete nutrition recommendation',
                'error_details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)