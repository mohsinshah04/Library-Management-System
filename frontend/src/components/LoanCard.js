import React from 'react';
import './LoanCard.css';

function LoanCard({ loan, onReturn, showReturnButton = false, isLibrarian = false }) {
  const isOverdue = loan.is_overdue;
  const isReturned = loan.return_date !== null;
  
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <div className={`loan-card ${isOverdue ? 'overdue' : ''} ${isReturned ? 'returned' : ''}`}>
      <div className="loan-card-header">
        <h3 className="loan-book-title">{loan.book_title}</h3>
        {isOverdue && !isReturned && (
          <span className="overdue-badge">Overdue</span>
        )}
        {isReturned && (
          <span className="returned-badge">Returned</span>
        )}
      </div>
      
      <div className="loan-card-body">
        <div className="loan-info">
          <p className="loan-isbn">
            <strong>ISBN:</strong> {loan.book_isbn}
          </p>
          
          {isLibrarian && (
            <p className="loan-user">
              <strong>Borrower:</strong> {loan.user_name}
            </p>
          )}
          
          <p className="loan-date">
            <strong>Loan Date:</strong> {formatDate(loan.loan_date)}
          </p>
          
          <p className={`due-date ${isOverdue && !isReturned ? 'overdue-text' : ''}`}>
            <strong>Due Date:</strong> {formatDate(loan.due_date)}
          </p>
          
          {isReturned && (
            <p className="return-date">
              <strong>Returned:</strong> {formatDate(loan.return_date)}
            </p>
          )}
        </div>
      </div>
      
      {showReturnButton && !isReturned && (
        <div className="loan-card-footer">
          <button 
            onClick={() => onReturn(loan.loan_id)} 
            className="return-btn"
          >
            Return Book
          </button>
        </div>
      )}
    </div>
  );
}

export default LoanCard;

