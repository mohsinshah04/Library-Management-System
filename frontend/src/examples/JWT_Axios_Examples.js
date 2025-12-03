/**
 * JWT and Axios - Practical Code Examples
 * 
 * This file contains practical examples showing how JWT and Axios work together.
 * You can reference these examples when building your app.
 */

import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// ============================================================================
// EXAMPLE 1: Basic Login (What we have in Login.js)
// ============================================================================

export async function example1_Login() {
  try {
    // Step 1: Send credentials to backend
    const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
      username: 'john_doe',
      password: 'password123'
    });

    // Step 2: Backend returns tokens and user data
    const { tokens, user } = response.data;
    // tokens = { access: "...", refresh: "..." }
    // user = { id: 1, username: "john_doe", role: "student", ... }

    // Step 3: Store tokens in localStorage
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    console.log('Login successful!', user);
    return { success: true, user };
  } catch (error) {
    // Handle errors
    if (error.response) {
      // Server responded with error (400, 401, 500, etc.)
      console.error('Login failed:', error.response.data);
      return { success: false, error: error.response.data.message };
    } else if (error.request) {
      // Request sent but no response (network error)
      console.error('Network error:', error.request);
      return { success: false, error: 'Network error. Is backend running?' };
    } else {
      // Something else went wrong
      console.error('Error:', error.message);
      return { success: false, error: error.message };
    }
  }
}

// ============================================================================
// EXAMPLE 2: Making Protected API Request (With Token)
// ============================================================================

export async function example2_GetCurrentUser() {
  try {
    // Step 1: Get token from localStorage
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No token found. Please login first.');
    }

    // Step 2: Make request with token in Authorization header
    const response = await axios.get(`${API_BASE_URL}/auth/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    // Step 3: Backend verifies token and returns user data
    const user = response.data;
    console.log('Current user:', user);
    return { success: true, user };
  } catch (error) {
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.error('Token expired. Need to refresh or login again.');
      return { success: false, error: 'Token expired', needsRefresh: true };
    }
    console.error('Error getting user:', error);
    return { success: false, error: error.message };
  }
}

// ============================================================================
// EXAMPLE 3: Refresh Token When Access Token Expires
// ============================================================================

export async function example3_RefreshToken() {
  try {
    // Step 1: Get refresh token from localStorage
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No refresh token found. Please login again.');
    }

    // Step 2: Request new access token
    const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
      refresh: refreshToken
    });

    // Step 3: Backend returns new access token
    const newAccessToken = response.data.access;

    // Step 4: Save new access token
    localStorage.setItem('access_token', newAccessToken);

    console.log('Token refreshed successfully!');
    return { success: true, accessToken: newAccessToken };
  } catch (error) {
    if (error.response?.status === 401) {
      // Refresh token also expired - user needs to login again
      console.error('Refresh token expired. User must login again.');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      return { success: false, error: 'Session expired. Please login again.', needsLogin: true };
    }
    console.error('Error refreshing token:', error);
    return { success: false, error: error.message };
  }
}

// ============================================================================
// EXAMPLE 4: Automatic Token Refresh (Smart Request Function)
// ============================================================================

/**
 * This function automatically refreshes the token if it expires.
 * Use this for all protected API calls.
 */
export async function example4_SmartRequest(method, url, data = null) {
  try {
    // Step 1: Get access token
    let token = localStorage.getItem('access_token');

    // Step 2: Make request with token
    const config = {
      method: method,
      url: `${API_BASE_URL}${url}`,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };

    if (data) {
      config.data = data;
    }

    const response = await axios(config);
    return { success: true, data: response.data };
  } catch (error) {
    // Step 3: If token expired (401), refresh it
    if (error.response?.status === 401) {
      console.log('Token expired. Refreshing...');
      
      const refreshResult = await example3_RefreshToken();
      
      if (refreshResult.success) {
        // Step 4: Retry original request with new token
        console.log('Retrying request with new token...');
        const newToken = localStorage.getItem('access_token');
        
        const retryConfig = {
          method: method,
          url: `${API_BASE_URL}${url}`,
          headers: {
            'Authorization': `Bearer ${newToken}`
          }
        };

        if (data) {
          retryConfig.data = data;
        }

        const retryResponse = await axios(retryConfig);
        return { success: true, data: retryResponse.data };
      } else {
        // Refresh failed - redirect to login
        return { success: false, error: 'Session expired', needsLogin: true };
      }
    }
    
    // Other errors
    return { success: false, error: error.response?.data || error.message };
  }
}

// Usage:
// const result = await example4_SmartRequest('GET', '/auth/me/');
// const result = await example4_SmartRequest('POST', '/books/', { title: 'New Book' });

// ============================================================================
// EXAMPLE 5: Axios Interceptor (Advanced - Automatic Token Injection)
// ============================================================================

/**
 * Axios interceptor automatically adds token to all requests.
 * Set this up once in your App.js or index.js
 */
export function example5_SetupAxiosInterceptor() {
  // Request interceptor: Add token to all requests
  axios.interceptors.request.use(
    (config) => {
      // Get token from localStorage
      const token = localStorage.getItem('access_token');
      
      // Add token to Authorization header if it exists
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor: Handle token expiration
  axios.interceptors.response.use(
    (response) => {
      // If request succeeds, just return the response
      return response;
    },
    async (error) => {
      const originalRequest = error.config;

      // If error is 401 and we haven't tried to refresh yet
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          });

          // Save new access token
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return axios(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );
}

// Usage: Call this once in App.js:
// import { example5_SetupAxiosInterceptor } from './examples/JWT_Axios_Examples';
// example5_SetupAxiosInterceptor();
// Now all axios requests automatically include the token!

// ============================================================================
// EXAMPLE 6: Register New User
// ============================================================================

export async function example6_Register() {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/register/`, {
      username: 'newuser',
      email: 'newuser@example.com',
      password: 'password123',
      password_confirm: 'password123',
      role: 'student',  // or 'librarian'
      first_name: 'New',
      last_name: 'User'
    });

    // Registration also returns tokens, so user is automatically logged in
    const { tokens, user } = response.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    console.log('Registration successful!', user);
    return { success: true, user };
  } catch (error) {
    if (error.response) {
      // Validation errors (passwords don't match, username taken, etc.)
      console.error('Registration failed:', error.response.data);
      return { success: false, errors: error.response.data };
    }
    console.error('Error:', error);
    return { success: false, error: error.message };
  }
}

// ============================================================================
// EXAMPLE 7: Logout
// ============================================================================

export function example7_Logout() {
  // Simply remove tokens from localStorage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  
  console.log('Logged out successfully');
  // Redirect to login page (handled by your router)
}

// ============================================================================
// EXAMPLE 8: Check if User is Logged In
// ============================================================================

export function example8_IsLoggedIn() {
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');
  
  if (token && user) {
    try {
      const userData = JSON.parse(user);
      return { isLoggedIn: true, user: userData };
    } catch (e) {
      return { isLoggedIn: false };
    }
  }
  
  return { isLoggedIn: false };
}

// ============================================================================
// SUMMARY: How to Use These Examples
// ============================================================================

/*
1. Basic Login:
   const result = await example1_Login();
   if (result.success) { navigate('/dashboard'); }

2. Get Current User:
   const result = await example2_GetCurrentUser();
   if (result.success) { console.log(result.user); }

3. Refresh Token:
   const result = await example3_RefreshToken();
   if (result.success) { console.log('Token refreshed!'); }

4. Smart Request (auto-refresh):
   const result = await example4_SmartRequest('GET', '/auth/me/');

5. Setup Interceptor (once in App.js):
   example5_SetupAxiosInterceptor();
   // Now all axios requests automatically include token!

6. Register:
   const result = await example6_Register();

7. Logout:
   example7_Logout();

8. Check Login Status:
   const { isLoggedIn, user } = example8_IsLoggedIn();
*/



