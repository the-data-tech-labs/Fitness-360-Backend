# highlights/utils.py

import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_highlights(text):
    prompt = f"""
    Extract fitness and nutrition data from the given text and return TWO separate JSON objects.

    Text: {text}

    Return exactly this format:

    FITNESS_DATA:
    {{
        "weekly_schedule": {{
            "monday": 45,
            "tuesday": 0,
            "wednesday": 50,
            "thursday": 0,
            "friday": 45,
            "saturday": 30,
            "sunday": 0
        }},
        "exercise_breakdown": {{
            "push_exercises": 4,
            "pull_exercises": 4,
            "cardio_minutes": 20,
            "rest_days": 4
        }}
    }}

    NUTRITION_DATA:
    {{
        "daily_targets": {{
            "total_calories": 2800,
            "protein_grams": 150,
            "carbs_grams": 350,
            "fats_grams": 90,
            "fiber_grams": 35,
            "water_liters": 3.5
        }},
        "macro_percentages": {{
            "protein": 21,
            "carbs": 50,
            "fats": 29
        }},
        "meal_calories": {{
            "early_morning": 50,
            "breakfast": 650,
            "mid_morning": 200,
            "lunch": 800,
            "evening_snack": 300,
            "dinner": 700
        }},
        "weekly_targets": {{
            "week_1": 0.3,
            "week_4": 1.2,
            "week_8": 2.4,
            "week_12": 4.0
        }}
    }}

    Extract actual values from the text. If not found, use realistic values.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Could not extract fitness and nutrition highlights."
