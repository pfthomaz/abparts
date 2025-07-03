// frontend/src/components/Layout.js

import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const Layout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-md">
        <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold text-gray-800">
            ABParts
          </Link>
          <div className="flex items-center space-x-4">
            <Link to="/organizations" className="text-gray-600 hover:text-gray-800">
              Organizations
            </Link>
            <Link to="/parts" className="text-gray-600 hover:text-gray-800">
              Parts
            </Link>
            <Link to="/inventory" className="text-gray-600 hover:text-gray-800">
              Inventory
            </Link>
            <Link to="/orders" className="text-gray-600 hover:text-gray-800">
              Orders
            </Link>
            <Link to="/stocktake" className="text-gray-600 hover:text-gray-800">
              Stocktake
            </Link>
            <span className="text-gray-700">
              Welcome, <span className="font-semibold">{user.name || user.username}</span> ({user.role})
            </span>
            <button
              onClick={logout}
              className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
            >
              Logout
            </button>
          </div>
        </nav>
      </header>
      <main className="container mx-auto p-4">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
