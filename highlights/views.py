# highlights/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Highlight
from .serializers import HighlightSerializer
from .utils import extract_highlights
from fitness.models import FitnessRecommendation
from nutrition.models import DietRecommendation


class GenerateHighlightsAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # ✅ FitnessRecommendation has direct user field
        try:
            fitness_rec = FitnessRecommendation.objects.filter(user=user).latest('created_at')
        except FitnessRecommendation.DoesNotExist:
            return Response({"error": "Fitness recommendation not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ DietRecommendation is linked through profile → user
        try:
            nutrition_rec = DietRecommendation.objects.filter(user=user).latest('created_at')
        except DietRecommendation.DoesNotExist:
            return Response({"error": "Nutrition recommendation not found."}, status=status.HTTP_404_NOT_FOUND)

        # Combine text
        combined_text = f"""
        FITNESS RECOMMENDATION:
        {fitness_rec.recommendation_text}

        NUTRITION RECOMMENDATION:
        {nutrition_rec.recommendation_text}
        """

        # Extract highlights using Gemini or fallback logic
        fitness_highlights, nutrition_highlights = extract_highlights(combined_text)

        # Save highlights
        highlight = Highlight.objects.create(
            user=user,
            fitness_highlights=fitness_highlights,
            nutrition_highlights=nutrition_highlights
        )

        serializer = HighlightSerializer(highlight)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
