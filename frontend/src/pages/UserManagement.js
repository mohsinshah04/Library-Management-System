import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import UserForm from '../components/UserForm';
import './UserManagement.css';

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [filter, setFilter] = useState('all'); // all, student, librarian
  const [searchTerm, setSearchTerm] = useState('');
  const [deleting, setDeleting] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
    fetchBranches();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load users. Please try again.');
        console.error('Error fetching users:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchBranches = async () => {
    try {
      // Try to fetch branches if endpoint exists
      const response = await api.get('/branches/').catch(() => null);
      if (response) {
        setBranches(response.data);
      }
    } catch (err) {
      console.error('Error fetching branches:', err);
      // Branches are optional, continue without them
    }
  };

  const handleCreateUser = async (data) => {
    try {
      setLoading(true);
      await api.post('/users/', data);
      setShowForm(false);
      await fetchUsers();
    } catch (err) {
      const errorData = err.response?.data;
      let errorMessage = 'Failed to create user.';
      
      if (errorData) {
        const looksLikeHtml = typeof errorData === 'string' && errorData.trim().startsWith('<');
        if (looksLikeHtml) {
          errorMessage = 'Server error occurred. Please check the console for details.';
          console.error('Backend returned HTML error:', errorData);
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else {
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          errorMessage = fieldErrors || JSON.stringify(errorData);
        }
      }
      
      alert(errorMessage);
      console.error('Error creating user:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (data) => {
    try {
      setLoading(true);
      await api.put(`/users/${editingUser.user_id}/`, data);
      setEditingUser(null);
      await fetchUsers();
    } catch (err) {
      const errorData = err.response?.data;
      let errorMessage = 'Failed to update user.';
      
      if (errorData) {
        const looksLikeHtml = typeof errorData === 'string' && errorData.trim().startsWith('<');
        if (looksLikeHtml) {
          errorMessage = 'Server error occurred. Please check the console for details.';
          console.error('Backend returned HTML error:', errorData);
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else {
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          errorMessage = fieldErrors || JSON.stringify(errorData);
        }
      }
      
      alert(errorMessage);
      console.error('Error updating user:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(userId);
      await api.delete(`/users/${userId}/`);
      await fetchUsers();
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to delete user.';
      alert(errorMsg);
      console.error('Error deleting user:', err);
    } finally {
      setDeleting(null);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setShowForm(false);
  };

  const filteredUsers = users.filter(user => {
    // Filter by role
    if (filter !== 'all' && user.role !== filter) return false;
    
    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const fullName = `${user.first_name} ${user.last_name}`.toLowerCase();
      const email = (user.email || '').toLowerCase();
      const username = (user.username || '').toLowerCase();
      return fullName.includes(searchLower) || 
             email.includes(searchLower) || 
             username.includes(searchLower);
    }
    
    return true;
  });

  const studentCount = users.filter(u => u.role === 'student').length;
  const librarianCount = users.filter(u => u.role === 'librarian').length;

  if (loading && users.length === 0) {
    return (
      <div className="user-management-page">
        <div className="user-management-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading users...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management-page">
      <div className="user-management-container">
        <div className="users-header">
          <div>
            <h1>👥 Manage Users</h1>
            <p className="subtitle">Create, update, and manage user accounts</p>
          </div>
          <div className="header-actions">
            <button onClick={() => navigate(-1)} className="back-btn">
              ← Back
            </button>
            <button 
              className="primary-btn" 
              onClick={() => {
                setEditingUser(null);
                setShowForm(true);
              }}
            >
              + Add User
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="users-summary">
          <div className="stat-card">
            <div className="stat-number">{users.length}</div>
            <div className="stat-label">Total Users</div>
          </div>
          <div className="stat-card student-stat">
            <div className="stat-number">{studentCount}</div>
            <div className="stat-label">Students</div>
          </div>
          <div className="stat-card librarian-stat">
            <div className="stat-number">{librarianCount}</div>
            <div className="stat-label">Librarians</div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="search-filter-bar">
          <input
            type="text"
            placeholder="Search by name, email, or username..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="filter-tabs">
            <button 
              className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All ({users.length})
            </button>
            <button 
              className={`filter-tab ${filter === 'student' ? 'active' : ''}`}
              onClick={() => setFilter('student')}
            >
              Students ({studentCount})
            </button>
            <button 
              className={`filter-tab ${filter === 'librarian' ? 'active' : ''}`}
              onClick={() => setFilter('librarian')}
            >
              Librarians ({librarianCount})
            </button>
          </div>
        </div>

        {/* Create/Edit User Form */}
        {(showForm || editingUser) && (
          <div className="form-card">
            <div className="form-card-header">
              <h3>{editingUser ? 'Edit User' : 'Add New User'}</h3>
              <button 
                className="secondary-btn" 
                onClick={() => {
                  setShowForm(false);
                  setEditingUser(null);
                }}
              >
                ✕
              </button>
            </div>
            <UserForm
              user={editingUser}
              onSubmit={editingUser ? handleUpdateUser : handleCreateUser}
              onCancel={() => {
                setShowForm(false);
                setEditingUser(null);
              }}
              loading={loading}
              branches={branches}
            />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchUsers} className="retry-btn">Retry</button>
          </div>
        )}

        {/* Users List */}
        {filteredUsers.length === 0 ? (
          <div className="empty-state">
            <p className="empty-message">
              {searchTerm 
                ? `No users found matching "${searchTerm}"` 
                : 'No users found.'}
            </p>
          </div>
        ) : (
          <div className="users-list">
            {filteredUsers.map((user) => (
              <div key={user.user_id} className="user-card">
                <div className="user-card-header">
                  <div>
                    <h3 className="user-name">
                      {user.first_name} {user.last_name}
                    </h3>
                    <span className={`role-badge ${user.role}`}>
                      {user.role}
                    </span>
                  </div>
                  <div className="user-actions">
                    <button
                      onClick={() => handleEdit(user)}
                      className="edit-btn"
                      disabled={loading || deleting === user.user_id}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.user_id)}
                      className="delete-btn"
                      disabled={loading || deleting === user.user_id}
                    >
                      {deleting === user.user_id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </div>
                <div className="user-card-body">
                  <div className="user-info">
                    <p><strong>Username:</strong> {user.username}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    {user.role === 'student' && (
                      <>
                        {user.major && <p><strong>Major:</strong> {user.major}</p>}
                        {user.year && <p><strong>Year:</strong> {user.year}</p>}
                      </>
                    )}
                    {user.role === 'librarian' && (
                      <>
                        {user.employee_id && <p><strong>Employee ID:</strong> {user.employee_id}</p>}
                        {user.branch_name && <p><strong>Branch:</strong> {user.branch_name}</p>}
                      </>
                    )}
                    <p><strong>Created:</strong> {new Date(user.date_created).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default UserManagement;

