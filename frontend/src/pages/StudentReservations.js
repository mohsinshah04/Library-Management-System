import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import ReservationCard from '../components/ReservationCard';
import './StudentReservations.css';

function StudentReservations() {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelling, setCancelling] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchReservations();
  }, []);

  const fetchReservations = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/reservations/');
      setReservations(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load reservations. Please try again.');
        console.error('Error fetching reservations:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (reservationId) => {
    const confirmCancel = window.confirm('Are you sure you want to cancel this reservation?');
    if (!confirmCancel) return;

    try {
      setCancelling(reservationId);
      await api.post(`/reservations/${reservationId}/cancel/`);
      await fetchReservations(); // Refresh the list
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to cancel reservation. Please try again.');
      console.error('Error cancelling reservation:', err);
    } finally {
      setCancelling(null);
    }
  };

  const activeReservations = reservations.filter(r => 
    r.status !== 'cancelled' && r.status !== 'completed'
  );
  const cancelledReservations = reservations.filter(r => r.status === 'cancelled');
  const completedReservations = reservations.filter(r => r.status === 'completed');

  if (loading) {
    return (
      <div className="student-reservations-page">
        <div className="student-reservations-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your reservations...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-reservations-page">
        <div className="student-reservations-container">
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchReservations} className="retry-btn">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="student-reservations-page">
      <div className="student-reservations-container">
        <div className="reservations-header">
          <div>
            <h1>📋 My Reservations</h1>
            <p className="subtitle">View and manage your book reservations</p>
          </div>
          <div className="header-actions">
            <button onClick={() => navigate('/books')} className="browse-books-btn">
              Browse Books
            </button>
            <button onClick={() => navigate(-1)} className="back-btn">
              ← Back
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="reservations-summary">
          <div className="stat-card">
            <div className="stat-number">{activeReservations.length}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card completed-stat">
            <div className="stat-number">{completedReservations.length}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card cancelled-stat">
            <div className="stat-number">{cancelledReservations.length}</div>
            <div className="stat-label">Cancelled</div>
          </div>
        </div>

        {/* Active Reservations */}
        {activeReservations.length > 0 && (
          <div className="reservations-section">
            <h2 className="section-title">Active Reservations</h2>
            <div className="reservations-list">
              {activeReservations.map((reservation) => (
                <ReservationCard
                  key={reservation.reservation_id}
                  reservation={reservation}
                  onCancel={handleCancel}
                  showCancelButton={true}
                />
              ))}
            </div>
          </div>
        )}

        {/* Completed Reservations */}
        {completedReservations.length > 0 && (
          <div className="reservations-section">
            <h2 className="section-title">Completed Reservations</h2>
            <div className="reservations-list">
              {completedReservations.map((reservation) => (
                <ReservationCard
                  key={reservation.reservation_id}
                  reservation={reservation}
                  showCancelButton={false}
                />
              ))}
            </div>
          </div>
        )}

        {/* Cancelled Reservations */}
        {cancelledReservations.length > 0 && (
          <div className="reservations-section">
            <h2 className="section-title">Cancelled Reservations</h2>
            <div className="reservations-list">
              {cancelledReservations.map((reservation) => (
                <ReservationCard
                  key={reservation.reservation_id}
                  reservation={reservation}
                  showCancelButton={false}
                />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {reservations.length === 0 && (
          <div className="empty-state">
            <p className="empty-message">You don't have any reservations yet.</p>
            <button 
              onClick={() => navigate('/books')} 
              className="browse-books-btn"
            >
              Browse Books to Reserve
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentReservations;

