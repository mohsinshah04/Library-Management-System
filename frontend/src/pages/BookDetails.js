import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/axiosConfig';
import './BookDetails.css';

function BookDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reserving, setReserving] = useState(false);

  useEffect(() => {
    fetchBookDetails();
  }, [id]);

  const handleReserve = async () => {
    if (!book || book.available_copies <= 0) {
      alert('This book is not available for reservation.');
      return;
    }

    const confirmReserve = window.confirm(`Reserve "${book.title}"?`);
    if (!confirmReserve) return;

    try {
      setReserving(true);
      await api.post('/reservations/', {
        book: book.book_id,
        status: 'pending'
      });
      alert('Book reserved successfully!');
      navigate('/student/reservations');
    } catch (err) {
      const status = err.response?.status;
      const errorData = err.response?.data;
      let errorMessage = 'Failed to reserve book.';

      if (errorData) {
        if (typeof errorData === 'string') {
          // If backend returned HTML, avoid dumping it in an alert
          const looksLikeHtml = errorData.trim().startsWith('<');
          errorMessage = looksLikeHtml
            ? `Failed to reserve book (status ${status || 'unknown'}).`
            : errorData;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else {
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          errorMessage = fieldErrors || JSON.stringify(errorData);
        }
      }

      alert(errorMessage);
      console.error('Error reserving book:', err.response?.data || err);
    } finally {
      setReserving(false);
    }
  };

  const fetchBookDetails = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get(`/books/${id}/`);
      setBook(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else if (err.response?.status === 404) {
        setError('Book not found.');
      } else {
        setError('Failed to load book details. Please try again.');
        console.error('Error fetching book:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="book-details-page">
        <div className="book-details-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading book details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="book-details-page">
        <div className="book-details-container">
          <div className="error-container">
            <div className="error-message">{error}</div>
            <div className="action-buttons">
              <button onClick={() => navigate(-1)} className="back-btn">
                ← Back
              </button>
              <button onClick={fetchBookDetails} className="retry-btn">
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!book) {
    return null;
  }

  const isAvailable = book.available_copies > 0;

  return (
    <div className="book-details-page">
      <div className="book-details-container">
        <div className="book-details-header">
          <button onClick={() => navigate(-1)} className="back-btn">
            ← Back to Books
          </button>
        </div>

        <div className="book-details-card">
          <div className="book-details-title-section">
            <h1>{book.title}</h1>
            <span className={`availability-badge-large ${isAvailable ? 'available' : 'unavailable'}`}>
              {isAvailable ? `${book.available_copies} Copies Available` : 'Currently Unavailable'}
            </span>
          </div>

          <div className="book-details-content">
            <div className="book-details-main">
              <div className="detail-row">
                <strong>ISBN:</strong>
                <span>{book.isbn}</span>
              </div>

              {book.publication_year && (
                <div className="detail-row">
                  <strong>Publication Year:</strong>
                  <span>{book.publication_year}</span>
                </div>
              )}

              {book.pages && (
                <div className="detail-row">
                  <strong>Pages:</strong>
                  <span>{book.pages}</span>
                </div>
              )}

              {book.publisher_name && (
                <div className="detail-row">
                  <strong>Publisher:</strong>
                  <span>{book.publisher_name}</span>
                </div>
              )}

              {book.branch_name && (
                <div className="detail-row">
                  <strong>Library Branch:</strong>
                  <span>{book.branch_name}</span>
                </div>
              )}

              {book.authors && book.authors.length > 0 && (
                <div className="detail-row">
                  <strong>Authors:</strong>
                  <span>
                    {book.authors.map((author, index) => (
                      <span key={author.author_id}>
                        {author.first_name} {author.last_name}
                        {index < book.authors.length - 1 && ', '}
                      </span>
                    ))}
                  </span>
                </div>
              )}

              {book.categories && book.categories.length > 0 && (
                <div className="detail-row">
                  <strong>Categories:</strong>
                  <span>
                    {book.categories.map((cat, index) => (
                      <span key={cat.catalog_id}>
                        {cat.category_name}
                        {index < book.categories.length - 1 && ', '}
                      </span>
                    ))}
                  </span>
                </div>
              )}

              <div className="detail-row">
                <strong>Available Copies:</strong>
                <span className={isAvailable ? 'available-text' : 'unavailable-text'}>
                  {book.available_copies}
                </span>
              </div>
            </div>
          </div>

          <div className="book-details-actions">
            {isAvailable && (
              <button 
                className="reserve-btn"
                onClick={handleReserve}
                disabled={reserving}
              >
                {reserving ? 'Reserving...' : 'Reserve This Book'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BookDetails;

