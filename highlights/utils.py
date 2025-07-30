# highlights/utils.py

import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_highlights(text):
    prompt = f"""
    Extract two separate bullet point summaries from the following fitness plan text:

    1. Fitness Highlights – key exercises, warm-up, cool-down, workout structure, recovery.
    2. Nutrition Highlights – meal planning, hydration, nutrition advice.

    Return only the summaries in clear bullet point format.

    Text:
    {text}
    """

    try:
        response = model.generate_content(prompt)
        full_text = response.text or ""
        # Split manually for now
        parts = full_text.split("Nutrition Highlights:")
        fitness_summary = parts[0].replace("Fitness Highlights:", "").strip()
        nutrition_summary = parts[1].strip() if len(parts) > 1 else ""
        return fitness_summary, nutrition_summary
    except Exception as e:
        return "Could not extract fitness highlights.", "Could not extract nutrition highlights."
