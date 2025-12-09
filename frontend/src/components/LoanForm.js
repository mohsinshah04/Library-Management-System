import React, { useState, useEffect } from 'react';
import './LoanForm.css';

function LoanForm({ onSubmit, onCancel, loading, books = [], users = [] }) {
  const [form, setForm] = useState({
    user: '',
    book: '',
    due_date: '',
  });

  // Calculate default due date (14 days from now)
  useEffect(() => {
    const today = new Date();
    const dueDate = new Date(today);
    dueDate.setDate(today.getDate() + 14); // 14 days from now
    const formattedDate = dueDate.toISOString().split('T')[0];
    setForm(prev => ({ ...prev, due_date: formattedDate }));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      user: Number(form.user),
      book: Number(form.book),
      due_date: form.due_date,
    });
  };

  return (
    <form className="loan-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label>Student *</label>
          <select
            name="user"
            value={form.user}
            onChange={handleChange}
            required
            disabled={loading}
            className="form-select"
          >
            <option value="">Select a student...</option>
            {users.map((user) => (
              <option key={user.user_id} value={user.user_id}>
                {user.first_name} {user.last_name} ({user.username})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Book *</label>
          <select
            name="book"
            value={form.book}
            onChange={handleChange}
            required
            disabled={loading}
            className="form-select"
          >
            <option value="">Select a book...</option>
            {books
              .filter(book => book.available_copies > 0)
              .map((book) => (
                <option key={book.book_id} value={book.book_id}>
                  {book.title} (ISBN: {book.isbn}) - {book.available_copies} available
                </option>
              ))}
          </select>
          {books.filter(book => book.available_copies > 0).length === 0 && (
            <p className="form-hint">No books available for loan</p>
          )}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Due Date *</label>
          <input
            name="due_date"
            type="date"
            value={form.due_date}
            onChange={handleChange}
            required
            disabled={loading}
            min={new Date().toISOString().split('T')[0]}
          />
          <p className="form-hint">Default: 14 days from today</p>
        </div>
      </div>

      <div className="form-actions">
        <button type="submit" className="primary" disabled={loading}>
          Issue Loan
        </button>
        <button type="button" onClick={onCancel} className="secondary" disabled={loading}>
          Cancel
        </button>
      </div>
    </form>
  );
}

export default LoanForm;

