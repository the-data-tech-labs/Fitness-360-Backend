from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializer import UserSerializer, UserSerializerWithToken, ProfileSerializer, ProfileUpdateSerializer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Profile
from rest_framework.decorators import api_view, permission_classes
import logging
from django.conf import settings
import re
import json
import ast


def getRoutes(request):
    """API routes endpoint"""
    return JsonResponse("Hi, welcome to the API", safe=False)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer"""
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        for key, value in serializer.items():
            data[key] = value
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view"""
    serializer_class = MyTokenObtainPairSerializer



@api_view(['POST'])
def registerUser(request):
    """User registration endpoint"""
    data = request.data
    
    try:
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        

        if not all([username, email, password, confirm_password]):
            return Response({
                'success': False,
                'message': "All fields are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        

    
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                'success': False,
                'message': "Please enter a valid email address."
            }, status=status.HTTP_400_BAD_REQUEST)
        
       
        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': "Username already exists. Please choose a different username."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': "Email already exists. Please use a different email address."
            }, status=status.HTTP_400_BAD_REQUEST)
        
       
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=True
        )
        

        Profile.objects.create(user=user)
        
        # Serialize user data with token
        serializer = UserSerializerWithToken(user, many=False)
        
        return Response({
            'success': True,
            'message': "Account created successfully!",
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError as ve:
        return Response({
            'success': False,
            'message': str(ve)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': "An error occurred while creating your account. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from django.contrib.auth import authenticate

@api_view(['POST'])
def loginUser(request):
    """User login endpoint"""
    try:
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        # Check if both fields are provided
        if not username or not password:
            return Response({
                'success': False,
                'message': "Username and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            serializer = UserSerializerWithToken(user)
            return Response({
                'success': True,
                'message': "Login successful",
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': "Invalid username or password. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': "An error occurred during login. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logoutUser(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({
                'success': False,
                'message': "Refresh token is required for logout."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'success': True,
            'message': "Logged out successfully."
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': "An error occurred during logout. Please try again."
        }, status=status.HTTP_400_BAD_REQUEST)






logger = logging.getLogger(__name__)

def clean_user_field_value(value):
    """Helper function to clean user field values"""
    if not value:
        return ""
    
    if isinstance(value, str):
        if value.startswith("['") and value.endswith("']"):
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return str(parsed[0]).strip()
                return ""
            except (ValueError, SyntaxError):
                try:
                    parsed = json.loads(value.replace("'", '"'))
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return str(parsed[0]).strip()
                    return ""
                except json.JSONDecodeError:
                    return value.strip("[]'\"")
        elif value.startswith('["') and value.endswith('"]'):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return str(parsed[0]).strip()
                return ""
            except json.JSONDecodeError:
                return value.strip("[]'\"")
        return value.strip()
    
    if isinstance(value, list):
        return str(value[0]).strip() if value else ""
    
    return str(value).strip()


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_detail(request):
    """User profile endpoint for viewing and updating profile"""
    try:
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response({
                'success': True,
                'message': "Profile retrieved successfully.",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        elif request.method == 'PUT':
            # Handle user fields update with proper cleaning
            user_fields = ['first_name', 'last_name', 'email']
            user_updated = False
            
            for field in user_fields:
                if field in request.data:
                    value = request.data[field]
                    
                    # Clean the incoming value
                    if isinstance(value, list):
                        clean_value = str(value[0]).strip() if value else ""
                    elif isinstance(value, str):
                        clean_value = value.strip()
                    else:
                        clean_value = str(value).strip()
                    
                    # Only update if value is different
                    current_value = clean_user_field_value(getattr(request.user, field, ""))
                    if current_value != clean_value:
                        setattr(request.user, field, clean_value)
                        user_updated = True
            
            if user_updated:
                request.user.save()
            
            # Handle profile fields
            profile_data = {k: v for k, v in request.data.items() if k not in user_fields}
            serializer = ProfileUpdateSerializer(profile, data=profile_data, partial=True)
            
            if serializer.is_valid():
                # Check if profile is complete
                required_fields = ['gender', 'age', 'height', 'weight']
                profile_complete = all(
                    getattr(profile, field) or profile_data.get(field) 
                    for field in required_fields
                )
                
                serializer.save(profile_completed=profile_complete)
                
                # Return fresh data with cleaned serializer
                response_serializer = ProfileSerializer(profile)
                return Response({
                    'success': True,
                    'message': "Profile updated successfully.",
                    'data': response_serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': "Please correct the errors below.",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Profile detail error for user {request.user.id}: {str(e)}")
        return Response({
            'success': False,
            'message': "An error occurred while processing your profile. Please try again.",
            'error_detail': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_profile_completed(request):
    """Check if user profile is completed"""
    try:
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        required_fields = ['gender', 'age', 'height', 'weight']
        missing_fields = []
        
        for field in required_fields:
            if not getattr(profile, field):
                missing_fields.append(field)
        
        is_complete = len(missing_fields) == 0 and profile.profile_completed
        completion_percentage = ((len(required_fields) - len(missing_fields)) / len(required_fields)) * 100
        
        return Response({
            'success': True,
            'data': {
                'profile_completed': is_complete,
                'completion_percentage': round(completion_percentage, 1),
                'missing_fields': missing_fields,
                'required_fields': required_fields
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile completion check error for user {request.user.id}: {str(e)}")
        return Response({
            'success': False,
            'message': "An error occurred while checking profile status.",
            'error_detail': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'success': False,
                'message': "Both current and new passwords are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check current password
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'message': "Current password is incorrect."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password length
        if len(new_password) < 8:
            return Response({
                'success': False,
                'message': "New password must be at least 8 characters long."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'success': True,
            'message': "Password changed successfully."
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Password change error for user {request.user.id}: {str(e)}")
        return Response({
            'success': False,
            'message': "An error occurred while changing password. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete user account"""
    try:
        password = request.data.get('password')
        
        if not password:
            return Response({
                'success': False,
                'message': "Password confirmation is required to delete account."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not request.user.check_password(password):
            return Response({
                'success': False,
                'message': "Password is incorrect."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete user (this will also delete the profile due to CASCADE)
        username = request.user.username
        request.user.delete()
        
        return Response({
            'success': True,
            'message': f"Account for {username} has been permanently deleted."
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Account deletion error for user {request.user.id}: {str(e)}")
        return Response({
            'success': False,
            'message': "An error occurred while deleting account. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
