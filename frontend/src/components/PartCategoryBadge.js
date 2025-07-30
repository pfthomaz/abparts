// frontend/src/components/PartCategoryBadge.js

import React from 'react';

/**
 * PartCategoryBadge component for visual consumable/bulk material indicators
 * Displays part type with appropriate styling and icons
 */
const PartCategoryBadge = ({
  partType,
  isProprietaryPart = false,
  size = 'medium',
  showIcon = true,
  showLabel = true,
  className = ''
}) => {
  // Part type configurations
  const partTypeConfig = {
    consumable: {
      label: 'Consumable',
      shortLabel: 'CONS',
      description: 'Whole units (pieces, sets, boxes)',
      icon: '📦',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-200',
      dotColor: 'bg-blue-500'
    },
    bulk_material: {
      label: 'Bulk Material',
      shortLabel: 'BULK',
      description: 'Measurable quantities (liters, kg, meters)',
      icon: '⚖️',
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      borderColor: 'border-green-200',
      dotColor: 'bg-green-500'
    }
  };

  // Proprietary part styling
  const proprietaryConfig = {
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
    borderColor: 'border-purple-200',
    dotColor: 'bg-purple-500',
    icon: '🔒',
    label: 'BossAqua'
  };

  // Size configurations
  const sizeConfig = {
    small: {
      containerClass: 'px-2 py-1 text-xs',
      iconClass: 'text-xs',
      dotClass: 'w-1.5 h-1.5'
    },
    medium: {
      containerClass: 'px-3 py-1 text-sm',
      iconClass: 'text-sm',
      dotClass: 'w-2 h-2'
    },
    large: {
      containerClass: 'px-4 py-2 text-base',
      iconClass: 'text-base',
      dotClass: 'w-3 h-3'
    }
  };

  // Get configuration for the part type
  const config = partTypeConfig[partType] || partTypeConfig.consumable;
  const sizeStyles = sizeConfig[size] || sizeConfig.medium;

  // Override with proprietary styling if applicable
  const finalConfig = isProprietaryPart ? {
    ...config,
    bgColor: proprietaryConfig.bgColor,
    textColor: proprietaryConfig.textColor,
    borderColor: proprietaryConfig.borderColor,
    dotColor: proprietaryConfig.dotColor
  } : config;

  // Determine what to display based on size and props
  const displayLabel = size === 'small' ? config.shortLabel : config.label;
  const shouldShowIcon = showIcon && size !== 'small';
  const shouldShowLabel = showLabel;

  return (
    <div className={`part-category-badge ${className}`}>
      <div className={`
        inline-flex items-center rounded-full border
        ${finalConfig.bgColor} 
        ${finalConfig.textColor} 
        ${finalConfig.borderColor}
        ${sizeStyles.containerClass}
        font-medium
      `}>
        {/* Status dot */}
        <div className={`
          ${finalConfig.dotColor} 
          ${sizeStyles.dotClass} 
          rounded-full mr-2
        `}></div>

        {/* Icon */}
        {shouldShowIcon && (
          <span className={`mr-1 ${sizeStyles.iconClass}`}>
            {config.icon}
          </span>
        )}

        {/* Proprietary icon */}
        {isProprietaryPart && shouldShowIcon && (
          <span className={`mr-1 ${sizeStyles.iconClass}`}>
            {proprietaryConfig.icon}
          </span>
        )}

        {/* Label */}
        {shouldShowLabel && (
          <span>
            {displayLabel}
            {isProprietaryPart && size !== 'small' && (
              <span className="ml-1 font-bold">
                ({proprietaryConfig.label})
              </span>
            )}
          </span>
        )}
      </div>

      {/* Tooltip for additional information */}
      {size === 'small' && (
        <div className="hidden group-hover:block absolute z-10 bg-white border border-gray-300 rounded-md shadow-lg p-2 mt-1 text-sm">
          <div className="font-medium text-gray-800">{config.label}</div>
          <div className="text-gray-600 text-xs mt-1">{config.description}</div>
          {isProprietaryPart && (
            <div className="text-purple-600 text-xs mt-1 font-medium">
              🔒 BossAqua Proprietary Part
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * PartCategorySelector component for selecting part categories in forms
 */
export const PartCategorySelector = ({
  value,
  onChange,
  disabled = false,
  required = false,
  className = ''
}) => {
  const options = [
    {
      value: 'consumable',
      label: 'Consumable',
      description: 'Whole units (pieces, sets, boxes)',
      icon: '📦'
    },
    {
      value: 'bulk_material',
      label: 'Bulk Material',
      description: 'Measurable quantities (liters, kg, meters)',
      icon: '⚖️'
    }
  ];

  return (
    <div className={`part-category-selector ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {options.map((option) => (
          <label
            key={option.value}
            className={`
              relative flex items-center p-4 border rounded-lg cursor-pointer
              ${value === option.value
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input
              type="radio"
              name="part_type"
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange && onChange(e.target.value)}
              disabled={disabled}
              required={required}
              className="sr-only"
            />

            <div className="flex items-center">
              <span className="text-2xl mr-3">{option.icon}</span>
              <div>
                <div className="font-medium text-gray-900">{option.label}</div>
                <div className="text-sm text-gray-500">{option.description}</div>
              </div>
            </div>

            {value === option.value && (
              <div className="absolute top-2 right-2">
                <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
            )}
          </label>
        ))}
      </div>
    </div>
  );
};

/**
 * PartCategoryFilter component for filtering parts by category
 */
export const PartCategoryFilter = ({
  value,
  onChange,
  showAll = true,
  className = ''
}) => {
  const options = [
    ...(showAll ? [{ value: 'all', label: 'All Types', icon: '📋' }] : []),
    { value: 'consumable', label: 'Consumable', icon: '📦' },
    { value: 'bulk_material', label: 'Bulk Material', icon: '⚖️' }
  ];

  return (
    <div className={`part-category-filter ${className}`}>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange && onChange(option.value)}
            className={`
              inline-flex items-center px-3 py-2 rounded-full text-sm font-medium border
              ${value === option.value
                ? 'bg-blue-100 text-blue-800 border-blue-200'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }
              transition-colors duration-200
            `}
          >
            <span className="mr-2">{option.icon}</span>
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default PartCategoryBadge;