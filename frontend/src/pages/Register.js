import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './Register.css';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'student',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validate passwords match
    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      setLoading(false);
      return;
    }

    try {
      // Send registration request to Django backend
      const response = await api.post('/auth/register/', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm,
        role: formData.role,
        first_name: formData.first_name,
        last_name: formData.last_name,
      });

      // Store tokens in localStorage (registration also returns tokens)
      const { tokens, user } = response.data;
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(user));

      // Redirect based on user role
      if (user.role === 'student') {
        navigate('/student/dashboard');
      } else if (user.role === 'librarian') {
        navigate('/librarian/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      // Handle errors
      console.error('Registration error:', err);
      console.error('Error response:', err.response?.data);
      
      if (err.response && err.response.data) {
        // Backend validation errors
        const errorData = err.response.data;
        
        // Handle different error formats
        if (typeof errorData === 'string') {
          setError(errorData);
        } else if (errorData.message) {
          setError(errorData.message);
        } else if (errorData.error) {
          setError(errorData.error);
        } else {
          // Collect all validation errors
          const errorMessages = [];
          
          // Check for field-specific errors
          Object.keys(errorData).forEach(field => {
            const fieldError = errorData[field];
            if (Array.isArray(fieldError)) {
              errorMessages.push(`${field}: ${fieldError.join(', ')}`);
            } else if (typeof fieldError === 'string') {
              errorMessages.push(`${field}: ${fieldError}`);
            } else if (Array.isArray(fieldError) && fieldError.length > 0) {
              errorMessages.push(`${field}: ${fieldError[0]}`);
            }
          });
          
          if (errorMessages.length > 0) {
            setError(errorMessages.join('. '));
          } else {
            setError('Registration failed. Please check your information and try again.');
          }
        }
      } else if (err.message) {
        setError(`Error: ${err.message}`);
      } else {
        setError('Network error. Please check if the backend server is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h1 className="register-title">Library Management System</h1>
        <h2 className="register-subtitle">Create Account</h2>
        
        <form onSubmit={handleSubmit} className="register-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="Enter your first name"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Last Name</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Enter your last name"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Choose a username"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">Account Type *</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              disabled={loading}
              className="role-select"
            >
              <option value="student">Student</option>
              <option value="librarian">Librarian</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              placeholder="At least 8 characters"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password_confirm">Confirm Password *</label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              minLength={8}
              placeholder="Re-enter your password"
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="register-button"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="login-link">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;

