from rest_framework import serializers
from django.utils import timezone
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
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_created']
        read_only_fields = ['user_id', 'date_created']


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer with student/librarian profile info"""
    major = serializers.CharField(source='student_profile.major', read_only=True, allow_null=True)
    year = serializers.IntegerField(source='student_profile.year', read_only=True, allow_null=True)
    employee_id = serializers.CharField(source='librarian_profile.employee_id', read_only=True, allow_null=True)
    branch_name = serializers.CharField(source='librarian_profile.branch.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Users
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'date_created', 'major', 'year', 'employee_id', 'branch_name'
        ]
        read_only_fields = ['user_id', 'date_created']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True, required=True)
    major = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    employee_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    branch = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Users
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name', 
            'role', 'major', 'year', 'employee_id', 'branch'
        ]
    
    def validate_username(self, value):
        if Users.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        from .models import Students, Librarians
        
        # Extract profile data
        major = validated_data.pop('major', None)
        year = validated_data.pop('year', None)
        employee_id = validated_data.pop('employee_id', None)
        branch_id = validated_data.pop('branch', None)
        
        # Hash password
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        validated_data['date_created'] = timezone.now()
        
        # Create user
        user = Users.objects.create(**validated_data)
        
        # Create student or librarian profile
        if user.role == 'student':
            Students.objects.create(
                student_id=user,
                major=major,
                year=year
            )
        elif user.role == 'librarian':
            branch = None
            if branch_id:
                from .models import Librarybranches
                branch = Librarybranches.objects.get(pk=branch_id)
            Librarians.objects.create(
                librarian_id=user,
                employee_id=employee_id or f"EMP{user.user_id:04d}",
                branch=branch
            )
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users"""
    password = serializers.CharField(write_only=True, required=False)
    major = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    employee_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    branch = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Users
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name', 
            'role', 'major', 'year', 'employee_id', 'branch'
        ]
    
    def validate_username(self, value):
        # Check if username is being changed and if new username exists
        if self.instance and self.instance.username != value:
            if Users.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username already exists.")
        return value
    
    def validate_email(self, value):
        # Check if email is being changed and if new email exists
        if self.instance and self.instance.email != value:
            if Users.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value
    
    def update(self, instance, validated_data):
        from django.contrib.auth.hashers import make_password
        from .models import Students, Librarians, Librarybranches
        
        # Handle password update
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        
        # Extract profile data
        major = validated_data.pop('major', None)
        year = validated_data.pop('year', None)
        employee_id = validated_data.pop('employee_id', None)
        branch_id = validated_data.pop('branch', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update student or librarian profile
        if instance.role == 'student':
            student_profile, created = Students.objects.get_or_create(student_id=instance)
            if major is not None:
                student_profile.major = major
            if year is not None:
                student_profile.year = year
            student_profile.save()
        elif instance.role == 'librarian':
            librarian_profile, created = Librarians.objects.get_or_create(librarian_id=instance)
            if employee_id is not None:
                librarian_profile.employee_id = employee_id
            if branch_id is not None:
                librarian_profile.branch = Librarybranches.objects.get(pk=branch_id) if branch_id else None
            librarian_profile.save()
        
        return instance


# -----------------------
# Books Serializers
# -----------------------

class BookSerializer(serializers.ModelSerializer):
    """Serializer for Books with nested relationships"""
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    authors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Books
        fields = [
            'book_id', 'title', 'isbn', 'pages', 'publication_year', 'description',
            'publisher', 'publisher_name', 'branch', 'branch_name',
            'available_copies', 'authors', 'categories', 'status', 'is_deleted'
        ]
        read_only_fields = ['book_id']
        extra_kwargs = {
            'description': {'required': False, 'allow_null': True},
            'is_deleted': {'required': False, 'allow_null': True}
        }
    
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
    
    def get_status(self, obj):
        """Get book status: available or out on loan"""
        if obj.available_copies > 0:
            return 'available'
        else:
            return 'out on loan'
    
    def to_representation(self, instance):
        """Override to handle missing fields gracefully"""
        data = super().to_representation(instance)
        # Handle missing fields if migration hasn't been run
        if 'description' not in data or data['description'] is None:
            data['description'] = None
        if 'is_deleted' not in data:
            data['is_deleted'] = False
        return data


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books"""
    authors = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = Books
        fields = [
            'title', 'isbn', 'pages', 'publication_year', 'description',
            'publisher', 'branch', 'available_copies',
            'authors', 'categories'
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


