// frontend/src/index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Your Tailwind CSS output
import App from './App';
import { AuthProvider } from './AuthContext'; // Import AuthProvider
import { PWAProvider } from './contexts/PWAContext'; // Import PWAProvider
import * as serviceWorkerRegistration from './utils/serviceWorkerRegistration';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
    <AuthProvider> {/* Wrap App with AuthProvider */}
        <PWAProvider> {/* Wrap with PWAProvider for offline support */}
            <App />
        </PWAProvider>
    </AuthProvider>
    </React.StrictMode>
);

// Register service worker for PWA features (production only)
if (process.env.NODE_ENV === 'production') {
    serviceWorkerRegistration.register({
        onSuccess: () => {
            // console.log('[App] Service worker registered successfully');
        },
        onUpdate: (registration) => {
            // console.log('[App] New version available');
            // The PWAUpdateNotification component will handle showing the update prompt
        }
    });
} else {
    console.log('[App] Service worker disabled in development mode');
    // Unregister any existing service workers in development
    serviceWorkerRegistration.unregister();
}
