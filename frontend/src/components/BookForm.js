import React, { useState, useEffect } from 'react';
import './BookForm.css';

const initialState = {
  title: '',
  isbn: '',
  pages: '',
  publication_year: '',
  publisher: '',
  branch: '',
  available_copies: '',
};

/**
 * Reusable form for creating and editing books.
 * Keeps inputs minimal and numeric fields as numbers.
 */
function BookForm({ onSubmit, onCancel, initialData, loading }) {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (initialData) {
      setForm({
        title: initialData.title || '',
        isbn: initialData.isbn || '',
        pages: initialData.pages ?? '',
        publication_year: initialData.publication_year || '',
        publisher: initialData.publisher || '',
        branch: initialData.branch || '',
        available_copies: initialData.available_copies ?? '',
      });
    } else {
      setForm(initialState);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      pages: form.pages ? Number(form.pages) : null,
      publication_year: form.publication_year || null,
      available_copies:
        form.available_copies === '' ? null : Number(form.available_copies),
    });
  };

  return (
    <form className="book-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label>Title *</label>
          <input
            name="title"
            value={form.title}
            onChange={handleChange}
            required
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label>ISBN *</label>
          <input
            name="isbn"
            value={form.isbn}
            onChange={handleChange}
            required
            disabled={loading}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Pages</label>
          <input
            name="pages"
            type="number"
            min="1"
            value={form.pages}
            onChange={handleChange}
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label>Publication Year</label>
          <input
            name="publication_year"
            value={form.publication_year}
            onChange={handleChange}
            disabled={loading}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Publisher ID</label>
          <input
            name="publisher"
            value={form.publisher}
            onChange={handleChange}
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label>Branch ID</label>
          <input
            name="branch"
            value={form.branch}
            onChange={handleChange}
            disabled={loading}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Available Copies *</label>
          <input
            name="available_copies"
            type="number"
            min="0"
            value={form.available_copies}
            onChange={handleChange}
            required
            disabled={loading}
          />
        </div>
      </div>

      <div className="form-actions">
        <button type="submit" className="primary" disabled={loading}>
          {initialData ? 'Update Book' : 'Add Book'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="secondary"
          disabled={loading}
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

export default BookForm;
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