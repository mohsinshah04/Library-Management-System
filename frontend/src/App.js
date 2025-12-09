import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import LibrarianDashboard from './pages/LibrarianDashboard';
import Books from './pages/Books';
import BookDetails from './pages/BookDetails';
import LibrarianBooks from './pages/LibrarianBooks';
import StudentLoans from './pages/StudentLoans';
import LibrarianLoans from './pages/LibrarianLoans';
import StudentReservations from './pages/StudentReservations';
import LibrarianReservations from './pages/LibrarianReservations';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes - require authentication */}
          <Route 
            path="/student/dashboard" 
            element={
              <ProtectedRoute role="student">
                <StudentDashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/librarian/dashboard" 
            element={
              <ProtectedRoute role="librarian">
                <LibrarianDashboard />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/librarian/books" 
            element={
              <ProtectedRoute role="librarian">
                <LibrarianBooks />
              </ProtectedRoute>
            } 
          />
          
          {/* Books routes - accessible to authenticated users */}
          <Route 
            path="/books" 
            element={
              <ProtectedRoute>
                <Books />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/books/:id" 
            element={
              <ProtectedRoute>
                <BookDetails />
              </ProtectedRoute>
            } 
          />
          
          {/* Student Loans */}
          <Route 
            path="/student/loans" 
            element={
              <ProtectedRoute role="student">
                <StudentLoans />
              </ProtectedRoute>
            } 
          />
          
          {/* Librarian Loans */}
          <Route 
            path="/librarian/loans" 
            element={
              <ProtectedRoute role="librarian">
                <LibrarianLoans />
              </ProtectedRoute>
            } 
          />
          
          {/* Student Reservations */}
          <Route 
            path="/student/reservations" 
            element={
              <ProtectedRoute role="student">
                <StudentReservations />
              </ProtectedRoute>
            } 
          />
          
          {/* Librarian Reservations */}
          <Route 
            path="/librarian/reservations" 
            element={
              <ProtectedRoute role="librarian">
                <LibrarianReservations />
              </ProtectedRoute>
            } 
          />
          
          {/* Default route - redirect to login */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* Catch all - redirect to login */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

