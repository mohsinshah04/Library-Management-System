import React from 'react';
import './ReservationCard.css';

function ReservationCard({ 
  reservation, 
  onCancel, 
  showCancelButton = false,
  isLibrarian = false,
  onMarkReady = null,
  onMarkPickedUp = null,
  onUpdateStatus = null
}) {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'status-pending';
      case 'ready':
        return 'status-ready';
      case 'picked_up':
        return 'status-picked-up';
      case 'active':
        return 'status-active';
      case 'completed':
        return 'status-completed';
      case 'cancelled':
        return 'status-cancelled';
      default:
        return '';
    }
  };

  return (
    <div className={`reservation-card ${getStatusColor(reservation.status)}`}>
      <div className="reservation-card-header">
        <h3 className="reservation-book-title">{reservation.book_title}</h3>
        <span className={`status-badge ${getStatusColor(reservation.status)}`}>
          {reservation.status}
        </span>
      </div>
      
      <div className="reservation-card-body">
        <div className="reservation-info">
          {isLibrarian && reservation.user_name && (
            <p className="reservation-user">
              <strong>Student:</strong> {reservation.user_name}
            </p>
          )}
          
          <p className="reservation-isbn">
            <strong>ISBN:</strong> {reservation.book_isbn}
          </p>
          
          <p className="reservation-date">
            <strong>Reserved:</strong> {formatDate(reservation.reservation_date)}
          </p>
          
          {isLibrarian && reservation.book_available_copies !== undefined && (
            <p className="reservation-availability">
              <strong>Available Copies:</strong> {reservation.book_available_copies}
            </p>
          )}
          
          <p className="reservation-status-text">
            <strong>Status:</strong> {reservation.status}
          </p>
        </div>
      </div>
      
      {/* Student Actions */}
      {showCancelButton && reservation.status !== 'cancelled' && reservation.status !== 'completed' && (
        <div className="reservation-card-footer">
          <button 
            onClick={() => onCancel(reservation.reservation_id)} 
            className="cancel-btn"
          >
            Cancel Reservation
          </button>
        </div>
      )}
      
      {/* Librarian Actions */}
      {isLibrarian && reservation.status !== 'cancelled' && reservation.status !== 'completed' && (
        <div className="reservation-card-footer">
          {reservation.status === 'pending' && reservation.book_available_copies > 0 && (
            <button 
              onClick={() => onUpdateStatus && onUpdateStatus(reservation.reservation_id, 'ready')} 
              className="action-btn ready-btn"
            >
              Mark as Ready
            </button>
          )}
          {(reservation.status === 'ready' || reservation.status === 'pending') && (
            <button 
              onClick={() => onUpdateStatus && onUpdateStatus(reservation.reservation_id, 'picked_up')} 
              className="action-btn picked-up-btn"
            >
              Mark as Picked Up
            </button>
          )}
          <button 
            onClick={() => onUpdateStatus && onUpdateStatus(reservation.reservation_id, 'cancelled')} 
            className="action-btn cancel-btn"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

export default ReservationCard;

