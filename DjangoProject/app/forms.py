from django import forms
from .models import Books, Users

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'isbn', 'pages', 'publication_year', 'publisher', 'branch', 'available_copies']

class UserForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'role']
        widgets = {
            'password': forms.PasswordInput(),  # hide password input
        }
