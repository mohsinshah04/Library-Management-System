import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import BookCard from '../components/BookCard';
import BookSearch from '../components/BookSearch';
import './Books.css';

function Books() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({ branch: '', availableOnly: false });
  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks();
  }, [searchTerm, filters]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      setError('');

      // Build query parameters
      const params = new URLSearchParams();
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      if (filters.branch) {
        params.append('branch', filters.branch);
      }
      if (filters.availableOnly) {
        params.append('available_only', 'true');
      }

      const queryString = params.toString();
      const url = queryString ? `/books/?${queryString}` : '/books/';

      const response = await api.get(url);
      setBooks(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to load books. Please try again.';
        setError(errorMsg);
        console.error('Error loading books:', err.response?.data || err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="books-page">
      <div className="books-container">
        <div className="books-header">
          <h1>📚 Library Books</h1>
          <button onClick={() => navigate(-1)} className="back-btn">
            ← Back
          </button>
        </div>

        <BookSearch
          onSearch={handleSearch}
          onFilterChange={handleFilterChange}
          loading={loading}
        />

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading books...</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <div className="error-message">{error}</div>
            <button onClick={fetchBooks} className="retry-btn">
              Retry
            </button>
          </div>
        )}

        {!loading && !error && (
          <>
            {books.length === 0 ? (
              <div className="no-books-container">
                <p className="no-books-message">
                  {searchTerm || filters.branch || filters.availableOnly
                    ? 'No books found matching your criteria.'
                    : 'No books available in the library.'}
                </p>
                {(searchTerm || filters.branch || filters.availableOnly) && (
                  <button
                    onClick={() => {
                      setSearchTerm('');
                      setFilters({ branch: '', availableOnly: false });
                    }}
                    className="clear-search-btn-page"
                  >
                    Clear Search & Filters
                  </button>
                )}
              </div>
            ) : (
              <>
                <div className="books-count">
                  Found {books.length} {books.length === 1 ? 'book' : 'books'}
                </div>
                <div className="books-grid">
                  {books.map((book) => (
                    <BookCard key={book.book_id} book={book} />
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Books;

