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
    path('reservations/<int:reservation_id>/update-status/', api_views.reservation_update_status, name='reservation_update_status'),
    
    # Notifications API
    path('notifications/', api_views.notification_list, name='notification_list'),
    path('notifications/create/', api_views.notification_create, name='notification_create'),
    path('notifications/trigger-overdue/', api_views.notification_trigger_overdue, name='notification_trigger_overdue'),
    path('notifications/<int:notification_id>/read/', api_views.notification_mark_read, name='notification_mark_read'),
    
    # Fines API
    path('fines/', api_views.fine_list, name='fine_list'),
    path('fines/<int:fine_id>/pay/', api_views.fine_pay, name='fine_pay'),
    
    # Users API
    path('users/', api_views.user_list, name='user_list'),
    path('users/<int:user_id>/', api_views.user_detail, name='user_detail'),
    
    # Branches API
    path('branches/', api_views.branch_list, name='branch_list'),
    
    # Authors API
    path('authors/', api_views.author_list, name='author_list'),
    
    # Categories API
    path('categories/', api_views.category_list, name='category_list'),
    
    # Publishers API
    path('publishers/', api_views.publisher_list, name='publisher_list'),
]


