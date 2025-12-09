import React from 'react';
import './ReservationCard.css';

function ReservationCard({ reservation, onCancel, showCancelButton = false }) {
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
          <p className="reservation-isbn">
            <strong>ISBN:</strong> {reservation.book_isbn}
          </p>
          
          <p className="reservation-date">
            <strong>Reserved:</strong> {formatDate(reservation.reservation_date)}
          </p>
          
          <p className="reservation-status-text">
            <strong>Status:</strong> {reservation.status}
          </p>
        </div>
      </div>
      
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
    </div>
  );
}

export default ReservationCard;

