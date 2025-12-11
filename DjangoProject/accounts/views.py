from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
import logging
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user (student or librarian).
    
    POST /api/auth/register/
    Body: {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "role": "student",  # or "librarian"
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Automatically create corresponding app.Users record for library system
        try:
            from app.models import Users as AppUsers
            # Check if app user already exists
            try:
                app_user = AppUsers.objects.get(username=user.username)
            except AppUsers.DoesNotExist:
                # Create app.Users record
                role = getattr(user, 'role', 'student')
                # Ensure role is valid for app.Users model
                valid_roles = [choice[0] for choice in AppUsers.ROLE_CHOICES]
                if role not in valid_roles:
                    role = 'student'  # Default to student if role is invalid
                
                password_stub = secrets.token_hex(16)  # not used for auth here
                email = user.email or f"{user.username}@example.com"
                
                # Check if email already exists
                try:
                    existing_user = AppUsers.objects.get(email=email)
                    # If email exists but username is different, update username
                    if existing_user.username != user.username:
                        existing_user.username = user.username
                        existing_user.save()
                        app_user = existing_user
                    else:
                        app_user = existing_user
                except AppUsers.DoesNotExist:
                    # Create new app user
                    app_user = AppUsers.objects.create(
                        username=user.username,
                        password=password_stub,
                        email=email,
                        first_name=getattr(user, 'first_name', '') or '',
                        last_name=getattr(user, 'last_name', '') or '',
                        role=role,
                        date_created=timezone.now(),
                    )
        except Exception as e:
            # Log error but don't fail registration
            logger.warning(f"Failed to create app.Users for {user.username}: {str(e)}")
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT tokens.
    
    POST /api/auth/login/
    Body: {
        "username": "john_doe",
        "password": "password123"
    }
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current logged-in user information.
    Requires valid JWT token in Authorization header.
    
    GET /api/auth/me/
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

