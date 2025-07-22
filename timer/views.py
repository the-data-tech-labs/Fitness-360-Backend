import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Global dictionary to store timer data
TIMER_STORE = {}

class StartTimerView(APIView):
    def post(self, request):
        duration = request.data.get('duration')
        if not duration:
            return Response({"error": "Duration is required"}, status=status.HTTP_400_BAD_REQUEST)
        start_time = time.time()
        user_id = request.user.id  # Assuming the user is logged in
        TIMER_STORE[user_id] = {"start_time": start_time, "duration": duration, "completed": False}
        return Response({"message": "Timer started", "start_time": start_time, "duration": duration})

class StopTimerView(APIView):
    def post(self, request):
        user_id = request.user.id

        if user_id not in TIMER_STORE:
            return Response({"error": "No active timer found"}, status=status.HTTP_404_NOT_FOUND)

        # Timer stop logic
        timer_data = TIMER_STORE[user_id]
        elapsed_time = time.time() - timer_data["start_time"]

        # Check if the timer has already completed
        if elapsed_time >= timer_data["duration"]:
            timer_data["completed"] = True
            return Response({
                "message": "Timer automatically expired",
                "elapsed_time": elapsed_time,
                "duration": timer_data["duration"]
            }, status=status.HTTP_200_OK)

        # Manually stop the timer
        timer_data["completed"] = True
        del TIMER_STORE[user_id]  # Remove from storage once stopped

        return Response({
            "message": "Timer stopped",
            "elapsed_time": elapsed_time,
            "duration": timer_data["duration"]
        }, status=status.HTTP_200_OK)

class TimerStatusView(APIView):
    def get(self, request):
        user_id = request.user.id

        if user_id not in TIMER_STORE:
            return Response({"error": "No active timer found"}, status=status.HTTP_404_NOT_FOUND)

        timer = TIMER_STORE[user_id]
        if timer["completed"]:
            return Response({"status": "Completed"}, status=status.HTTP_200_OK)

        elapsed_time = time.time() - timer["start_time"]
        remaining_time = max(0, timer["duration"] - elapsed_time)

        return Response({
            "status": "In Progress",
            "remaining_time": remaining_time
        }, status=status.HTTP_200_OK)
