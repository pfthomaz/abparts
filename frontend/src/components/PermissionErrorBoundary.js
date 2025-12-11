// frontend/src/components/PermissionErrorBoundary.js

import React from 'react';
import PermissionDenied from './PermissionDenied';

/**
 * Error boundary specifically for permission-related errors
 * Catches and handles authorization errors gracefully
 */
class PermissionErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      isPermissionError: false
    };
  }

  static getDerivedStateFromError(error) {
    // Check if this is a permission-related error
    const isPermissionError =
      error.message?.includes('permission') ||
      error.message?.includes('unauthorized') ||
      error.message?.includes('forbidden') ||
      error.status === 403 ||
      error.status === 401;

    return {
      hasError: true,
      isPermissionError
    };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log permission errors for monitoring
    if (this.state.isPermissionError) {
      console.warn('Permission Error Boundary caught:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        feature: this.props.feature,
        requiredPermission: this.props.requiredPermission
      });
    }
  }

  render() {
    if (this.state.hasError) {
      // If it's a permission error, show the permission denied component
      if (this.state.isPermissionError) {
        return (
          <PermissionDenied
            message={this.props.permissionErrorMessage}
            feature={this.props.feature}
            requiredRole={this.props.requiredRole}
            requiredPermissions={this.props.requiredPermission ? [this.props.requiredPermission] : []}
            resource={this.props.resource}
            action={this.props.action}
            isInline={this.props.inline}
          />
        );
      }

      // For other errors, show a generic error fallback
      return this.props.fallback || (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Something went wrong
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  {this.state.error?.message || 'An unexpected error occurred while loading this feature.'}
                </p>
                {process.env.NODE_ENV === 'development' && (
                  <details className="mt-2">
                    <summary className="cursor-pointer font-medium">Error Details (Development)</summary>
                    <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-auto">
                      {this.state.error?.stack}
                    </pre>
                  </details>
                )}
              </div>
              <div className="mt-4">
                <button
                  onClick={() => window.location.reload()}
                  className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Reload Page
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component for wrapping components with permission error boundary
 */
export const withPermissionErrorBoundary = (WrappedComponent, options = {}) => {
  return function PermissionBoundaryWrapper(props) {
    return (
      <PermissionErrorBoundary
        feature={options.feature}
        requiredPermission={options.requiredPermission}
        requiredRole={options.requiredRole}
        resource={options.resource}
        action={options.action}
        permissionErrorMessage={options.permissionErrorMessage}
        inline={options.inline}
        fallback={options.fallback}
      >
        <WrappedComponent {...props} />
      </PermissionErrorBoundary>
    );
  };
};

/**
 * Hook for handling permission errors in functional components
 */
export const usePermissionErrorHandler = () => {
  const handlePermissionError = (error, context = {}) => {
    if (error.status === 403 || error.status === 401) {
      // Permission error - could trigger a modal or redirect
      console.warn('Permission error:', error.message, context);

      // You could dispatch an action to show a global permission error modal
      // or redirect to a permission denied page

      return {
        isPermissionError: true,
        shouldShowModal: true,
        errorMessage: error.message
      };
    }

    return {
      isPermissionError: false,
      shouldShowModal: false,
      errorMessage: error.message
    };
  };

  return { handlePermissionError };
};

export default PermissionErrorBoundary;