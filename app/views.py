from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from .serializer import Userserializer, UserserializerWithToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
 
# for sending mails and generate token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .serializer import ProfileSerializer
from django.shortcuts import get_object_or_404
from .models import Profile
from django.contrib.auth.tokens import default_token_generator

# View for returning basic routes
def getRoutes(request):
    return JsonResponse("Hi, welcome to the API", safe=False)


# Custom Token Serializer
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserserializerWithToken(self.user).data
        for key, value in serializer.items():
            data[key] = value
        return data


# Custom Token View
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# # User Profile View
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getUserProfile(request):
#     user = request.user
#     serializer = Userserializer(user, many=False)
#     return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def getUsers(request):
#     users=User.objects.all()
#     serializer=Userserializer(users,many=True)
#     return Response(serializer.data)

import re
from django.core.exceptions import ValidationError

def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Password must contain at least one special character.")

def validate_username(username):
    if len(username) < 4 or len(username) > 20:
        raise ValidationError("Username must be between 4 and 20 characters.")
    if not re.match(r"^[A-Za-z0-9_-]+$", username):
        raise ValidationError("Username can only contain letters, digits, underscores, and hyphens.")
    if not any(char.isupper() for char in username):
        raise ValidationError("Username must contain at least one uppercase letter.")

# Custom Token View
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        # Validate username and password
        validate_username(data['username'])
        validate_password(data['password'])

        # Check if password and confirm password match
        if data['password'] != data.get('confirm_password', ''):
            return Response({'details': "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(data['email'])
        except ValidationError:
            return Response({'details': "Enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username or email already exists
        if User.objects.filter(username=data['username']).exists():
            return Response({'details': "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data['email']).exists():
            return Response({'details': "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user with `is_active` set to False
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            is_active=False
        )

        # Create a profile for the user
        Profile.objects.create(user=user)

        # Generate the activation email content
        email_subject = "Activate Your Account"
        message = render_to_string(
            "activate.html",
            {
                'user': user,
                'domain': '127.0.0.1:8000',  # Replace with your domain in production
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            }
        )

        # Send the activation email
        try:
            email_message = EmailMessage(
                subject=email_subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to=[data['email']]
            )
            email_message.content_subtype = "html"  # Ensure the email is sent as HTML
            email_message.send()
        except Exception as mail_error:
            print(f"Mail Error: {mail_error}")
            return Response({'details': "Failed to send activation email. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize and return user data
        serializer = UserserializerWithToken(user, many=False)
        return Response(serializer.data)

    except ValidationError as ve:
        return Response({'details': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error: {e}")
        return Response({'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    
from django.shortcuts import render, redirect

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the user ID from the activation link
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Validate the token
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, "activatesuccess.html")  # Successful activation template
        else:
            return render(request, "activatefail.html")  # Failed activation template


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def logoutUser(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
    except KeyError:
        return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Reset password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.contrib.auth.hashers import make_password


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Corrected variable name and URL format
            reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"
            
            # Send email with the correct variable (reset_url instead of reset_link)
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email="360degree_fitness@gmail.com",  # Fixed typo in email
                recipient_list=[email],
            )
            return Response({"message": "Password reset link sent to email"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get('new_password')
            if not new_password:
                return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the new password
            try:
                validate_password(new_password)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, ValueError):
            return Response({"error": "Invalid token or user"}, status=status.HTTP_400_BAD_REQUEST)
class ChangePasswordView(APIView):
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile
from .serializer import ProfileSerializer

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_detail(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    elif request.method == 'PUT':
        print("Received data:", request.data)  # Log the incoming data
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(profile_completed=True)  # Set profile_completed to True
            return Response(serializer.data)
        print("Validation errors:", serializer.errors)  # Log validation errors
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_profile_completed(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return Response({"profile_completed": profile.profile_completed})
