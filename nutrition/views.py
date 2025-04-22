
# {
#   "age": 25,
#   "gender": "Male",
#   "weight": 70,
#   "height": 175,
#   "veg_or_nonveg": "Veg",
#   "goal": "Gain muscles",
#   "disease": "",
#   "country": "India",
#   "state": "Maharashtra",
#   "allergics": "",
#   "food_type": "Veg",
#   "Target_timeline": "3 months"
# }


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserInputSerializer, DietRecommendationSerializer
from .models import UserInput, DietRecommendation
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

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
                
                # Configure Gemini
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                # Modify the prompt to explicitly request raw JSON without markdown
                prompt = f"""
                You are an expert nutritionist specializing in personalized diet planning. Create a detailed, culturally-appropriate diet plan based on the following profile. 
                IMPORTANT: Return ONLY a raw JSON object without any markdown formatting, code blocks, or additional text.
                Do NOT wrap the response in ```json or ``` tags.
                Start your response with {{ and end with }}.

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

                {{
                    "nutritional_analysis": {{
                        "current_status": {{
                            "bmi_data": {{
                                "current_bmi": "",
                                "healthy_weight_range": ""
                            }},
                            "daily_calories": {{
                                "base_requirement": "",
                                "adjusted_for_goal": ""
                            }},
                            "macro_distribution": {{
                                "protein": {{
                                    "grams": "",
                                    "percentage": ""
                                }},
                                "carbs": {{
                                    "grams": "",
                                    "percentage": ""
                                }},
                                "fats": {{
                                    "grams": "",
                                    "percentage": ""
                                }}
                            }},
                            "micronutrient_focus": []
                        }},
                        "goal_adjustments": {{
                            "dietary_considerations": [],
                            "allergy_alternatives": []
                        }}
                    }},
                    "meal_plan": {{
                        "daily_targets": {{
                            "total_calories": "",
                            "protein_grams": "",
                            "carbs_grams": "",
                            "fats_grams": "",
                            "fiber_grams": "",
                            "water_liters": ""
                        }},
                        "meal_schedule": {{
                            "early_morning": {{
                                "time": "6-7 AM",
                                "items": [],
                                "total_calories": "",
                                "macros": {{
                                    "protein": "",
                                    "carbs": "",
                                    "fats": ""
                                }}
                            }},
                            "breakfast": {{
                                "time": "8-9 AM",
                                "items": [],
                                "total_calories": "",
                                "macros": {{
                                    "protein": "",
                                    "carbs": "",
                                    "fats": ""
                                }}
                            }},
                            "mid_morning": {{
                                "time": "11 AM",
                                "items": [],
                                "total_calories": "",
                                "macros": {{
                                    "protein": "",
                                    "carbs": "",
                                    "fats": ""
                                }}
                            }},
                            "lunch": {{
                                "time": "1-2 PM",
                                "items": [],
                                "total_calories": "",
                                "macros": {{
                                    "protein": "",
                                    "carbs": "",
                                    "fats": ""
                                }}
                            }},
                            "evening_snack": {{
                                "time": "4-5 PM",
                                "items": [],
                                "total_calories": "",
                                "macros": {{
                                    "protein": "",
                                    "carbs": "",
                                    "fats": ""
                                }}
                            }},
                            "dinner": {{
                                "time": "7-8 PM",
                                "items": [],
                                "total_calories": "",
                                "macros": {{
                                    "protein": "",
                                    "carbs": "",
                                    "fats": ""
                                }}
                            }}
                        }}
                    }},
                    "food_recommendations": {{
                        "essential_foods": [
                            {{
                                "food": "",
                                "benefits": [],
                                "portion": "",
                                "best_time": ""
                            }}
                        ],
                        "foods_to_avoid": [
                            {{
                                "food": "",
                                "reason": "",
                                "alternatives": []
                            }}
                        ]
                    }},
                    "preparation_guidelines": {{
                        "cooking_methods": [
                            {{
                                "method": "",
                                "benefits": [],
                                "tips": []
                            }}
                        ],
                        "portion_control": {{
                            "visual_guides": [],
                            "measuring_techniques": [],
                            "activity_adjustments": []
                        }}
                    }},
                    "hydration_and_supplements": {{
                        "hydration": {{
                            "daily_intake_goal": "",
                            "schedule": [],
                            "tips": []
                        }},
                        "supplements": [
                            {{
                                "name": "",
                                "dosage": "",
                                "timing": "",
                                "natural_alternatives": []
                            }}
                        ]
                    }},
                    "progress_monitoring": {{
                        "weekly_milestones": [
                            {{
                                "week": "",
                                "expected_progress": "",
                                "measurements": []
                            }}
                        ],
                        "success_indicators": {{
                            "physical": [],
                            "energy": [],
                            "digestive": []
                        }}
                    }},
                    "special_instructions": {{
                        "local_alternatives": [],
                        "seasonal_options": [],
                        "budget_friendly_tips": [],
                        "quick_meal_ideas": [],
                        "emergency_food_options": [],
                        "meal_prep_shortcuts": []
                    }}
                }}
                """
                
                # Generate response
                response = model.generate_content(prompt)
                
                try:
                    # Clean the response text - remove any potential markdown formatting
                    cleaned_response = response.text.strip()
                    if cleaned_response.startswith('```json'):
                        cleaned_response = cleaned_response.replace('```json', '', 1)
                    if cleaned_response.startswith('```'):
                        cleaned_response = cleaned_response.replace('```', '', 1)
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response[:-3]
                    cleaned_response = cleaned_response.strip()
                    
                    # Parse the cleaned response as JSON
                    recommendation_json = json.loads(cleaned_response)
                    
                    # Save recommendation
                    recommendation = DietRecommendation.objects.create(
                        profile=profile,
                        recommendation_text=json.dumps(recommendation_json),  
                        bmi=bmi,
                        bmi_category=bmi_category
                    )
                    
                    return Response({
                        'status': 'success',
                        'data': {
                            'profile': profile_serializer.data,
                            'bmi': bmi,
                            'bmi_category': bmi_category,
                            'recommendation': recommendation_json   
                        }
                    }, status=status.HTTP_201_CREATED)
                    
                except json.JSONDecodeError as e:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to parse AI response as JSON',
                        'error': str(e),
                        'raw_response': cleaned_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)