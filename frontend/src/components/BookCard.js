import React from 'react';
import { Link } from 'react-router-dom';
import './BookCard.css';

function BookCard({ book, showStatus = false }) {
  const isAvailable = book.available_copies > 0;
  const status = book.status || (isAvailable ? 'available' : 'out on loan');
  
  return (
    <div className="book-card">
      <div className="book-card-header">
        <h3 className="book-title">{book.title}</h3>
        <div className="badge-group">
          <span className={`availability-badge ${isAvailable ? 'available' : 'unavailable'}`}>
            {isAvailable ? `${book.available_copies} Available` : 'Unavailable'}
          </span>
          {showStatus && (
            <span className={`status-badge ${status === 'available' ? 'status-available' : 'status-loan'}`}>
              {status === 'available' ? 'Available' : 'Out on Loan'}
            </span>
          )}
        </div>
      </div>
      
      <div className="book-card-body">
        <div className="book-info">
          <p className="book-isbn">
            <strong>ISBN:</strong> {book.isbn}
          </p>
          
          {book.publication_year && (
            <p className="book-year">
              <strong>Year:</strong> {book.publication_year}
            </p>
          )}
          
          {book.pages && (
            <p className="book-pages">
              <strong>Pages:</strong> {book.pages}
            </p>
          )}
          
          {book.publisher_name && (
            <p className="book-publisher">
              <strong>Publisher:</strong> {book.publisher_name}
            </p>
          )}
          
          {book.branch_name && (
            <p className="book-branch">
              <strong>Branch:</strong> {book.branch_name}
            </p>
          )}
          
          {book.authors && book.authors.length > 0 && (
            <p className="book-authors">
              <strong>Authors:</strong>{' '}
              {book.authors.map(author => `${author.first_name} ${author.last_name}`).join(', ')}
            </p>
          )}
          
          {book.categories && book.categories.length > 0 && (
            <p className="book-categories">
              <strong>Categories:</strong>{' '}
              {book.categories.map(cat => cat.category_name).join(', ')}
            </p>
          )}
        </div>
      </div>
      
      <div className="book-card-footer">
        <Link to={`/books/${book.book_id}`} className="view-details-btn">
          View Details
        </Link>
      </div>
    </div>
  );
}

export default BookCard;

