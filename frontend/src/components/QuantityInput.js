// frontend/src/components/QuantityInput.js

import React from 'react';

/**
 * Quantity input component that handles both whole numbers (consumable) and decimals (bulk_material)
 */
function QuantityInput({
  value,
  onChange,
  partType = 'consumable',
  unitOfMeasure = 'pieces',
  min = 0,
  max,
  step,
  disabled = false,
  required = false,
  className = '',
  placeholder,
  ...props
}) {
  // Determine step and validation based on part type
  const inputStep = step || (partType === 'bulk_material' ? '0.001' : '1');
  const inputPattern = partType === 'bulk_material' ? '[0-9]+(\\.[0-9]+)?' : '[0-9]+';

  const handleChange = (e) => {
    const inputValue = e.target.value;

    // Allow empty value for clearing
    if (inputValue === '') {
      onChange(e);
      return;
    }

    // Validate based on part type
    if (partType === 'consumable') {
      // Only allow whole numbers for consumable parts
      if (/^\d+$/.test(inputValue)) {
        onChange(e);
      }
    } else {
      // Allow decimal numbers for bulk materials
      if (/^\d*\.?\d*$/.test(inputValue)) {
        onChange(e);
      }
    }
  };

  // Don't include unit in placeholder since we show it separately on the right
  const defaultPlaceholder = placeholder ||
    (partType === 'bulk_material' ? '0.000' : '0');

  return (
    <div className="relative">
      <input
        type="number"
        value={value}
        onChange={handleChange}
        min={min}
        max={max}
        step={inputStep}
        pattern={inputPattern}
        disabled={disabled}
        required={required}
        placeholder={defaultPlaceholder}
        className={`w-full px-3 py-2 pr-20 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${className}`}
        {...props}
      />
      {unitOfMeasure && (
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <span className="text-gray-500 text-sm">{unitOfMeasure}</span>
        </div>
      )}
    </div>
  );
}

export default QuantityInput;