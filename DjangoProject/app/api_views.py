from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
import secrets

from .models import Books, Loans, Reservations, Notifications, Fines, Users, Librarybranches, Authors, Catalogs, Bookauthors, Bookcatalogs
from .serializers import (
    BookSerializer, BookCreateSerializer,
    LoanSerializer, LoanCreateSerializer,
    ReservationSerializer, ReservationCreateSerializer,
    NotificationSerializer, NotificationCreateSerializer, 
    FineSerializer, FineUpdateSerializer,
    UserBasicSerializer, UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    LibraryBranchSerializer, AuthorSerializer, CatalogSerializer, PublisherSerializer
)


# -----------------------
# Helper Functions
# -----------------------

def is_librarian(user):
    """Check if user is a librarian"""
    # Check accounts.User role
    if hasattr(user, 'role'):
        return user.role == 'librarian'
    return False


def get_app_user(user):
    """
    Get (or create) app.Users instance from accounts.User.
    If missing, auto-create a minimal record so student flows don't fail.
    """
    try:
        return Users.objects.get(username=user.username)
    except Users.DoesNotExist:
        # Auto-create a corresponding legacy user record
        try:
            role = getattr(user, 'role', 'student')
            password_stub = secrets.token_hex(16)  # not used for auth here
            return Users.objects.create(
                username=user.username,
                password=password_stub,
                email=user.email or f"{user.username}@example.com",
                first_name=user.first_name or '',
                last_name=user.last_name or '',
                role=role if role in dict(Users.ROLE_CHOICES) else 'student',
                date_created=timezone.now(),
            )
        except Exception:
            return None


# -----------------------
# Books API Views
# -----------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def book_list_create(request):
    """
    GET: List all books (with optional search/filter)
    POST: Create a new book (librarian only)
    """
    if request.method == 'GET':
        # Get query parameters
        search = request.query_params.get('search', None)
        branch_id = request.query_params.get('branch', None)
        available_only = request.query_params.get('available_only', None)
        
        # Filter out deleted books if is_deleted field exists
        # Handle case where migration hasn't been run yet
        from django.db import OperationalError, ProgrammingError
        try:
            books = Books.objects.filter(is_deleted=False)
        except (OperationalError, ProgrammingError) as e:
            # Database column doesn't exist yet (migration not run)
            # Fallback to get all books
            books = Books.objects.all()
        except Exception:
            # Other errors - fallback to get all books
            books = Books.objects.all()
        
        # Apply filters
        if search:
            books = books.filter(
                Q(title__icontains=search) | Q(isbn__icontains=search)
            )
        
        if branch_id:
            books = books.filter(branch_id=branch_id)
        
        if available_only == 'true':
            books = books.filter(available_copies__gt=0)
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Only librarians can create books
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can create books.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BookCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Extract authors and categories before saving
            authors_ids = request.data.get('authors', [])
            categories_ids = request.data.get('categories', [])
            
            # Save book
            book = serializer.save()
            
            # Handle authors (many-to-many)
            if authors_ids:
                # Clear existing authors
                Bookauthors.objects.filter(book=book).delete()
                # Add new authors
                for author_id in authors_ids:
                    try:
                        author = Authors.objects.get(pk=author_id)
                        Bookauthors.objects.get_or_create(book=book, author=author)
                    except Authors.DoesNotExist:
                        pass
            
            # Handle categories (many-to-many)
            if categories_ids:
                # Clear existing categories
                Bookcatalogs.objects.filter(book=book).delete()
                # Add new categories
                for category_id in categories_ids:
                    try:
                        catalog = Catalogs.objects.get(pk=category_id)
                        Bookcatalogs.objects.get_or_create(book=book, catalog=catalog)
                    except Catalogs.DoesNotExist:
                        pass
            
            return Response(
                BookSerializer(book).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def book_detail(request, book_id):
    """
    GET: Get book details
    PUT: Update book (librarian only)
    DELETE: Delete book (librarian only)
    """
    book = get_object_or_404(Books, pk=book_id)
    
    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can update books.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BookCreateSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            # Extract authors and categories before saving
            authors_ids = request.data.get('authors', None)
            categories_ids = request.data.get('categories', None)
            
            # Save book
            serializer.save()
            
            # Handle authors (many-to-many) - only if provided
            if authors_ids is not None:
                # Clear existing authors
                Bookauthors.objects.filter(book=book).delete()
                # Add new authors
                for author_id in authors_ids:
                    try:
                        author = Authors.objects.get(pk=author_id)
                        Bookauthors.objects.get_or_create(book=book, author=author)
                    except Authors.DoesNotExist:
                        pass
            
            # Handle categories (many-to-many) - only if provided
            if categories_ids is not None:
                # Clear existing categories
                Bookcatalogs.objects.filter(book=book).delete()
                # Add new categories
                for category_id in categories_ids:
                    try:
                        catalog = Catalogs.objects.get(pk=category_id)
                        Bookcatalogs.objects.get_or_create(book=book, catalog=catalog)
                    except Catalogs.DoesNotExist:
                        pass
            
            # Refresh book to get updated relationships
            book.refresh_from_db()
            return Response(BookSerializer(book).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can delete books.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete (recommended) - check if field exists
        if hasattr(book, 'is_deleted'):
            book.is_deleted = True
            book.save()
            return Response(
                {'message': 'Book deleted successfully (soft delete).'},
                status=status.HTTP_200_OK
            )
        else:
            # Hard delete if is_deleted field doesn't exist
            book.delete()
            return Response(
                {'message': 'Book deleted successfully.'},
                status=status.HTTP_204_NO_CONTENT
            )


# -----------------------
# Loans API Views
# -----------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def loan_list_create(request):
    """
    GET: List loans (students see their own, librarians see all)
    POST: Create a new loan (librarian only)
    """
    if request.method == 'GET':
        app_user = get_app_user(request.user)
        
        if is_librarian(request.user):
            # Librarians see all loans
            loans = Loans.objects.all().order_by('-loan_date')
        else:
            # Students see only their loans
            if app_user:
                loans = Loans.objects.filter(user=app_user).order_by('-loan_date')
            else:
                return Response(
                    {'error': 'User not found in library system.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Only librarians can create loans
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can create loans.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = LoanCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Get the book before creating loan
            book_id = serializer.validated_data['book'].book_id
            book = Books.objects.get(pk=book_id)
            
            # Check availability
            if book.available_copies <= 0:
                return Response(
                    {'error': 'No available copies for this book.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create loan with loan_date set
            loan = serializer.save(loan_date=timezone.now())
            
            # Update book availability
            book.available_copies -= 1
            book.save()
            
            return Response(
                LoanSerializer(loan).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_return(request, loan_id):
    """
    Return a book (librarian only)
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can return books.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    loan = get_object_or_404(Loans, pk=loan_id)
    
    if loan.return_date:
        return Response(
            {'error': 'This book has already been returned.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate return date
    return_date = timezone.now().date()
    
    # Calculate late days and create fine if overdue
    late_days = 0
    fine_created = False
    fine_amount = 0.00
    if return_date > loan.due_date:
        late_days = (return_date - loan.due_date).days
        # Calculate fine: $1.00 per day late (minimum $1.00)
        fine_amount = max(1.00, late_days * 1.00)
        
        # Check if fine already exists for this loan
        existing_fine = Fines.objects.filter(loan=loan).first()
        if not existing_fine:
            # Create fine automatically
            Fines.objects.create(
                user=loan.user,
                loan=loan,
                amount=fine_amount,
                paid=0,
                date_issued=timezone.now()
            )
            fine_created = True
            
            # Create notification for the student about the fine
            notification_message = f"Fine of ${fine_amount:.2f} issued for late return of '{loan.book.title}' ({late_days} day{'s' if late_days > 1 else ''} late)."
            Notifications.objects.create(
                user=loan.user,
                message=notification_message,
                notification_type='overdue',
                created_at=timezone.now(),
                is_read=0
            )
    
    # Update loan
    loan.return_date = return_date
    loan.save()
    
    # Update book availability
    loan.book.available_copies += 1
    loan.book.save()
    
    # Check for pending reservations and notify the first student in queue
    pending_reservations = Reservations.objects.filter(
        book=loan.book,
        status='pending'
    ).order_by('reservation_date')
    
    if pending_reservations.exists() and loan.book.available_copies > 0:
        # Notify the first student in the reservation queue
        first_reservation = pending_reservations.first()
        
        # Create notification for the student
        notification_message = f"Book '{loan.book.title}' is now available! Your reservation is ready."
        Notifications.objects.create(
            user=first_reservation.user,
            message=notification_message,
            notification_type='reservation',
            created_at=timezone.now(),
            is_read=0
        )
        
        # Update reservation status to 'ready'
        first_reservation.status = 'ready'
        first_reservation.save()
    
    response_data = {
        'message': 'Book returned successfully.',
        'loan': LoanSerializer(loan).data
    }
    
    if late_days > 0:
        response_data['late_days'] = late_days
        response_data['fine_created'] = fine_created
        if fine_created:
            response_data['fine_amount'] = float(fine_amount)
            response_data['message'] = f'Book returned successfully. Fine of ${fine_amount:.2f} issued for {late_days} day{"s" if late_days > 1 else ""} late return.'
    
    return Response(response_data, status=status.HTTP_200_OK)


# -----------------------
# Reservations API Views
# -----------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reservation_list_create(request):
    """
    GET: List reservations (students see their own, librarians see all)
    POST: Create a new reservation
    """
    if request.method == 'GET':
        app_user = get_app_user(request.user)
        
        if is_librarian(request.user):
            # Librarians see all reservations
            reservations = Reservations.objects.all().order_by('-reservation_date')
        else:
            # Students see only their reservations
            if app_user:
                reservations = Reservations.objects.filter(user=app_user).order_by('-reservation_date')
            else:
                return Response(
                    {'error': 'User not found in library system.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        app_user = get_app_user(request.user)
        data = request.data.copy()  # make mutable copy

        if not app_user:
            return Response(
                {'error': 'User not found in library system.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Students can only create reservations for themselves
        if not is_librarian(request.user):
            data['user'] = app_user.user_id
        
        serializer = ReservationCreateSerializer(data=data)
        if serializer.is_valid():
            # Ensure required fields are set before hitting DB
            reservation = serializer.save(
                reservation_date=timezone.now(),
                status=data.get('status', 'pending')
            )

            return Response(
                ReservationSerializer(reservation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reservation_cancel(request, reservation_id):
    """
    Cancel a reservation
    """
    reservation = get_object_or_404(Reservations, pk=reservation_id)
    app_user = get_app_user(request.user)
    
    # Check permission: students can only cancel their own reservations
    if not is_librarian(request.user):
        if not app_user or reservation.user != app_user:
            return Response(
                {'error': 'You can only cancel your own reservations.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if reservation.status == 'cancelled':
        return Response(
            {'error': 'This reservation is already cancelled.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reservation.status = 'cancelled'
    reservation.save()
    
    return Response(
        {
            'message': 'Reservation cancelled successfully.',
            'reservation': ReservationSerializer(reservation).data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reservation_update_status(request, reservation_id):
    """
    Update reservation status (librarian only)
    Used to mark reservations as ready, picked_up, or cancel them
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can update reservation status.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    reservation = get_object_or_404(Reservations, pk=reservation_id)
    new_status = request.data.get('status')
    
    if not new_status:
        return Response(
            {'error': 'Status is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    valid_statuses = ['ready', 'picked_up', 'cancelled', 'completed']
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Business logic checks
    if new_status == 'ready':
        # Check if book is available
        if reservation.book.available_copies <= 0:
            return Response(
                {'error': 'Book is not available. Cannot mark reservation as ready.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Only pending reservations can be marked as ready
        if reservation.status != 'pending':
            return Response(
                {'error': 'Only pending reservations can be marked as ready.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    elif new_status == 'picked_up':
        # Only ready reservations can be marked as picked_up
        if reservation.status not in ['ready', 'pending']:
            return Response(
                {'error': 'Only ready or pending reservations can be marked as picked_up.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # When marked as picked_up, we should create a loan automatically
        # For now, just update status - librarian can create loan separately
    
    elif new_status == 'cancelled':
        if reservation.status == 'cancelled':
            return Response(
                {'error': 'This reservation is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Update status
    reservation.status = new_status
    reservation.save()
    
    return Response(
        {
            'message': f'Reservation status updated to {new_status}.',
            'reservation': ReservationSerializer(reservation).data
        },
        status=status.HTTP_200_OK
    )


# -----------------------
# Notifications API Views
# -----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    Get notifications:
    - Students: their own notifications
    - Librarians: all notifications (notification history)
    """
    app_user = get_app_user(request.user)
    
    if not app_user:
        return Response(
            {'error': 'User not found in library system.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Librarians see all notifications, students see only their own
    if is_librarian(request.user):
        notifications = Notifications.objects.all().order_by('-created_at')
    else:
        notifications = Notifications.objects.filter(user=app_user).order_by('-created_at')
    
    # Filter by read status if provided
    is_read = request.query_params.get('is_read', None)
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        notifications = notifications.filter(is_read=1 if is_read_bool else 0)
    
    # Filter by user if provided (for librarians)
    user_id = request.query_params.get('user_id', None)
    if user_id and is_librarian(request.user):
        try:
            notifications = notifications.filter(user_id=user_id)
        except ValueError:
            pass
    
    # Filter by notification type if provided
    notification_type = request.query_params.get('type', None)
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, notification_id):
    """
    Mark a notification as read
    - Students can only mark their own notifications
    - Librarians can mark any notification
    """
    notification = get_object_or_404(Notifications, pk=notification_id)
    app_user = get_app_user(request.user)
    
    # Check permission: students can only mark their own, librarians can mark any
    if not is_librarian(request.user):
        if not app_user or notification.user != app_user:
            return Response(
                {'error': 'You can only mark your own notifications as read.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    notification.is_read = 1
    notification.save()
    
    return Response(
        {
            'message': 'Notification marked as read.',
            'notification': NotificationSerializer(notification).data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_create(request):
    """
    Create a custom notification (librarian only)
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can create notifications.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = NotificationCreateSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save()
        return Response(
            {
                'message': 'Notification sent successfully.',
                'notification': NotificationSerializer(notification).data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_trigger_overdue(request):
    """
    Trigger overdue notices for all overdue loans (librarian only)
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can trigger overdue notices.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    today = timezone.now().date()
    
    # Find all overdue loans (due_date < today and return_date is None)
    overdue_loans = Loans.objects.filter(
        due_date__lt=today,
        return_date__isnull=True
    )
    
    notifications_created = 0
    notifications_updated = 0
    
    for loan in overdue_loans:
        # Calculate late days
        late_days = (today - loan.due_date).days
        
        # Check if notification already exists for this loan
        existing_notification = Notifications.objects.filter(
            user=loan.user,
            notification_type='overdue',
            message__icontains=loan.book.title
        ).order_by('-created_at').first()
        
        # Only create notification if it doesn't exist or if it's been more than 7 days
        should_create = True
        if existing_notification:
            days_since_notification = (today - existing_notification.created_at.date()).days
            if days_since_notification < 7:
                should_create = False
        
        if should_create:
            notification_message = (
                f"Overdue Notice: Your book '{loan.book.title}' is {late_days} day{'s' if late_days > 1 else ''} overdue. "
                f"Please return it as soon as possible to avoid additional fines."
            )
            
            Notifications.objects.create(
                user=loan.user,
                message=notification_message,
                notification_type='overdue',
                created_at=timezone.now(),
                is_read=0
            )
            notifications_created += 1
        else:
            notifications_updated += 1
    
    return Response(
        {
            'message': f'Overdue notices processed. {notifications_created} new notifications created, {notifications_updated} already exist.',
            'notifications_created': notifications_created,
            'overdue_loans_count': overdue_loans.count()
        },
        status=status.HTTP_200_OK
    )


# -----------------------
# Fines API Views
# -----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fine_list(request):
    """
    Get all fines (students see their own, librarians see all)
    """
    app_user = get_app_user(request.user)
    
    if is_librarian(request.user):
        # Librarians see all fines
        fines = Fines.objects.all().order_by('-date_issued')
    else:
        # Students see only their fines
        if app_user:
            fines = Fines.objects.filter(user=app_user).order_by('-date_issued')
        else:
            return Response(
                {'error': 'User not found in library system.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Filter by paid status if provided
    paid = request.query_params.get('paid', None)
    if paid is not None:
        paid_bool = paid.lower() == 'true'
        fines = fines.filter(paid=1 if paid_bool else 0)
    
    serializer = FineSerializer(fines, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fine_pay(request, fine_id):
    """
    Pay a fine (librarian only - to mark as paid)
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can process fine payments.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    fine = get_object_or_404(Fines, pk=fine_id)
    
    if fine.paid == 1:
        return Response(
            {'error': 'This fine has already been paid.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    fine.paid = 1
    fine.save()
    
    return Response(
        {
            'message': 'Fine marked as paid.',
            'fine': FineSerializer(fine).data
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def fine_update(request, fine_id):
    """
    Update fine amount (librarian only)
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can update fines.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    fine = get_object_or_404(Fines, pk=fine_id)
    
    serializer = FineUpdateSerializer(fine, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'Fine amount updated successfully.',
                'fine': FineSerializer(fine).data
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def fine_delete(request, fine_id):
    """
    Delete a fine (librarian only - if mistake)
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can delete fines.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    fine = get_object_or_404(Fines, pk=fine_id)
    fine.delete()
    
    return Response(
        {'message': 'Fine deleted successfully.'},
        status=status.HTTP_200_OK
    )


# -----------------------
# Users API Views
# -----------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """
    GET: List users (librarians see all, students see only themselves)
    POST: Create new user (librarian only)
    """
    if request.method == 'GET':
        if is_librarian(request.user):
            # Librarians can see all users
            users = Users.objects.all().order_by('first_name', 'last_name')
            
            # Filter by role if provided
            role = request.query_params.get('role', None)
            if role:
                users = users.filter(role=role)
            
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Students can only see their own info
            app_user = get_app_user(request.user)
            if app_user:
                serializer = UserSerializer(app_user)
                return Response([serializer.data], status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'User not found in library system.'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    elif request.method == 'POST':
        # Only librarians can create users
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can create user accounts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """
    GET: Get user details
    PUT: Update user (librarian only, or user can update themselves)
    DELETE: Delete/deactivate user (librarian only)
    """
    user = get_object_or_404(Users, pk=user_id)
    app_user = get_app_user(request.user)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Users can update themselves, librarians can update anyone
        if not is_librarian(request.user):
            if not app_user or app_user.user_id != user_id:
                return Response(
                    {'error': 'You can only update your own account.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(
                UserSerializer(updated_user).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Only librarians can delete users
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can delete user accounts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Don't allow deleting yourself
        if app_user and app_user.user_id == user_id:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete user (cascade will delete student/librarian profile)
        user.delete()
        return Response(
            {'message': 'User account deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def branch_list(request):
    """
    Get list of library branches (for librarian assignment)
    """
    branches = Librarybranches.objects.all().order_by('branch_name')
    serializer = LibraryBranchSerializer(branches, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def author_list(request):
    """
    Get list of authors (for book form)
    """
    authors = Authors.objects.all().order_by('last_name', 'first_name')
    serializer = AuthorSerializer(authors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list(request):
    """
    Get list of categories (for book form)
    """
    categories = Catalogs.objects.all().order_by('category_name')
    serializer = CatalogSerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def publisher_list(request):
    """
    Get list of publishers (for book form)
    """
    from .models import Publishers
    from .serializers import PublisherSerializer
    publishers = Publishers.objects.all().order_by('name')
    serializer = PublisherSerializer(publishers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# -----------------------
# Dashboard API Views
# -----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics (librarian only)
    Returns:
    - total_books: Total number of books in library (excluding soft-deleted)
    - total_students: Total number of student users
    """
    if not is_librarian(request.user):
        return Response(
            {'error': 'Only librarians can access dashboard statistics.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Total books (excluding soft-deleted)
    try:
        total_books = Books.objects.filter(is_deleted=False).count()
    except Exception:
        total_books = Books.objects.count()
    
    # Total students
    total_students = Users.objects.filter(role='student').count()
    
    stats = {
        'total_books': total_books,
        'total_students': total_students
    }
    
    return Response(stats, status=status.HTTP_200_OK)


