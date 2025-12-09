import React, { useState, useEffect } from 'react';
import './BookForm.css';

const initialState = {
  title: '',
  isbn: '',
  pages: '',
  publication_year: '',
  description: '',
  publisher: '',
  branch: '',
  available_copies: '',
  authors: [],
  categories: [],
};

/**
 * Reusable form for creating and editing books.
 * Keeps inputs minimal and numeric fields as numbers.
 */
function BookForm({ onSubmit, onCancel, initialData, loading, authors = [], categories = [], publishers = [], branches = [] }) {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (initialData) {
      setForm({
        title: initialData.title || '',
        isbn: initialData.isbn || '',
        pages: initialData.pages ?? '',
        publication_year: initialData.publication_year || '',
        description: initialData.description || '',
        publisher: initialData.publisher || '',
        branch: initialData.branch || '',
        available_copies: initialData.available_copies ?? '',
        authors: initialData.authors ? initialData.authors.map(a => a.author_id) : [],
        categories: initialData.categories ? initialData.categories.map(c => c.catalog_id) : [],
      });
    } else {
      setForm(initialState);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleMultiSelectChange = (e) => {
    const { name } = e.target;
    const selectedOptions = Array.from(e.target.selectedOptions, option => parseInt(option.value));
    setForm((prev) => ({ ...prev, [name]: selectedOptions }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      title: form.title,
      isbn: form.isbn,
      pages: form.pages ? Number(form.pages) : null,
      publication_year: form.publication_year || null,
      description: form.description || null,
      available_copies: form.available_copies === '' ? 0 : Number(form.available_copies),
    };
    
    // Only include publisher and branch if they have values
    if (form.publisher && form.publisher.trim() !== '') {
      submitData.publisher = Number(form.publisher);
    }
    
    if (form.branch && form.branch.trim() !== '') {
      submitData.branch = Number(form.branch);
    }
    
    // Include authors and categories
    if (form.authors && form.authors.length > 0) {
      submitData.authors = form.authors;
    }
    
    if (form.categories && form.categories.length > 0) {
      submitData.categories = form.categories;
    }
    
    onSubmit(submitData);
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
          <label>Publisher</label>
          <select
            name="publisher"
            value={form.publisher}
            onChange={handleChange}
            disabled={loading}
          >
            <option value="">Select a publisher...</option>
            {publishers.map((publisher) => (
              <option key={publisher.publisher_id} value={publisher.publisher_id}>
                {publisher.name}
              </option>
            ))}
          </select>
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
                {branch.branch_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Authors</label>
          <select
            name="authors"
            multiple
            value={form.authors.map(String)}
            onChange={handleMultiSelectChange}
            disabled={loading}
            className="multi-select"
            size="4"
          >
            {authors.map((author) => (
              <option key={author.author_id} value={author.author_id}>
                {author.first_name} {author.last_name}
              </option>
            ))}
          </select>
          <p className="form-hint">Hold Ctrl/Cmd to select multiple authors</p>
        </div>
        <div className="form-group">
          <label>Categories/Genres</label>
          <select
            name="categories"
            multiple
            value={form.categories.map(String)}
            onChange={handleMultiSelectChange}
            disabled={loading}
            className="multi-select"
            size="4"
          >
            {categories.map((category) => (
              <option key={category.catalog_id} value={category.catalog_id}>
                {category.category_name}
              </option>
            ))}
          </select>
          <p className="form-hint">Hold Ctrl/Cmd to select multiple categories</p>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group full-width">
          <label>Description</label>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            disabled={loading}
            rows="4"
            placeholder="Enter book description..."
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
