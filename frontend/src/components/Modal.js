// frontend/src/components/Modal.js

import React from 'react';

function Modal({ show, onClose, title, children }) {
  if (!show) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
      <div className="relative bg-white p-8 rounded-lg shadow-xl max-w-lg mx-auto my-10 overflow-hidden">
        <div className="flex justify-between items-center pb-3 border-b border-gray-200 mb-4">
          <h3 className="text-2xl font-bold text-gray-800">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-3xl font-light leading-none focus:outline-none"
            aria-label="Close"
          >
            &times;
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto pr-2"> {/* Added max-height and overflow for scrollability */}
          {children}
        </div>
      </div>
    </div>
  );
}

export default Modal;
