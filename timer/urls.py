from django.urls import path
from timer.views import StartTimerView, StopTimerView, TimerStatusView

urlpatterns = [
    path('start/', StartTimerView.as_view(), name='start_timer'),
    path('stop/', StopTimerView.as_view(), name='stop_timer'),
    path('status/', TimerStatusView.as_view(), name='timer_status'),
]
