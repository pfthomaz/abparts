// frontend/src/AuthContext.js

import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { authService } from './services/authService';

// Create Auth Context
const AuthContext = createContext(null);

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  // Function to log in a user
  const login = async (username, password) => {
    try {
      const data = await authService.login(username, password);
      localStorage.setItem('authToken', data.access_token);
      setToken(data.access_token);
      return true; // Indicate successful login
    } catch (error) {
      console.error("Login failed:", error);
      localStorage.removeItem('authToken');
      throw error; // Re-throw to be caught by login form
    }
  };

  // Function to log out a user
  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
  }, []);

  // Effect to fetch user details when token changes
  useEffect(() => {
    const fetchUser = async () => {
      setLoadingUser(true);
      if (token) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          // The api client throws an error on non-ok responses, which we catch here.
          // This is expected if the token is expired or invalid.
          console.error("Failed to fetch user details, logging out:", error.message);
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
  }, [token, logout]);

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
