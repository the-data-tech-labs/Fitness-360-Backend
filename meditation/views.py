from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import DailyExperience, MeditationRecommendation
from .serializers import DailyExperienceSerializer, ExperienceWithRecommendationsSerializer, MeditationRecommendationSerializer
import google.generativeai as genai
from django.conf import settings
import json
import re

class DailyExperienceViewSet(viewsets.ModelViewSet):
    queryset = DailyExperience.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DailyExperienceSerializer
        return ExperienceWithRecommendationsSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experience = serializer.save()
        
        # Generate recommendations
        self.generate_meditation_recommendations(experience)
        
        # Return the complete experience with recommendations
        result_serializer = ExperienceWithRecommendationsSerializer(experience)
        headers = self.get_success_headers(serializer.data)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def generate_meditation_recommendations(self, experience):
        # Using Gemini to generate meditation recommendations based on the experience
        try:
            print(f"Generating recommendations for experience ID: {experience.id}")
            # Configure the Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize the model
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = f"""
            Based on the following daily experience, recommend THREE different types of meditation practices:
            
            Experience: {experience.experience_text}
            
            Provide your response in the following JSON format:
            {{
                "recommendations": [
                    {{
                        "meditation_type": "Name of first meditation technique",
                        "duration_minutes": duration in minutes (integer between 5 and 30),
                        "how_to_perform": "Detailed step-by-step instructions on how to perform this meditation",
                        "benefits": "Specific benefits of this meditation practice for the person's situation"
                    }},
                    {{
                        "meditation_type": "Name of second meditation technique",
                        "duration_minutes": duration in minutes (integer between 5 and 30),
                        "how_to_perform": "Detailed step-by-step instructions on how to perform this meditation",
                        "benefits": "Specific benefits of this meditation practice for the person's situation"
                    }},
                    {{
                        "meditation_type": "Name of third meditation technique",
                        "duration_minutes": duration in minutes (integer between 5 and 30),
                        "how_to_perform": "Detailed step-by-step instructions on how to perform this meditation",
                        "benefits": "Specific benefits of this meditation practice for the person's situation"
                    }}
                ]
            }}
            
            Your response MUST be valid, parseable JSON. Do not include any explanations, markdown formatting, or code blocks.
            """
            
            response = model.generate_content(prompt)
            
            # Extract the text from the response
            response_text = response.text
            print(f"Raw AI response: {response_text[:200]}...")  # Print start of response for debugging
            
            # Clean up the response if it has code blocks or markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Try to parse the JSON response
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                # Try to extract JSON if it's wrapped in code blocks or has other text
                json_match = re.search(r'({.*})', response_text.replace('\n', ''))
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        raise Exception(f"Could not parse JSON response: {str(e)}")
                else:
                    raise Exception(f"Could not parse JSON response: {str(e)}")
            
            # Check if the recommendations field exists
            if 'recommendations' not in data or not isinstance(data['recommendations'], list):
                print("Missing recommendations array in response")
                raise Exception("Invalid response format: missing recommendations array")
            
            # Ensure we have at least 3 recommendations
            recommendations = data['recommendations']
            if len(recommendations) < 3:
                print(f"Expected 3 recommendations, but got {len(recommendations)}")
                raise Exception(f"Expected 3 recommendations, but got {len(recommendations)}")
            
            # Create recommendation objects
            print(f"Creating {len(recommendations[:3])} recommendation objects")
            for rec in recommendations[:3]:  # Only use the first 3 recommendations
                # Validate required fields
                if not all(k in rec for k in ('meditation_type', 'duration_minutes', 'how_to_perform', 'benefits')):
                    print(f"Skipping recommendation due to missing fields: {rec.keys()}")
                    continue  # Skip invalid recommendations
                
                meditation_rec = MeditationRecommendation.objects.create(
                    experience=experience,
                    meditation_type=rec.get('meditation_type'),
                    duration_minutes=int(rec.get('duration_minutes')),
                    how_to_perform=rec.get('how_to_perform'),
                    benefits=rec.get('benefits', '')
                )
                print(f"Created recommendation: {meditation_rec.id} - {meditation_rec.meditation_type}")
        
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            # If AI processing fails, create default recommendations
            default_recommendations = [
                {
                    "meditation_type": "Mindful Breathing",
                    "duration_minutes": 10,
                    "how_to_perform": "1. Find a quiet place where you won't be disturbed. 2. Sit in a comfortable position with your spine straight. 3. Close your eyes or maintain a soft gaze. 4. Focus your attention on your breath, noticing the sensation of air entering and leaving your nostrils. 5. When your mind wanders to thoughts about work or deadlines, gently acknowledge them and return your focus to your breath. 6. Continue for 10 minutes.",
                    "benefits": "This practice will help calm your nervous system, reduce stress hormones, and create mental space away from work pressures."
                },
                {
                    "meditation_type": "Body Scan Relaxation",
                    "duration_minutes": 15,
                    "how_to_perform": "1. Lie down or sit comfortably. 2. Close your eyes and take a few deep breaths. 3. Begin at your feet and slowly move your attention up through your body. 4. Notice any areas of tension and consciously relax them. 5. Pay special attention to your shoulders, neck, and forehead where stress often accumulates. 6. Visualize the tension melting away with each exhale.",
                    "benefits": "This technique helps release physical tension that builds up during stressful work situations and improves your ability to notice stress signals earlier."
                },
                {
                    "meditation_type": "Focus Enhancement Meditation",
                    "duration_minutes": 8,
                    "how_to_perform": "1. Sit comfortably with a straight spine. 2. Place a small object (like a stone or paperclip) on the table in front of you. 3. Focus your complete attention on this object. 4. Examine its color, texture, shape, and other qualities. 5. When your mind wanders, gently bring it back to the object. 6. Practice this focused attention for 8 minutes.",
                    "benefits": "This practice strengthens your concentration muscles, making it easier to maintain focus during work tasks and approaching deadlines."
                }
            ]
            
            print("Using default recommendations due to error")
            for rec in default_recommendations:
                meditation_rec = MeditationRecommendation.objects.create(
                    experience=experience,
                    meditation_type=rec["meditation_type"],
                    duration_minutes=rec["duration_minutes"],
                    how_to_perform=rec["how_to_perform"],
                    benefits=rec["benefits"]
                )
                print(f"Created default recommendation: {meditation_rec.id} - {meditation_rec.meditation_type}")