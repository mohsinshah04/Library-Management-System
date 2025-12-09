import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './Dashboard.css';

function StudentDashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch current user data when component loads
    fetchCurrentUser();
  }, []);

  const fetchCurrentUser = async () => {
    try {
      setLoading(true);
      // Use our configured axios instance (automatically adds token)
      const response = await api.get('/auth/me/');
      setUser(response.data);
      setError('');
    } catch (err) {
      if (err.response?.status === 401) {
        // Token expired or invalid - redirect to login
        navigate('/login');
      } else {
        setError('Failed to load user data');
        console.error('Error fetching user:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    // Clear tokens and user data
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Redirect to login
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-card">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-card">
          <div className="error-message">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <div className="dashboard-header">
          <h1>Student Dashboard</h1>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>

        <div className="welcome-section">
          <h2>Welcome, {user?.first_name || user?.username}!</h2>
          <p className="user-info">
            <strong>Role:</strong> {user?.role}
          </p>
          {user?.email && (
            <p className="user-info">
              <strong>Email:</strong> {user?.email}
            </p>
          )}
        </div>

        <div className="dashboard-content">
          <div className="info-box clickable" onClick={() => navigate('/books')}>
            <h3>🔍 Browse Books</h3>
            <p>Find and browse available books</p>
            <span className="action-link">View Books →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/student/loans')}>
            <h3>📚 My Loans</h3>
            <p>View your borrowed books</p>
            <span className="action-link">View Loans →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/student/reservations')}>
            <h3>📋 My Reservations</h3>
            <p>View your book reservations</p>
            <span className="action-link">View Reservations →</span>
          </div>
        </div>

        <div className="debug-info">
          <details>
            <summary>Debug Info (Click to expand)</summary>
            <pre>{JSON.stringify(user, null, 2)}</pre>
          </details>
        </div>
      </div>
    </div>
  );
}

export default StudentDashboard;

