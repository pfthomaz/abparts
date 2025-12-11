// frontend/src/components/PartSearchSelector.js

import React, { useState, useMemo, useRef, useEffect } from 'react';

/**
 * Searchable part selector component
 * Searches across part_number, manufacturer_part_number, name (all languages), and description
 */
const PartSearchSelector = ({ 
  parts = [], 
  value, 
  onChange, 
  disabled = false,
  placeholder = "Search by code, name, or description...",
  className = ""
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const wrapperRef = useRef(null);
  const inputRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter parts based on search term
  const filteredParts = useMemo(() => {
    if (!searchTerm.trim()) return parts;

    const search = searchTerm.toLowerCase().trim();
    
    return parts.filter(part => {
      // Search in part_number
      if (part.part_number?.toLowerCase().includes(search)) return true;
      
      // Search in manufacturer_part_number
      if (part.manufacturer_part_number?.toLowerCase().includes(search)) return true;
      
      // Search in name (supports multilingual - searches the entire name field)
      if (part.name?.toLowerCase().includes(search)) return true;
      
      // Search in description
      if (part.description?.toLowerCase().includes(search)) return true;
      
      return false;
    });
  }, [parts, searchTerm]);

  // Get selected part details
  const selectedPart = useMemo(() => {
    return parts.find(p => p.id === value);
  }, [parts, value]);

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown') {
        setIsOpen(true);
        e.preventDefault();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < filteredParts.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : 0);
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredParts[highlightedIndex]) {
          handleSelect(filteredParts[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        break;
      default:
        break;
    }
  };

  const handleSelect = (part) => {
    onChange(part.id);
    setSearchTerm('');
    setIsOpen(false);
    setHighlightedIndex(0);
  };

  const handleClear = () => {
    onChange('');
    setSearchTerm('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value);
    setIsOpen(true);
    setHighlightedIndex(0);
  };

  const displayValue = selectedPart 
    ? `${selectedPart.part_number} - ${selectedPart.name}`
    : '';

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      {/* Display selected part or search input */}
      {selectedPart && !isOpen ? (
        <div className="flex items-center">
          <div className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white">
            <div className="font-medium text-gray-900">{selectedPart.part_number}</div>
            <div className="text-sm text-gray-600">{selectedPart.name}</div>
          </div>
          <button
            type="button"
            onClick={handleClear}
            disabled={disabled}
            className="ml-2 px-3 py-2 text-red-600 hover:text-red-800 font-semibold disabled:opacity-50"
          >
            Clear
          </button>
        </div>
      ) : (
        <input
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
        />
      )}

      {/* Dropdown list */}
      {isOpen && !disabled && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
          {filteredParts.length === 0 ? (
            <div className="px-3 py-2 text-gray-500 text-sm">
              {searchTerm ? 'No parts found matching your search' : 'No parts available'}
            </div>
          ) : (
            filteredParts.map((part, index) => (
              <div
                key={part.id}
                onClick={() => handleSelect(part)}
                onMouseEnter={() => setHighlightedIndex(index)}
                className={`px-3 py-2 cursor-pointer ${
                  index === highlightedIndex
                    ? 'bg-blue-100'
                    : 'hover:bg-gray-100'
                } ${value === part.id ? 'bg-blue-50' : ''}`}
              >
                <div className="font-medium text-gray-900">{part.part_number}</div>
                <div className="text-sm text-gray-600">{part.name}</div>
                {part.manufacturer_part_number && (
                  <div className="text-xs text-gray-500">
                    Mfr: {part.manufacturer_part_number}
                  </div>
                )}
                {searchTerm && part.description?.toLowerCase().includes(searchTerm.toLowerCase()) && (
                  <div className="text-xs text-gray-500 truncate">
                    {part.description}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Helper text */}
      {isOpen && searchTerm && (
        <div className="text-xs text-gray-500 mt-1">
          Showing {filteredParts.length} of {parts.length} parts
        </div>
      )}
    </div>
  );
};

export default PartSearchSelector;
