import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import ReservationCard from '../components/ReservationCard';
import './LibrarianReservations.css';

function LibrarianReservations() {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, pending, active, completed, cancelled
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

  const filteredReservations = reservations.filter(reservation => {
    if (filter === 'all') return true;
    return reservation.status.toLowerCase() === filter.toLowerCase();
  });

  const handleUpdateStatus = async (reservationId, newStatus) => {
    try {
      setLoading(true);
      await api.post(`/reservations/${reservationId}/update-status/`, { status: newStatus });
      await fetchReservations();
    } catch (err) {
      const errorMsg = err.response?.data?.error || `Failed to update reservation status.`;
      alert(errorMsg);
      console.error('Error updating reservation status:', err);
    } finally {
      setLoading(false);
    }
  };

  const pendingCount = reservations.filter(r => r.status === 'pending').length;
  const readyCount = reservations.filter(r => r.status === 'ready').length;
  const activeCount = reservations.filter(r => r.status === 'active').length;
  const completedCount = reservations.filter(r => r.status === 'completed').length;
  const cancelledCount = reservations.filter(r => r.status === 'cancelled').length;

  if (loading && reservations.length === 0) {
    return (
      <div className="librarian-reservations-page">
        <div className="librarian-reservations-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading reservations...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="librarian-reservations-page">
      <div className="librarian-reservations-container">
        <div className="reservations-header">
          <div>
            <h1>📋 Manage Reservations</h1>
            <p className="subtitle">View and manage all book reservations</p>
          </div>
          <button onClick={() => navigate(-1)} className="back-btn">
            ← Back
          </button>
        </div>

        {/* Summary Stats */}
        <div className="reservations-summary">
          <div className="stat-card">
            <div className="stat-number">{reservations.length}</div>
            <div className="stat-label">Total</div>
          </div>
          <div className="stat-card pending-stat">
            <div className="stat-number">{pendingCount}</div>
            <div className="stat-label">Pending</div>
          </div>
          <div className="stat-card ready-stat">
            <div className="stat-number">{readyCount}</div>
            <div className="stat-label">Ready</div>
          </div>
          <div className="stat-card active-stat">
            <div className="stat-number">{activeCount}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card completed-stat">
            <div className="stat-number">{completedCount}</div>
            <div className="stat-label">Completed</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="filter-tabs">
          <button 
            className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({reservations.length})
          </button>
          <button 
            className={`filter-tab ${filter === 'pending' ? 'active' : ''}`}
            onClick={() => setFilter('pending')}
          >
            Pending ({pendingCount})
          </button>
          <button 
            className={`filter-tab ${filter === 'ready' ? 'active' : ''}`}
            onClick={() => setFilter('ready')}
          >
            Ready ({readyCount})
          </button>
          <button 
            className={`filter-tab ${filter === 'active' ? 'active' : ''}`}
            onClick={() => setFilter('active')}
          >
            Active ({activeCount})
          </button>
          <button 
            className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completed ({completedCount})
          </button>
          <button 
            className={`filter-tab ${filter === 'cancelled' ? 'active' : ''}`}
            onClick={() => setFilter('cancelled')}
          >
            Cancelled ({cancelledCount})
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchReservations} className="retry-btn">Retry</button>
          </div>
        )}

        {/* Reservations List */}
        {filteredReservations.length === 0 ? (
          <div className="empty-state">
            <p className="empty-message">
              {filter === 'all' 
                ? 'No reservations found.' 
                : `No ${filter} reservations found.`}
            </p>
          </div>
        ) : (
          <div className="reservations-list">
            {filteredReservations.map((reservation) => (
              <ReservationCard
                key={reservation.reservation_id}
                reservation={reservation}
                showCancelButton={false}
                isLibrarian={true}
                onUpdateStatus={handleUpdateStatus}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LibrarianReservations;

