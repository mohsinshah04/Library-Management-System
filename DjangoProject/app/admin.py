from django.contrib import admin
from .models import (
    Users, Books, Authors, Publishers, Catalogs, Librarybranches,
    Students, Librarians, Loans, Fines, Reservations, Notifications,
    Bookauthors, Bookcatalogs
)


# -----------------------
# Users Admin
# -----------------------
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_created']
    list_filter = ['role', 'date_created']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['user_id', 'date_created']
    ordering = ['-date_created']


# -----------------------
# Authors Admin
# -----------------------
@admin.register(Authors)
class AuthorsAdmin(admin.ModelAdmin):
    list_display = ['author_id', 'first_name', 'last_name', 'bio']
    search_fields = ['first_name', 'last_name']
    readonly_fields = ['author_id']


# -----------------------
# Publishers Admin
# -----------------------
@admin.register(Publishers)
class PublishersAdmin(admin.ModelAdmin):
    list_display = ['publisher_id', 'name', 'address', 'contact_email']
    search_fields = ['name', 'address', 'contact_email']
    readonly_fields = ['publisher_id']


# -----------------------
# Catalogs Admin
# -----------------------
@admin.register(Catalogs)
class CatalogsAdmin(admin.ModelAdmin):
    list_display = ['catalog_id', 'category_name', 'description']
    search_fields = ['category_name']
    readonly_fields = ['catalog_id']


# -----------------------
# Library Branches Admin
# -----------------------
@admin.register(Librarybranches)
class LibrarybranchesAdmin(admin.ModelAdmin):
    list_display = ['branch_id', 'branch_name', 'address', 'phone']
    search_fields = ['branch_name', 'address']
    readonly_fields = ['branch_id']


# -----------------------
# Books Admin
# -----------------------
@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'title', 'isbn', 'publisher', 'branch', 'available_copies', 'publication_year']
    list_filter = ['publisher', 'branch', 'publication_year']
    search_fields = ['title', 'isbn']
    readonly_fields = ['book_id']
    filter_horizontal = []  # Can be used for many-to-many if needed


# -----------------------
# Students Admin
# -----------------------
@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'major', 'year']
    search_fields = ['student_id__username', 'major']
    readonly_fields = ['student_id']


# -----------------------
# Librarians Admin
# -----------------------
@admin.register(Librarians)
class LibrariansAdmin(admin.ModelAdmin):
    list_display = ['librarian_id', 'employee_id', 'branch']
    search_fields = ['librarian_id__username', 'employee_id']
    list_filter = ['branch']
    readonly_fields = ['librarian_id']


# -----------------------
# Loans Admin
# -----------------------
@admin.register(Loans)
class LoansAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'user', 'book', 'loan_date', 'due_date', 'return_date', 'is_overdue']
    list_filter = ['loan_date', 'due_date', 'return_date']
    search_fields = ['user__username', 'book__title', 'book__isbn']
    readonly_fields = ['loan_id', 'loan_date']
    date_hierarchy = 'loan_date'
    
    def is_overdue(self, obj):
        """Check if loan is overdue"""
        from django.utils import timezone
        if obj.return_date:
            return False
        return timezone.now().date() > obj.due_date
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


# -----------------------
# Fines Admin
# -----------------------
@admin.register(Fines)
class FinesAdmin(admin.ModelAdmin):
    list_display = ['fine_id', 'user', 'loan', 'amount', 'paid', 'date_issued', 'is_paid']
    list_filter = ['paid', 'date_issued']
    search_fields = ['user__username', 'loan__book__title']
    readonly_fields = ['fine_id', 'date_issued']
    date_hierarchy = 'date_issued'
    
    def is_paid(self, obj):
        """Check if fine is paid"""
        return obj.paid == 1
    is_paid.boolean = True
    is_paid.short_description = 'Paid'


# -----------------------
# Reservations Admin
# -----------------------
@admin.register(Reservations)
class ReservationsAdmin(admin.ModelAdmin):
    list_display = ['reservation_id', 'user', 'book', 'reservation_date', 'status']
    list_filter = ['status', 'reservation_date']
    search_fields = ['user__username', 'book__title', 'book__isbn']
    readonly_fields = ['reservation_id', 'reservation_date']
    date_hierarchy = 'reservation_date'


# -----------------------
# Notifications Admin
# -----------------------
@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'user', 'notification_type', 'created_at', 'is_read']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['notification_id', 'created_at']
    date_hierarchy = 'created_at'


# -----------------------
# Book Authors (Many-to-Many) Admin
# -----------------------
@admin.register(Bookauthors)
class BookauthorsAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'author']
    list_filter = ['book', 'author']
    search_fields = ['book__title', 'author__first_name', 'author__last_name']
    readonly_fields = ['id']


# -----------------------
# Book Catalogs (Many-to-Many) Admin
# -----------------------
@admin.register(Bookcatalogs)
class BookcatalogsAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'catalog']
    list_filter = ['book', 'catalog']
    search_fields = ['book__title', 'catalog__category_name']
    readonly_fields = ['id']
