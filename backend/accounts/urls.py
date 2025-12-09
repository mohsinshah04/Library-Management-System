from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('me/', views.get_current_user, name='get_current_user'),
    
    # JWT token refresh endpoint (built-in from SimpleJWT)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

