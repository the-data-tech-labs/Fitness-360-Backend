from django.urls import path
from app import views
from .views import loginUser, registerUser, logoutUser, profile_detail, check_profile_completed, change_password, delete_account
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('', views.getRoutes, name='getRoutes'),
    path('users/login/', views.loginUser, name='login'),
    path('users/register/', views.registerUser, name="register"),
    path('logout/', views.logoutUser, name='logout'), 
    path('profile/', views.profile_detail, name='profile-detail'), 
    path('check_profile_completed/', views.check_profile_completed, name='check_profile_completed'), 
     path('change-password/', change_password, name='change_password'),
    path('delete-account/', delete_account, name='delete_account'),
]
