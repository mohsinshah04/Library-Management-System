"""
URL configuration for library_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    # path('api/', include('books.urls')),
]

