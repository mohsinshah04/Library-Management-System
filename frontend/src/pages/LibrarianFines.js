import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './LibrarianFines.css';

function LibrarianFines() {
  const [fines, setFines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, unpaid, paid
  const [editingFine, setEditingFine] = useState(null);
  const [updateAmount, setUpdateAmount] = useState('');
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchFines();
  }, [filter]);

  const fetchFines = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {};
      if (filter === 'unpaid') {
        params.paid = 'false';
      } else if (filter === 'paid') {
        params.paid = 'true';
      }
      
      const response = await api.get('/fines/', { params });
      setFines(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load fines. Please try again.');
        console.error('Error fetching fines:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsPaid = async (fineId) => {
    if (!window.confirm('Mark this fine as paid?')) {
      return;
    }

    try {
      await api.post(`/fines/${fineId}/pay/`);
      await fetchFines();
      alert('Fine marked as paid successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to mark fine as paid.';
      alert(errorMsg);
      console.error('Error marking fine as paid:', err);
    }
  };

  const handleUpdateAmount = async (fineId) => {
    const amount = parseFloat(updateAmount);
    if (isNaN(amount) || amount < 0) {
      alert('Please enter a valid amount (must be 0 or greater).');
      return;
    }

    try {
      setUpdating(true);
      await api.put(`/fines/${fineId}/update/`, { amount });
      await fetchFines();
      setEditingFine(null);
      setUpdateAmount('');
      alert('Fine amount updated successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to update fine amount.';
      alert(errorMsg);
      console.error('Error updating fine amount:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async (fineId) => {
    if (!window.confirm('Are you sure you want to delete this fine? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(fineId);
      await api.delete(`/fines/${fineId}/delete/`);
      await fetchFines();
      alert('Fine deleted successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to delete fine.';
      alert(errorMsg);
      console.error('Error deleting fine:', err);
    } finally {
      setDeleting(null);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    return `$${parseFloat(amount).toFixed(2)}`;
  };

  const unpaidFines = fines.filter(f => !f.is_paid);
  const paidFines = fines.filter(f => f.is_paid);
  const totalUnpaid = unpaidFines.reduce((sum, fine) => sum + parseFloat(fine.amount), 0);

  if (loading && fines.length === 0) {
    return (
      <div className="librarian-fines-page">
        <div className="librarian-fines-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading fines...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="librarian-fines-page">
      <div className="librarian-fines-container">
        <div className="fines-header">
          <button onClick={() => navigate(-1)} className="back-btn">
            ← Back
          </button>
          <h1>Manage Fines</h1>
        </div>

        {error && (
          <div className="error-message">{error}</div>
        )}

        {/* Statistics */}
        <div className="fines-stats">
          <div className="stat-card">
            <div className="stat-value">{fines.length}</div>
            <div className="stat-label">Total Fines</div>
          </div>
          <div className="stat-card unpaid">
            <div className="stat-value">{unpaidFines.length}</div>
            <div className="stat-label">Unpaid Fines</div>
          </div>
          <div className="stat-card paid">
            <div className="stat-value">{paidFines.length}</div>
            <div className="stat-label">Paid Fines</div>
          </div>
          <div className="stat-card total">
            <div className="stat-value">{formatCurrency(totalUnpaid)}</div>
            <div className="stat-label">Total Unpaid Amount</div>
          </div>
        </div>

        {/* Filters */}
        <div className="fines-filters">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filter === 'unpaid' ? 'active' : ''}`}
            onClick={() => setFilter('unpaid')}
          >
            Unpaid ({unpaidFines.length})
          </button>
          <button
            className={`filter-btn ${filter === 'paid' ? 'active' : ''}`}
            onClick={() => setFilter('paid')}
          >
            Paid ({paidFines.length})
          </button>
        </div>

        {/* Fines List */}
        <div className="fines-list">
          {fines.length === 0 ? (
            <div className="no-fines">
              <p>No fines found.</p>
            </div>
          ) : (
            fines.map(fine => (
              <div key={fine.fine_id} className={`fine-card ${fine.is_paid ? 'paid' : 'unpaid'}`}>
                <div className="fine-info">
                  <div className="fine-header-row">
                    <h3>{fine.book_title}</h3>
                    <span className={`fine-status ${fine.is_paid ? 'paid-badge' : 'unpaid-badge'}`}>
                      {fine.is_paid ? 'Paid' : 'Unpaid'}
                    </span>
                  </div>
                  <div className="fine-details">
                    <p><strong>Student:</strong> {fine.user_name} ({fine.user_email})</p>
                    <p><strong>Amount:</strong> <span className="fine-amount">{formatCurrency(fine.amount)}</span></p>
                    <p><strong>Date Issued:</strong> {formatDate(fine.date_issued)}</p>
                  </div>
                </div>
                <div className="fine-actions">
                  {!fine.is_paid && (
                    <>
                      <button
                        className="action-btn pay-btn"
                        onClick={() => handleMarkAsPaid(fine.fine_id)}
                      >
                        Mark as Paid
                      </button>
                      {editingFine === fine.fine_id ? (
                        <div className="update-amount-form">
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={updateAmount}
                            onChange={(e) => setUpdateAmount(e.target.value)}
                            placeholder="New amount"
                            className="amount-input"
                          />
                          <button
                            className="action-btn save-btn"
                            onClick={() => handleUpdateAmount(fine.fine_id)}
                            disabled={updating}
                          >
                            {updating ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            className="action-btn cancel-btn"
                            onClick={() => {
                              setEditingFine(null);
                              setUpdateAmount('');
                            }}
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          className="action-btn update-btn"
                          onClick={() => {
                            setEditingFine(fine.fine_id);
                            setUpdateAmount(fine.amount);
                          }}
                        >
                          Update Amount
                        </button>
                      )}
                    </>
                  )}
                  <button
                    className="action-btn delete-btn"
                    onClick={() => handleDelete(fine.fine_id)}
                    disabled={deleting === fine.fine_id}
                  >
                    {deleting === fine.fine_id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default LibrarianFines;

