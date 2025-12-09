from rest_framework import serializers
from .models import (
    Books, Loans, Reservations, Notifications, Fines,
    Authors, Publishers, Catalogs, Librarybranches,
    Bookauthors, Bookcatalogs, Users
)


# -----------------------
# Nested Serializers (for relationships)
# -----------------------

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Authors"""
    class Meta:
        model = Authors
        fields = ['author_id', 'first_name', 'last_name', 'bio']


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publishers"""
    class Meta:
        model = Publishers
        fields = ['publisher_id', 'name', 'address', 'contact_email']


class CatalogSerializer(serializers.ModelSerializer):
    """Serializer for Catalogs"""
    class Meta:
        model = Catalogs
        fields = ['catalog_id', 'category_name', 'description']


class LibraryBranchSerializer(serializers.ModelSerializer):
    """Serializer for Library Branches"""
    class Meta:
        model = Librarybranches
        fields = ['branch_id', 'branch_name', 'address', 'phone']


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer (for nested use)"""
    class Meta:
        model = Users
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'role']


# -----------------------
# Books Serializers
# -----------------------

class BookSerializer(serializers.ModelSerializer):
    """Serializer for Books with nested relationships"""
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    authors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    
    class Meta:
        model = Books
        fields = [
            'book_id', 'title', 'isbn', 'pages', 'publication_year',
            'publisher', 'publisher_name', 'branch', 'branch_name',
            'available_copies', 'authors', 'categories'
        ]
        read_only_fields = ['book_id']
    
    def get_authors(self, obj):
        """Get all authors for this book"""
        book_authors = Bookauthors.objects.filter(book=obj)
        authors = [ba.author for ba in book_authors]
        return AuthorSerializer(authors, many=True).data
    
    def get_categories(self, obj):
        """Get all categories for this book"""
        book_catalogs = Bookcatalogs.objects.filter(book=obj)
        catalogs = [bc.catalog for bc in book_catalogs]
        return CatalogSerializer(catalogs, many=True).data


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating books"""
    class Meta:
        model = Books
        fields = [
            'title', 'isbn', 'pages', 'publication_year',
            'publisher', 'branch', 'available_copies'
        ]


# -----------------------
# Loans Serializers
# -----------------------

class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loans with nested book and user info"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    user_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Loans
        fields = [
            'loan_id', 'user', 'user_name', 'book', 'book_title', 'book_isbn',
            'loan_date', 'due_date', 'return_date', 'is_overdue'
        ]
        read_only_fields = ['loan_id', 'loan_date']
    
    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def get_is_overdue(self, obj):
        """Check if loan is overdue"""
        from django.utils import timezone
        if obj.return_date:
            return False
        return timezone.now().date() > obj.due_date


class LoanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating loans"""
    class Meta:
        model = Loans
        fields = ['user', 'book', 'due_date']
    
    def validate(self, attrs):
        """Validate loan creation"""
        book = attrs.get('book')
        if book and book.available_copies <= 0:
            raise serializers.ValidationError({
                'book': 'No available copies for this book.'
            })
        return attrs


# -----------------------
# Reservations Serializers
# -----------------------

class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservations"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    book_available_copies = serializers.IntegerField(source='book.available_copies', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservations
        fields = [
            'reservation_id', 'user', 'user_name', 'book', 'book_title', 'book_isbn',
            'book_available_copies', 'reservation_date', 'status'
        ]
        read_only_fields = ['reservation_id', 'reservation_date']
    
    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}"


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reservations"""
    class Meta:
        model = Reservations
        fields = ['user', 'book', 'status']
    
    def validate_status(self, value):
        """Validate status"""
        valid_statuses = ['pending', 'ready', 'picked_up', 'active', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f'Status must be one of: {", ".join(valid_statuses)}'
            )
        return value


# -----------------------
# Notifications Serializers
# -----------------------

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notifications"""
    class Meta:
        model = Notifications
        fields = [
            'notification_id', 'user', 'message', 'notification_type',
            'created_at', 'is_read'
        ]
        read_only_fields = ['notification_id', 'created_at']


# -----------------------
# Fines Serializers
# -----------------------

class FineSerializer(serializers.ModelSerializer):
    """Serializer for Fines"""
    user_name = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='loan.book.title', read_only=True)
    is_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = Fines
        fields = [
            'fine_id', 'user', 'user_name', 'loan', 'book_title',
            'amount', 'paid', 'is_paid', 'date_issued'
        ]
        read_only_fields = ['fine_id', 'date_issued']
    
    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def get_is_paid(self, obj):
        """Check if fine is paid"""
        return obj.paid == 1


