from django.urls import path
from .views import (
    BookListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView,
    UserListView, UserDetailView, UserCreateView, UserUpdateView, UserDeleteView,
    loan_list, loan_create, loan_return
)

urlpatterns = [
    # Books
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book_detail'),
    path('books/create/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:book_id>/update/', BookUpdateView.as_view(), name='book_update'),
    path('books/<int:book_id>/delete/', BookDeleteView.as_view(), name='book_delete'),

    # Users
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # Loans
    path('loans/', loan_list, name='loan_list'),
    path('loans/create/', loan_create, name='loan_create'),
    path('loans/<int:loan_id>/return/', loan_return, name='loan_return'),
]
