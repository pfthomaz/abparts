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
      // CRITICAL FIX: Clear old token and user data BEFORE login
      // This prevents race conditions where old token is used
      setToken(null);
      setUser(null);
      localStorage.removeItem('authToken');
      localStorage.removeItem('token');
      
      // Now perform the login
      const data = await authService.login(username, password);
      localStorage.setItem('authToken', data.access_token);
      // Clear the reminder check flag for fresh login
      sessionStorage.removeItem('hasCheckedReminders');
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
    
    // Clear all authentication and user-specific data from localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('token'); // ChatWidget uses this
    localStorage.removeItem('selectedOrganizationId'); // OrganizationContext
    localStorage.removeItem('localizationPreferences'); // LocalizationContext
    
    // Clear session storage completely
    sessionStorage.clear();
    
    // Force a hard reload to clear any cached React state
    // This is especially important in production builds to prevent
    // the previous user's data from appearing after logout
    window.location.href = '/';
  }, []);

  // Function to refresh user data (useful after profile/logo updates)
  const refreshUser = useCallback(async () => {
    if (token) {
      try {
        const userData = await authService.getCurrentUser();
        
        // Fetch organization separately if not included
        if (userData.organization_id && !userData.organization) {
          try {
            const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}/organizations/${userData.organization_id}`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            if (response.ok) {
              const orgData = await response.json();
              userData.organization = orgData;
            }
          } catch (orgError) {
            console.error("Failed to fetch organization:", orgError);
          }
        }
        
        setUser(userData);
      } catch (error) {
        console.error("Failed to refresh user details:", error);
      }
    }
  }, [token]);

  // Effect to fetch user details when token changes
  useEffect(() => {
    const fetchUser = async () => {
      setLoadingUser(true);
      if (token) {
        try {
          const userData = await authService.getCurrentUser();
          
          // Fetch organization separately if not included
          if (userData.organization_id && !userData.organization) {
            try {
              const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}/organizations/${userData.organization_id}`, {
                headers: {
                  'Authorization': `Bearer ${token}`
                }
              });
              if (response.ok) {
                const orgData = await response.json();
                userData.organization = orgData;
              }
            } catch (orgError) {
              console.error("Failed to fetch organization:", orgError);
            }
          }
          
          setUser(userData);
          
          // Preload offline data after successful login
          // This runs in the background and doesn't block the UI
          if (navigator.onLine) {
            import('./services/offlineDataPreloader').then(({ preloadOfflineData }) => {
              preloadOfflineData(userData).catch(error => {
                console.error('[Auth] Offline data preload failed:', error);
              });
            });
          }
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
    <AuthContext.Provider value={{ token, user, login, logout, loadingUser, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the Auth Context
export const useAuth = () => {
  return useContext(AuthContext);
};
