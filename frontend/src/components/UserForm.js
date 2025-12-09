import React, { useState, useEffect } from 'react';
import './UserForm.css';

function UserForm({ user = null, onSubmit, onCancel, loading, branches = [] }) {
  const [form, setForm] = useState({
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'student',
    major: '',
    year: '',
    employee_id: '',
    branch: '',
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (user) {
      // Editing existing user
      setForm({
        username: user.username || '',
        password: '', // Don't pre-fill password
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        role: user.role || 'student',
        major: user.major || '',
        year: user.year || '',
        employee_id: user.employee_id || '',
        branch: user.branch || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    const newErrors = {};
    if (!form.username) newErrors.username = 'Username is required';
    if (!user && !form.password) newErrors.password = 'Password is required';
    if (!form.email) newErrors.email = 'Email is required';
    if (!form.first_name) newErrors.first_name = 'First name is required';
    if (!form.last_name) newErrors.last_name = 'Last name is required';
    if (!form.role) newErrors.role = 'Role is required';
    
    if (form.role === 'librarian' && !form.employee_id && !user) {
      // Employee ID is optional, will be auto-generated if not provided
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Prepare data
    const submitData = {
      username: form.username,
      email: form.email,
      first_name: form.first_name,
      last_name: form.last_name,
      role: form.role,
    };

    // Only include password if provided (for new users or password updates)
    if (form.password) {
      submitData.password = form.password;
    }

    // Add role-specific fields
    if (form.role === 'student') {
      if (form.major) submitData.major = form.major;
      if (form.year) submitData.year = parseInt(form.year) || null;
    } else if (form.role === 'librarian') {
      if (form.employee_id) submitData.employee_id = form.employee_id;
      if (form.branch) submitData.branch = parseInt(form.branch) || null;
    }

    onSubmit(submitData);
  };

  const isEditMode = !!user;

  return (
    <form className="user-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label>Username *</label>
          <input
            name="username"
            type="text"
            value={form.username}
            onChange={handleChange}
            required
            disabled={loading || isEditMode}
            className={errors.username ? 'error' : ''}
          />
          {errors.username && <span className="error-text">{errors.username}</span>}
        </div>
        <div className="form-group">
          <label>Email *</label>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
            disabled={loading}
            className={errors.email ? 'error' : ''}
          />
          {errors.email && <span className="error-text">{errors.email}</span>}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>First Name *</label>
          <input
            name="first_name"
            type="text"
            value={form.first_name}
            onChange={handleChange}
            required
            disabled={loading}
            className={errors.first_name ? 'error' : ''}
          />
          {errors.first_name && <span className="error-text">{errors.first_name}</span>}
        </div>
        <div className="form-group">
          <label>Last Name *</label>
          <input
            name="last_name"
            type="text"
            value={form.last_name}
            onChange={handleChange}
            required
            disabled={loading}
            className={errors.last_name ? 'error' : ''}
          />
          {errors.last_name && <span className="error-text">{errors.last_name}</span>}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Password {isEditMode ? '(leave blank to keep current)' : '*'} </label>
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required={!isEditMode}
            disabled={loading}
            className={errors.password ? 'error' : ''}
            placeholder={isEditMode ? 'Enter new password to change' : ''}
          />
          {errors.password && <span className="error-text">{errors.password}</span>}
        </div>
        <div className="form-group">
          <label>Role *</label>
          <select
            name="role"
            value={form.role}
            onChange={handleChange}
            required
            disabled={loading || isEditMode}
            className={errors.role ? 'error' : ''}
          >
            <option value="student">Student</option>
            <option value="librarian">Librarian</option>
          </select>
          {errors.role && <span className="error-text">{errors.role}</span>}
        </div>
      </div>

      {form.role === 'student' && (
        <div className="form-row">
          <div className="form-group">
            <label>Major</label>
            <input
              name="major"
              type="text"
              value={form.major}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., Computer Science"
            />
          </div>
          <div className="form-group">
            <label>Year</label>
            <input
              name="year"
              type="number"
              min="1"
              max="5"
              value={form.year}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., 1, 2, 3, 4"
            />
          </div>
        </div>
      )}

      {form.role === 'librarian' && (
        <div className="form-row">
          <div className="form-group">
            <label>Employee ID</label>
            <input
              name="employee_id"
              type="text"
              value={form.employee_id}
              onChange={handleChange}
              disabled={loading || isEditMode}
              placeholder="Auto-generated if not provided"
            />
            <p className="form-hint">Leave blank to auto-generate</p>
          </div>
          <div className="form-group">
            <label>Library Branch</label>
            <select
              name="branch"
              value={form.branch}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">Select a branch...</option>
              {branches.map((branch) => (
                <option key={branch.branch_id} value={branch.branch_id}>
                  {branch.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      <div className="form-actions">
        <button type="submit" className="primary" disabled={loading}>
          {isEditMode ? 'Update User' : 'Create User'}
        </button>
        <button type="button" onClick={onCancel} className="secondary" disabled={loading}>
          Cancel
        </button>
      </div>
    </form>
  );
}

export default UserForm;

