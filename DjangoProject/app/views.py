from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Books, Users
from .forms import BookForm, UserForm

# ----------------------------
# Books CRUD
# ----------------------------

class BookListView(ListView):
    model = Books
    template_name = 'books/book_list.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    pk_url_kwarg = 'book_id'

class BookCreateView(CreateView):
    model = Books
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

class BookUpdateView(UpdateView):
    model = Books
    form_class = BookForm
    template_name = 'books/book_form.html'
    pk_url_kwarg = 'book_id'
    success_url = reverse_lazy('book_list')

class BookDeleteView(DeleteView):
    model = Books
    template_name = 'books/book_confirm_delete.html'
    pk_url_kwarg = 'book_id'
    success_url = reverse_lazy('book_list')


# ----------------------------
# Users CRUD
# ----------------------------

class UserListView(ListView):
    model = Users
    template_name = 'users/user_list.html'
    context_object_name = 'users'

class UserDetailView(DetailView):
    model = Users
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'

class UserCreateView(CreateView):
    model = Users
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')

class UserUpdateView(UpdateView):
    model = Users
    form_class = UserForm
    template_name = 'users/user_form.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('user_list')

class UserDeleteView(DeleteView):
    model = Users
    template_name = 'users/user_confirm_delete.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('user_list')
