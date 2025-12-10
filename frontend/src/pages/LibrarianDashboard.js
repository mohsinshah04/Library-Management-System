import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './Dashboard.css';

function LibrarianDashboard() {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch current user data and stats when component loads
    fetchCurrentUser();
    fetchDashboardStats();
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

  const fetchDashboardStats = async () => {
    try {
      setStatsLoading(true);
      const response = await api.get('/dashboard/stats/');
      console.log('Dashboard stats API response:', response.data);
      
      if (response.data) {
        console.log('Setting stats:', response.data);
        // Ensure values are numbers
        const statsData = {
          total_books: Number(response.data.total_books) || 0,
          total_students: Number(response.data.total_students) || 0
        };
        console.log('Processed stats:', statsData);
        setStats(statsData);
      } else {
        console.warn('No data in response');
        setStats({
          total_books: 0,
          total_students: 0
        });
      }
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      console.error('Error response:', err.response);
      // Set default stats with 0 values if API fails
      setStats({
        total_books: 0,
        total_students: 0
      });
    } finally {
      setStatsLoading(false);
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
          <h1>Librarian Dashboard</h1>
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

        {/* Statistics Section */}
        <div className="stats-section">
          <h2 className="section-title">Library Statistics</h2>
          {statsLoading ? (
            <div className="loading">Loading statistics...</div>
          ) : stats ? (
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📚</div>
                <div className="stat-content">
                  <div className="stat-value" style={{color: 'white', fontSize: '32px', fontWeight: 'bold'}}>
                    {stats.total_books !== undefined && stats.total_books !== null ? String(stats.total_books) : '0'}
                  </div>
                  <div className="stat-label">Total Books</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-content">
                  <div className="stat-value" style={{color: 'white', fontSize: '32px', fontWeight: 'bold'}}>
                    {stats.total_students !== undefined && stats.total_students !== null ? String(stats.total_students) : '0'}
                  </div>
                  <div className="stat-label">Total Students</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="error-message">Failed to load statistics. Please refresh the page.</div>
          )}
        </div>

        {/* Quick Actions Section */}
        <div className="quick-actions-section">
          <h2 className="section-title">Quick Actions</h2>
          <div className="quick-actions-grid">
            <button 
              className="quick-action-btn"
              onClick={() => navigate('/librarian/books')}
            >
              <span className="action-icon">➕</span>
              <span className="action-text">Add Book</span>
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => navigate('/librarian/users')}
            >
              <span className="action-icon">👤</span>
              <span className="action-text">Add User</span>
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => navigate('/librarian/loans')}
            >
              <span className="action-icon">📝</span>
              <span className="action-text">Process Loan</span>
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => navigate('/librarian/loans')}
            >
              <span className="action-icon">↩️</span>
              <span className="action-text">Process Return</span>
            </button>
          </div>
        </div>

        <div className="dashboard-content">
          <div className="info-box clickable" onClick={() => navigate('/librarian/books')}>
            <h3>📚 Manage Books</h3>
            <p>Add, edit, and manage library books</p>
            <span className="action-link">Go to Books →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/librarian/reservations')}>
            <h3>📋 Manage Reservations</h3>
            <p>View and manage all book reservations</p>
            <span className="action-link">View Reservations →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/librarian/loans')}>
            <h3>📊 Manage Loans</h3>
            <p>Issue books and monitor all loans</p>
            <span className="action-link">Manage Loans →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/notifications')}>
            <h3>🔔 Notifications</h3>
            <p>View your notifications and alerts</p>
            <span className="action-link">View Notifications →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/librarian/users')}>
            <h3>👥 Manage Users</h3>
            <p>Create, update, and manage user accounts</p>
            <span className="action-link">Manage Users →</span>
          </div>

          <div className="info-box clickable" onClick={() => navigate('/librarian/loans')}>
            <h3>💰 Manage Fines</h3>
            <p>View and process overdue fines</p>
            <span className="action-link">View Fines →</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LibrarianDashboard;

