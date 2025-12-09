import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import LoanCard from '../components/LoanCard';
import './StudentLoans.css';

function StudentLoans() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [returning, setReturning] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLoans();
  }, []);

  const fetchLoans = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/loans/');
      setLoans(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load loans. Please try again.');
        console.error('Error fetching loans:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (loanId) => {
    const confirmReturn = window.confirm('Are you sure you want to return this book?');
    if (!confirmReturn) return;

    try {
      setReturning(loanId);
      await api.post(`/loans/${loanId}/return/`);
      await fetchLoans(); // Refresh the list
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to return book. Please contact a librarian.');
      console.error('Error returning book:', err);
    } finally {
      setReturning(null);
    }
  };

  const activeLoans = loans.filter(loan => !loan.return_date);
  const returnedLoans = loans.filter(loan => loan.return_date);
  const overdueLoans = activeLoans.filter(loan => loan.is_overdue);

  if (loading) {
    return (
      <div className="student-loans-page">
        <div className="student-loans-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your loans...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-loans-page">
        <div className="student-loans-container">
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchLoans} className="retry-btn">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="student-loans-page">
      <div className="student-loans-container">
        <div className="loans-header">
          <div>
            <h1>📚 My Loans</h1>
            <p className="subtitle">View and manage your borrowed books</p>
          </div>
          <button onClick={() => navigate(-1)} className="back-btn">
            ← Back
          </button>
        </div>

        {/* Summary Stats */}
        <div className="loans-summary">
          <div className="stat-card">
            <div className="stat-number">{activeLoans.length}</div>
            <div className="stat-label">Active Loans</div>
          </div>
          <div className="stat-card overdue-stat">
            <div className="stat-number">{overdueLoans.length}</div>
            <div className="stat-label">Overdue</div>
          </div>
          <div className="stat-card returned-stat">
            <div className="stat-number">{returnedLoans.length}</div>
            <div className="stat-label">Returned</div>
          </div>
        </div>

        {/* Active Loans */}
        {activeLoans.length > 0 && (
          <div className="loans-section">
            <h2 className="section-title">Active Loans</h2>
            <div className="loans-list">
              {activeLoans.map((loan) => (
                <LoanCard
                  key={loan.loan_id}
                  loan={loan}
                  onReturn={handleReturn}
                  showReturnButton={true}
                  isLibrarian={false}
                />
              ))}
            </div>
          </div>
        )}

        {/* Returned Loans */}
        {returnedLoans.length > 0 && (
          <div className="loans-section">
            <h2 className="section-title">Loan History</h2>
            <div className="loans-list">
              {returnedLoans.map((loan) => (
                <LoanCard
                  key={loan.loan_id}
                  loan={loan}
                  showReturnButton={false}
                  isLibrarian={false}
                />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {loans.length === 0 && (
          <div className="empty-state">
            <p className="empty-message">You don't have any loans yet.</p>
            <button 
              onClick={() => navigate('/books')} 
              className="browse-books-btn"
            >
              Browse Books
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentLoans;

