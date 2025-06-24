// frontend/src/AuthContext.js

import React, { createContext, useState, useContext, useEffect } from 'react';

// Create Auth Context
const AuthContext = createContext(null);

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  // Function to log in a user
  const login = async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL}/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      localStorage.setItem('authToken', data.access_token);
      setToken(data.access_token);
      return true; // Indicate successful login
    } catch (error) {
      console.error("Login failed:", error);
      setToken(null); // Ensure token is cleared on failed login
      localStorage.removeItem('authToken');
      throw error; // Re-throw to be caught by login form
    }
  };

  // Function to log out a user
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
  };

  // Effect to fetch user details when token changes
  useEffect(() => {
    const fetchUser = async () => {
      setLoadingUser(true);
      if (token) {
        try {
          const response = await fetch(`${API_BASE_URL}/users/me/`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            // If token is invalid or expired, log out
            console.error("Failed to fetch user details, token might be invalid/expired.");
            logout();
            return;
          }
          const userData = await response.json();
          setUser(userData);
        } catch (error) {
          console.error("Error fetching user details:", error);
          logout(); // Log out on any fetch error
        } finally {
          setLoadingUser(false);
        }
      } else {
        setUser(null);
        setLoadingUser(false);
      }
    };

    fetchUser();
  }, [token, API_BASE_URL]);

  return (
    <AuthContext.Provider value={{ token, user, login, logout, loadingUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the Auth Context
export const useAuth = () => {
  return useContext(AuthContext);
};
