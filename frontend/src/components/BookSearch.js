import React, { useState } from 'react';
import './BookSearch.css';

function BookSearch({ onSearch, onFilterChange, loading }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [availableOnly, setAvailableOnly] = useState(false);

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    onSearch(value);
  };

  const handleBranchChange = (e) => {
    const value = e.target.value;
    setBranchFilter(value);
    onFilterChange({ branch: value, availableOnly });
  };

  const handleAvailableOnlyChange = (e) => {
    const checked = e.target.checked;
    setAvailableOnly(checked);
    onFilterChange({ branch: branchFilter, availableOnly: checked });
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setBranchFilter('');
    setAvailableOnly(false);
    onSearch('');
    onFilterChange({ branch: '', availableOnly: false });
  };

  return (
    <div className="book-search-container">
      <div className="search-section">
        <div className="search-input-wrapper">
          <input
            type="text"
            placeholder="Search by title, ISBN, or author..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
            disabled={loading}
          />
          {searchTerm && (
            <button
              onClick={() => {
                setSearchTerm('');
                onSearch('');
              }}
              className="clear-search-btn"
              disabled={loading}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="branch-filter" className="filter-label">
            Branch:
          </label>
          <select
            id="branch-filter"
            value={branchFilter}
            onChange={handleBranchChange}
            className="filter-select"
            disabled={loading}
          >
            <option value="">All Branches</option>
            {/* Branches will be populated dynamically if needed */}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-checkbox-label">
            <input
              type="checkbox"
              checked={availableOnly}
              onChange={handleAvailableOnlyChange}
              className="filter-checkbox"
              disabled={loading}
            />
            <span>Available Only</span>
          </label>
        </div>

        {(searchTerm || branchFilter || availableOnly) && (
          <button
            onClick={handleClearFilters}
            className="clear-filters-btn"
            disabled={loading}
          >
            Clear Filters
          </button>
        )}
      </div>
    </div>
  );
}

export default BookSearch;

