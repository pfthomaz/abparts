// frontend/src/App.js

import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import './index.css'; // Import Tailwind CSS base styles
import { useAuth } from './AuthContext'; // Import useAuth hook
import LoginForm from './components/LoginForm'; // Import LoginForm component
import Layout from './components/Layout'; // Import Layout component
import Dashboard from './pages/Dashboard';
import Organizations from './pages/Organizations';
import Parts from './pages/Parts';
import Inventory from './pages/Inventory';
import Orders from './pages/Orders';
import Stocktake from './pages/Stocktake';

function App() {
  const { token, loadingUser } = useAuth();

  if (loadingUser) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <p className="text-xl text-gray-700">Checking authentication...</p>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={!token ? <LoginForm /> : <Navigate to="/" />}
        />
        <Route
          path="/*"
          element={token ? <Layout /> : <Navigate to="/login" />}
        >
          <Route index element={<Dashboard />} />
          <Route path="organizations" element={<Organizations />} />
          <Route path="parts" element={<Parts />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="orders" element={<Orders />} />
          <Route path="stocktake" element={<Stocktake />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
