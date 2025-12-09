import React, { useState, useEffect } from 'react';
import './LoanForm.css';

function LoanForm({ onSubmit, onCancel, loading, books = [], users = [] }) {
  const [form, setForm] = useState({
    user: '',
    book: '',
    due_date: '',
  });
  const [studentSearch, setStudentSearch] = useState('');
  const [bookSearch, setBookSearch] = useState('');

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

  // Filter students by search term (name or email)
  const filteredUsers = users.filter(user => {
    if (!studentSearch) return true;
    const searchLower = studentSearch.toLowerCase();
    const fullName = `${user.first_name} ${user.last_name}`.toLowerCase();
    const email = (user.email || '').toLowerCase();
    const username = (user.username || '').toLowerCase();
    return fullName.includes(searchLower) || 
           email.includes(searchLower) || 
           username.includes(searchLower);
  });

  // Filter books by search term (title or ISBN)
  const filteredBooks = books.filter(book => {
    if (!bookSearch) return true;
    const searchLower = bookSearch.toLowerCase();
    const title = (book.title || '').toLowerCase();
    const isbn = (book.isbn || '').toLowerCase();
    return title.includes(searchLower) || isbn.includes(searchLower);
  });

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
          <input
            type="text"
            placeholder="Search by name or email..."
            value={studentSearch}
            onChange={(e) => setStudentSearch(e.target.value)}
            className="search-input"
            disabled={loading}
          />
          <select
            name="user"
            value={form.user}
            onChange={handleChange}
            required
            disabled={loading}
            className="form-select"
          >
            <option value="">Select a student...</option>
            {filteredUsers.map((user) => (
              <option key={user.user_id} value={user.user_id}>
                {user.first_name} {user.last_name} ({user.username}) - {user.email}
              </option>
            ))}
          </select>
          {studentSearch && filteredUsers.length === 0 && (
            <p className="form-hint">No students found matching "{studentSearch}"</p>
          )}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Book *</label>
          <input
            type="text"
            placeholder="Search by title or ISBN..."
            value={bookSearch}
            onChange={(e) => setBookSearch(e.target.value)}
            className="search-input"
            disabled={loading}
          />
          <select
            name="book"
            value={form.book}
            onChange={handleChange}
            required
            disabled={loading}
            className="form-select"
          >
            <option value="">Select a book...</option>
            {filteredBooks
              .filter(book => book.available_copies > 0)
              .map((book) => (
                <option key={book.book_id} value={book.book_id}>
                  {book.title} (ISBN: {book.isbn}) - {book.available_copies} available
                </option>
              ))}
          </select>
          {bookSearch && filteredBooks.filter(book => book.available_copies > 0).length === 0 && (
            <p className="form-hint">No available books found matching "{bookSearch}"</p>
          )}
          {!bookSearch && filteredBooks.filter(book => book.available_copies > 0).length === 0 && (
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

