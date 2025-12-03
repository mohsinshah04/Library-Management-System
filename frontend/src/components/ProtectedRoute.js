import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute Component
 * 
 * Protects routes that require authentication.
 * If user is not logged in, redirects to login page.
 * If user is logged in but wrong role, redirects to appropriate dashboard.
 * 
 * Usage:
 * <ProtectedRoute role="student">
 *   <StudentDashboard />
 * </ProtectedRoute>
 */
function ProtectedRoute({ children, role = null }) {
  // Check if user is logged in
  const token = localStorage.getItem('access_token');
  const userStr = localStorage.getItem('user');

  // If no token, redirect to login
  if (!token || !userStr) {
    return <Navigate to="/login" replace />;
  }

  try {
    const user = JSON.parse(userStr);

    // If role is specified, check if user has the correct role
    if (role && user.role !== role) {
      // Redirect to appropriate dashboard based on user's role
      if (user.role === 'student') {
        return <Navigate to="/student/dashboard" replace />;
      } else if (user.role === 'librarian') {
        return <Navigate to="/librarian/dashboard" replace />;
      }
    }

    // User is authenticated and has correct role (if required)
    return children;
  } catch (error) {
    // Invalid user data, redirect to login
    console.error('Error parsing user data:', error);
    return <Navigate to="/login" replace />;
  }
}

export default ProtectedRoute;

