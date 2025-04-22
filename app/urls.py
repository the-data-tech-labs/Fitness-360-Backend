from django.urls import path
from app import views
from .views import ForgotPasswordView, ResetPasswordView, ChangePasswordView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('', views.getRoutes, name='getRoutes'),
    path('users/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('users/profile/', views.getUserProfile, name="getUserProfile"),
    # path('users/', views.getUsers, name="getUsers"),
    path('users/register/', views.registerUser, name="register"),
    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate'),
    path('logout/', views.logoutUser, name='logout'),  # Fixed the path
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', views.profile_detail, name='profile-detail'), 
     path('check_profile_completed/', views.check_profile_completed, name='check_profile_completed'), 
]
