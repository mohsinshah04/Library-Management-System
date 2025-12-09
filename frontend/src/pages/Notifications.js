import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './Notifications.css';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'unread', 'read'
  const [typeFilter, setTypeFilter] = useState('all'); // 'all', 'overdue', 'reservation', 'alert'
  const [showSendForm, setShowSendForm] = useState(false);
  const [sending, setSending] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  
  const isLibrarian = user?.role === 'librarian';

  useEffect(() => {
    // Get user from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const parsedUser = JSON.parse(userStr);
        setUser(parsedUser);
        
        // Fetch users if librarian
        if (parsedUser?.role === 'librarian') {
          fetchUsers();
        }
      } catch (e) {
        console.error('Error parsing user:', e);
      }
    }
  }, []);
  
  useEffect(() => {
    fetchNotifications();
  }, [filter, typeFilter]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {};
      if (filter === 'unread') {
        params.is_read = 'false';
      } else if (filter === 'read') {
        params.is_read = 'true';
      }
      
      if (typeFilter !== 'all') {
        params.type = typeFilter;
      }
      
      const response = await api.get('/notifications/', { params });
      setNotifications(response.data);
    } catch (err) {
      console.error('Error fetching notifications:', err);
      setError('Failed to load notifications. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchUsers = async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/${notificationId}/read/`);
      // Update local state
      setNotifications(prevNotifications =>
        prevNotifications.map(notif =>
          notif.notification_id === notificationId
            ? { ...notif, is_read: 1 }
            : notif
        )
      );
    } catch (err) {
      console.error('Error marking notification as read:', err);
      alert('Failed to mark notification as read. Please try again.');
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

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'reservation':
        return '📚';
      case 'overdue':
        return '⚠️';
      case 'alert':
        return '🔔';
      default:
        return '📬';
    }
  };
  
  const handleSendNotification = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const user_id = parseInt(formData.get('user_id'));
    const message = formData.get('message');
    const notification_type = formData.get('notification_type') || 'alert';
    
    if (!user_id || !message.trim()) {
      alert('Please select a user and enter a message.');
      return;
    }
    
    setSending(true);
    try {
      await api.post('/notifications/create/', {
        user_id,
        message: message.trim(),
        notification_type
      });
      alert('Notification sent successfully!');
      setShowSendForm(false);
      e.target.reset();
      fetchNotifications();
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to send notification.';
      alert(errorMsg);
      console.error('Error sending notification:', err);
    } finally {
      setSending(false);
    }
  };
  
  const handleTriggerOverdue = async () => {
    if (!window.confirm('This will send overdue notices to all students with overdue books. Continue?')) {
      return;
    }
    
    setTriggering(true);
    try {
      const response = await api.post('/notifications/trigger-overdue/');
      alert(response.data.message || 'Overdue notices processed successfully!');
      fetchNotifications();
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to trigger overdue notices.';
      alert(errorMsg);
      console.error('Error triggering overdue notices:', err);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) {
    return (
      <div className="notifications-page">
        <div className="notifications-container">
          <div className="loading">Loading notifications...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="notifications-page">
        <div className="notifications-container">
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchNotifications} className="retry-btn">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => n.is_read === 0).length;

  return (
    <div className="notifications-page">
      <div className="notifications-container">
        <div className="notifications-header">
          <button onClick={() => navigate(-1)} className="back-btn">
            ← Back
          </button>
          <h1>{isLibrarian ? 'Notification Management' : 'Notifications'}</h1>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount} unread</span>
          )}
          {isLibrarian && (
            <div className="librarian-actions">
              <button
                onClick={() => setShowSendForm(!showSendForm)}
                className="action-btn send-btn"
              >
                {showSendForm ? '✕ Cancel' : '+ Send Notification'}
              </button>
              <button
                onClick={handleTriggerOverdue}
                className="action-btn trigger-btn"
                disabled={triggering}
              >
                {triggering ? 'Processing...' : '⚠️ Trigger Overdue Notices'}
              </button>
            </div>
          )}
        </div>
        
        {isLibrarian && showSendForm && (
          <div className="send-notification-form">
            <h3>Send Custom Notification</h3>
            <form onSubmit={handleSendNotification}>
              <div className="form-group">
                <label htmlFor="user_id">Send to:</label>
                <select id="user_id" name="user_id" required>
                  <option value="">Select a user...</option>
                  {users.map(u => (
                    <option key={u.user_id} value={u.user_id}>
                      {u.first_name} {u.last_name} ({u.email}) - {u.role}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="notification_type">Type:</label>
                <select id="notification_type" name="notification_type">
                  <option value="alert">Alert</option>
                  <option value="overdue">Overdue</option>
                  <option value="reservation">Reservation</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="message">Message:</label>
                <textarea
                  id="message"
                  name="message"
                  rows="4"
                  required
                  placeholder="Enter notification message..."
                />
              </div>
              <div className="form-actions">
                <button type="submit" disabled={sending} className="submit-btn">
                  {sending ? 'Sending...' : 'Send Notification'}
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="notifications-filters">
          <div className="filter-group">
            <span className="filter-label">Status:</span>
            <button
              className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
              onClick={() => setFilter('unread')}
            >
              Unread ({unreadCount})
            </button>
            <button
              className={`filter-btn ${filter === 'read' ? 'active' : ''}`}
              onClick={() => setFilter('read')}
            >
              Read
            </button>
          </div>
          {isLibrarian && (
            <div className="filter-group">
              <span className="filter-label">Type:</span>
              <button
                className={`filter-btn ${typeFilter === 'all' ? 'active' : ''}`}
                onClick={() => setTypeFilter('all')}
              >
                All
              </button>
              <button
                className={`filter-btn ${typeFilter === 'overdue' ? 'active' : ''}`}
                onClick={() => setTypeFilter('overdue')}
              >
                Overdue
              </button>
              <button
                className={`filter-btn ${typeFilter === 'reservation' ? 'active' : ''}`}
                onClick={() => setTypeFilter('reservation')}
              >
                Reservation
              </button>
              <button
                className={`filter-btn ${typeFilter === 'alert' ? 'active' : ''}`}
                onClick={() => setTypeFilter('alert')}
              >
                Alert
              </button>
            </div>
          )}
        </div>

        <div className="notifications-list">
          {notifications.length === 0 ? (
            <div className="no-notifications">
              <p>No notifications found.</p>
            </div>
          ) : (
            notifications.map(notification => (
              <div
                key={notification.notification_id}
                className={`notification-card ${notification.is_read === 0 ? 'unread' : 'read'}`}
              >
                <div className="notification-icon">
                  {getNotificationIcon(notification.notification_type)}
                </div>
                <div className="notification-content">
                  {isLibrarian && notification.user_name && (
                    <div className="notification-user">
                      <strong>To:</strong> {notification.user_name} ({notification.user_email})
                    </div>
                  )}
                  <div className="notification-message">
                    {notification.message}
                  </div>
                  <div className="notification-meta">
                    <span className="notification-type">
                      {notification.notification_type}
                    </span>
                    <span className="notification-date">
                      {formatDate(notification.created_at)}
                    </span>
                  </div>
                </div>
                {notification.is_read === 0 && (
                  <button
                    className="mark-read-btn"
                    onClick={() => handleMarkAsRead(notification.notification_id)}
                    title="Mark as read"
                  >
                    ✓
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default Notifications;

