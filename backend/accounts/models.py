from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds a 'role' field to distinguish between students and librarians.
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text='User role: student or librarian'
    )
    
    # Additional fields we might need later
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        db_table = 'users'

