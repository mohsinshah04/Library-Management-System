import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import BookForm from '../components/BookForm';
import BookCard from '../components/BookCard';
import './LibrarianBooks.css';

function LibrarianBooks() {
  const [books, setBooks] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [publishers, setPublishers] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks();
    fetchAuthors();
    fetchCategories();
    fetchPublishers();
    fetchBranches();
  }, []);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get('/books/');
      setBooks(res.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to load books.';
        setError(errorMsg);
        console.error('Error loading books:', err.response?.data || err);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAuthors = async () => {
    try {
      const res = await api.get('/authors/');
      setAuthors(res.data);
    } catch (err) {
      console.error('Error fetching authors:', err);
    }
  };

  const fetchCategories = async () => {
    try {
      const res = await api.get('/categories/');
      setCategories(res.data);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const fetchPublishers = async () => {
    try {
      const res = await api.get('/publishers/');
      setPublishers(res.data);
    } catch (err) {
      console.error('Error fetching publishers:', err);
    }
  };

  const fetchBranches = async () => {
    try {
      const res = await api.get('/branches/');
      setBranches(res.data);
    } catch (err) {
      console.error('Error fetching branches:', err);
    }
  };

  const handleCreate = async (data) => {
    try {
      setSaving(true);
      await api.post('/books/', data);
      setShowForm(false);
      setEditingBook(null);
      await fetchBooks();
    } catch (err) {
      // Show detailed error messages
      const errorData = err.response?.data;
      let errorMessage = 'Failed to add book.';
      
      if (errorData) {
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else {
          // Format field-specific errors
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          errorMessage = fieldErrors || JSON.stringify(errorData);
        }
      }
      
      alert(errorMessage);
      console.error('Error creating book:', err.response?.data);
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async (data) => {
    try {
      setSaving(true);
      await api.put(`/books/${editingBook.book_id}/`, data);
      setShowForm(false);
      setEditingBook(null);
      await fetchBooks();
    } catch (err) {
      // Show detailed error messages
      const errorData = err.response?.data;
      let errorMessage = 'Failed to update book.';
      
      if (errorData) {
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else {
          // Format field-specific errors
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          errorMessage = fieldErrors || JSON.stringify(errorData);
        }
      }
      
      alert(errorMessage);
      console.error('Error updating book:', err.response?.data);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (bookId) => {
    const confirm = window.confirm('Delete this book?');
    if (!confirm) return;
    try {
      setSaving(true);
      await api.delete(`/books/${bookId}/`);
      await fetchBooks();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete book');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (book) => {
    setEditingBook(book);
    setShowForm(true);
  };

  const handleFormSubmit = (data) => {
    if (editingBook) {
      handleUpdate(data);
    } else {
      handleCreate(data);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingBook(null);
  };

  return (
    <div className="librarian-books-page">
      <div className="librarian-books-container">
        <div className="page-header">
          <div>
            <h1>📚 Manage Books</h1>
            <p className="subtitle">Add, edit, and remove library books</p>
          </div>
          <div className="header-actions">
            <button className="back-btn" onClick={() => navigate(-1)}>
              ← Back
            </button>
            <button
              className="primary-btn"
              onClick={() => {
                setShowForm(true);
                setEditingBook(null);
              }}
            >
              + Add Book
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner" />
            <p>Loading books...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <p>{error}</p>
            <button className="primary-btn" onClick={fetchBooks}>
              Retry
            </button>
          </div>
        ) : (
          <>
            {showForm && (
              <div className="form-card">
                <div className="form-card-header">
                  <h3>{editingBook ? 'Edit Book' : 'Add Book'}</h3>
                  <button className="secondary-btn" onClick={handleCancel}>
                    ✕
                  </button>
                </div>
                <BookForm
                  initialData={editingBook}
                  onSubmit={handleFormSubmit}
                  onCancel={handleCancel}
                  loading={saving}
                  authors={authors}
                  categories={categories}
                  publishers={publishers}
                  branches={branches}
                />
              </div>
            )}

            <div className="books-grid">
              {books.length === 0 ? (
                <div className="empty-state">
                  <p>No books found.</p>
                  <button
                    className="primary-btn"
                    onClick={() => {
                      setShowForm(true);
                      setEditingBook(null);
                    }}
                  >
                    Add First Book
                  </button>
                </div>
              ) : (
                books.map((book) => (
                  <div key={book.book_id} className="book-card-wrapper">
                    <BookCard book={book} showStatus={true} />
                    <div className="card-actions">
                      <button
                        className="secondary-btn"
                        onClick={() => startEdit(book)}
                        disabled={saving}
                      >
                        Edit
                      </button>
                      <button
                        className="danger-btn"
                        onClick={() => handleDelete(book.book_id)}
                        disabled={saving}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default LibrarianBooks;