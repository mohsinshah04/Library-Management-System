from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Books API
    path('books/', api_views.book_list_create, name='book_list_create'),
    path('books/<int:book_id>/', api_views.book_detail, name='book_detail'),
    
    # Loans API
    path('loans/', api_views.loan_list_create, name='loan_list_create'),
    path('loans/<int:loan_id>/return/', api_views.loan_return, name='loan_return'),
    
    # Reservations API
    path('reservations/', api_views.reservation_list_create, name='reservation_list_create'),
    path('reservations/<int:reservation_id>/cancel/', api_views.reservation_cancel, name='reservation_cancel'),
    
    # Notifications API
    path('notifications/', api_views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', api_views.notification_mark_read, name='notification_mark_read'),
    
    # Fines API
    path('fines/', api_views.fine_list, name='fine_list'),
    path('fines/<int:fine_id>/pay/', api_views.fine_pay, name='fine_pay'),
]


