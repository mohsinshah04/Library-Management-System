import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import LoanCard from '../components/LoanCard';
import LoanForm from '../components/LoanForm';
import './LibrarianLoans.css';

function LibrarianLoans() {
  const [loans, setLoans] = useState([]);
  const [books, setBooks] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [returning, setReturning] = useState(null);
  const [filter, setFilter] = useState('all'); // all, active, returned, overdue
  const navigate = useNavigate();

  useEffect(() => {
    fetchLoans();
    fetchBooks();
    fetchUsers();
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

  const fetchBooks = async () => {
    try {
      const response = await api.get('/books/');
      setBooks(response.data);
    } catch (err) {
      console.error('Error fetching books:', err);
    }
  };

  const fetchUsers = async () => {
    try {
      // Fetch only students for loan form
      const response = await api.get('/users/', { params: { role: 'student' } });
      setUsers(response.data);
    } catch (err) {
      console.error('Error fetching users:', err);
      // Users will be empty, librarian can still create loans manually
    }
  };

  const handleCreateLoan = async (data) => {
    try {
      setLoading(true);
      await api.post('/loans/', data);
      setShowForm(false);
      await fetchLoans();
      await fetchBooks(); // Refresh to update available copies
    } catch (err) {
      const errorData = err.response?.data;
      let errorMessage = 'Failed to create loan.';
      
      if (errorData) {
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else {
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          errorMessage = fieldErrors || JSON.stringify(errorData);
        }
      }
      
      alert(errorMessage);
      console.error('Error creating loan:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (loanId) => {
    try {
      setReturning(loanId);
      await api.post(`/loans/${loanId}/return/`);
      await fetchLoans();
      await fetchBooks(); // Refresh to update available copies
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to return book.');
      console.error('Error returning book:', err);
    } finally {
      setReturning(null);
    }
  };

  const filteredLoans = loans.filter(loan => {
    if (filter === 'active') return !loan.return_date;
    if (filter === 'returned') return loan.return_date;
    if (filter === 'overdue') return loan.is_overdue && !loan.return_date;
    return true; // all
  });

  const activeLoans = loans.filter(loan => !loan.return_date);
  const overdueLoans = activeLoans.filter(loan => loan.is_overdue);

  if (loading && loans.length === 0) {
    return (
      <div className="librarian-loans-page">
        <div className="librarian-loans-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading loans...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="librarian-loans-page">
      <div className="librarian-loans-container">
        <div className="loans-header">
          <div>
            <h1>📊 Manage Loans</h1>
            <p className="subtitle">Issue books and manage all library loans</p>
          </div>
          <div className="header-actions">
            <button onClick={() => navigate(-1)} className="back-btn">
              ← Back
            </button>
            <button 
              className="primary-btn" 
              onClick={() => setShowForm(true)}
            >
              + Issue Loan
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="loans-summary">
          <div className="stat-card">
            <div className="stat-number">{loans.length}</div>
            <div className="stat-label">Total Loans</div>
          </div>
          <div className="stat-card active-stat">
            <div className="stat-number">{activeLoans.length}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card overdue-stat">
            <div className="stat-number">{overdueLoans.length}</div>
            <div className="stat-label">Overdue</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="filter-tabs">
          <button 
            className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({loans.length})
          </button>
          <button 
            className={`filter-tab ${filter === 'active' ? 'active' : ''}`}
            onClick={() => setFilter('active')}
          >
            Active ({activeLoans.length})
          </button>
          <button 
            className={`filter-tab ${filter === 'overdue' ? 'active' : ''}`}
            onClick={() => setFilter('overdue')}
          >
            Overdue ({overdueLoans.length})
          </button>
          <button 
            className={`filter-tab ${filter === 'returned' ? 'active' : ''}`}
            onClick={() => setFilter('returned')}
          >
            Returned ({loans.filter(l => l.return_date).length})
          </button>
        </div>

        {/* Create Loan Form */}
        {showForm && (
          <div className="form-card">
            <div className="form-card-header">
              <h3>Issue New Loan</h3>
              <button className="secondary-btn" onClick={() => setShowForm(false)}>✕</button>
            </div>
            <LoanForm
              onSubmit={handleCreateLoan}
              onCancel={() => setShowForm(false)}
              loading={loading}
              books={books}
              users={users}
            />
          </div>
        )}

        {/* Loans List */}
        {error && (
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchLoans} className="retry-btn">Retry</button>
          </div>
        )}

        {filteredLoans.length === 0 ? (
          <div className="empty-state">
            <p className="empty-message">
              {filter === 'all' 
                ? 'No loans found.' 
                : `No ${filter} loans found.`}
            </p>
          </div>
        ) : (
          <div className="loans-list">
            {filteredLoans.map((loan) => (
              <LoanCard
                key={loan.loan_id}
                loan={loan}
                onReturn={handleReturn}
                showReturnButton={!loan.return_date}
                isLibrarian={true}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LibrarianLoans;

