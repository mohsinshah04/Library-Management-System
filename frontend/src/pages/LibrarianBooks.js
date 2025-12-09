import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import BookForm from '../components/BookForm';
import BookCard from '../components/BookCard';
import './LibrarianBooks.css';

function LibrarianBooks() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks();
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
        setError('Failed to load books.');
        console.error(err);
      }
    } finally {
      setLoading(false);
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
      alert(err.response?.data?.detail || 'Failed to add book');
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
      alert(err.response?.data?.detail || 'Failed to update book');
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
                    <BookCard book={book} />
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
{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}