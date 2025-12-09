import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './Notifications.css';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'unread', 'read'
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

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
      
      const response = await api.get('/notifications/', { params });
      setNotifications(response.data);
    } catch (err) {
      console.error('Error fetching notifications:', err);
      setError('Failed to load notifications. Please try again.');
    } finally {
      setLoading(false);
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
          <h1>Notifications</h1>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount} unread</span>
          )}
        </div>

        <div className="notifications-filters">
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

