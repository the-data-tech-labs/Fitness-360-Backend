from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
import ast
import json


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with data cleaning"""
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'isAdmin', 'date_joined']

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff
    
    def get_full_name(self, obj):
        first_name = self._clean_field_value(obj.first_name)
        last_name = self._clean_field_value(obj.last_name)
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        return self._clean_field_value(obj.username)

    def _clean_field_value(self, value):
        """Clean field values that are stored as JSON string arrays"""
        if not value:
            return ""
        
        # If it's a string that looks like a Python list
        if isinstance(value, str):
            # Check if it starts and ends with brackets (list format)
            if value.startswith("['") and value.endswith("']"):
                try:
                    # Use ast.literal_eval to safely parse Python literal
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return str(parsed[0]).strip()
                    return ""
                except (ValueError, SyntaxError):
                    # If parsing fails, try JSON
                    try:
                        parsed = json.loads(value.replace("'", '"'))
                        if isinstance(parsed, list) and len(parsed) > 0:
                            return str(parsed[0]).strip()
                        return ""
                    except json.JSONDecodeError:
                        # If both fail, return the original value cleaned
                        return value.strip("[]'\"")
            
            # If it's a JSON array string
            elif value.startswith('["') and value.endswith('"]'):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return str(parsed[0]).strip()
                    return ""
                except json.JSONDecodeError:
                    return value.strip("[]'\"")
            
            # If it's a regular string, return as is
            return value.strip()
        
        # If it's actually a list (shouldn't happen in your case)
        if isinstance(value, list):
            return str(value[0]).strip() if value else ""
        
        # For any other type, convert to string
        return str(value).strip()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Clean all user string fields
        string_fields = ['username', 'email', 'first_name', 'last_name']
        for field in string_fields:
            if field in data:
                original_value = getattr(instance, field, "")
                cleaned_value = self._clean_field_value(original_value)
                data[field] = cleaned_value
                
        return data


class UserSerializerWithToken(UserSerializer):
    """User serializer with JWT token"""
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'isAdmin', 'date_joined', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model with all fields"""
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    bmi = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)  # Include cleaned user data
    
    class Meta:
        model = Profile
        fields = [
            'user',
            'phone', 
            'location', 
            'bio', 
            'profile_picture', 
            'profile_picture_url',
            'gender', 
            'age', 
            'height', 
            'weight', 
            'fitness_goal', 
            'activity_level',
            'profile_completed', 
            'created_at', 
            'updated_at', 
            'full_name', 
            'bmi'
        ]
        read_only_fields = ['created_at', 'updated_at', 'profile_completed']
        
    def get_profile_picture_url(self, obj):
        return obj.get_profile_picture_url()
        
    def get_full_name(self, obj):
        return obj.get_full_name()
        
    def get_bmi(self, obj):
        return obj.calculate_bmi()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Separate serializer for profile updates"""
    
    class Meta:
        model = Profile
        fields = [
            'phone', 
            'location', 
            'bio', 
            'profile_picture',
            'gender', 
            'age', 
            'height', 
            'weight', 
            'fitness_goal', 
            'activity_level'
        ]
        
    def validate_age(self, value):
        if value and (value < 13 or value > 120):
            raise serializers.ValidationError("Age must be between 13 and 120 years.")
        return value
    
    def validate_height(self, value):
        if value and (value < 50 or value > 300):
            raise serializers.ValidationError("Height must be between 50 and 300 cm.")
        return value
    
    def validate_weight(self, value):
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Weight must be between 20 and 500 kg.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user serializer with profile data"""
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'date_joined',
            'profile'
        ]
