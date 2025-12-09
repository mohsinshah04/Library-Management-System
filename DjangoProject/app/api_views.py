from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Books, Loans, Reservations, Notifications, Fines, Users
from .serializers import (
    BookSerializer, BookCreateSerializer,
    LoanSerializer, LoanCreateSerializer,
    ReservationSerializer, ReservationCreateSerializer,
    NotificationSerializer, FineSerializer
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
    """Get app.Users instance from accounts.User"""
    # Try to find matching user in app.Users by username or email
    try:
        app_user = Users.objects.get(username=user.username)
        return app_user
    except Users.DoesNotExist:
        # If not found, return None (user needs to be created in app.Users)
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
            book = serializer.save()
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
            serializer.save()
            return Response(BookSerializer(book).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_librarian(request.user):
            return Response(
                {'error': 'Only librarians can delete books.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
            loan = serializer.save(commit=False)
            book = loan.book
            
            # Check availability
            if book.available_copies <= 0:
                return Response(
                    {'error': 'No available copies for this book.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update book availability
            book.available_copies -= 1
            book.save()
            
            # Set loan date
            loan.loan_date = timezone.now()
            loan.save()
            
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
    
    # Update loan
    loan.return_date = timezone.now().date()
    loan.save()
    
    # Update book availability
    loan.book.available_copies += 1
    loan.book.save()
    
    return Response(
        {
            'message': 'Book returned successfully.',
            'loan': LoanSerializer(loan).data
        },
        status=status.HTTP_200_OK
    )


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
        
        if not app_user:
            return Response(
                {'error': 'User not found in library system.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Students can only create reservations for themselves
        if not is_librarian(request.user):
            request.data['user'] = app_user.user_id
        
        serializer = ReservationCreateSerializer(data=request.data)
        if serializer.is_valid():
            reservation = serializer.save()
            reservation.reservation_date = timezone.now()
            if 'status' not in request.data:
                reservation.status = 'pending'
            reservation.save()
            
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


# -----------------------
# Notifications API Views
# -----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    Get all notifications for the current user
    """
    app_user = get_app_user(request.user)
    
    if not app_user:
        return Response(
            {'error': 'User not found in library system.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    notifications = Notifications.objects.filter(user=app_user).order_by('-created_at')
    
    # Filter by read status if provided
    is_read = request.query_params.get('is_read', None)
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        notifications = notifications.filter(is_read=1 if is_read_bool else 0)
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, notification_id):
    """
    Mark a notification as read
    """
    notification = get_object_or_404(Notifications, pk=notification_id)
    app_user = get_app_user(request.user)
    
    # Check permission: users can only mark their own notifications as read
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


