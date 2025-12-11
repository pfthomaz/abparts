// frontend/src/components/ConfigurationItem.js

import React, { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { api } from '../services/api';

const ConfigurationItem = ({ configuration, onUpdate, isSuperAdmin }) => {
  const { t, getNamespace, currentLanguage } = useTranslation();
  
  // Debug: Log current language and test translation access
  console.log(`🌍 Current language: ${currentLanguage}`);
  console.log(`🧪 Test translation: ${t('configuration.title')}`);
  
  // Get configuration namespace for direct object access
  const configNamespace = getNamespace('configuration');
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(configuration.value || '');
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const canEdit = configuration.is_user_configurable &&
    (isSuperAdmin || !configuration.is_system_managed);

  const handleEdit = () => {
    setIsEditing(true);
    setEditValue(configuration.value || '');
    setValidationError(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditValue(configuration.value || '');
    setValidationError(null);
  };

  const validateValue = async (value) => {
    if (!configuration.validation_rules) {
      return { isValid: true };
    }

    try {
      setIsValidating(true);
      const result = await api.post('/configuration/validate', {
        key: configuration.key,
        value: value
      });
      return result;

    } catch (error) {
      console.error('Error validating configuration:', error);
      return { isValid: false, error_message: t('configuration.item.validationFailed') };
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setValidationError(null);

      // Validate the value first
      const validation = await validateValue(editValue);
      if (!validation.is_valid) {
        setValidationError(validation.error_message);
        return;
      }

      // Update the configuration
      const result = await onUpdate(configuration.id, editValue);

      if (result.success) {
        setIsEditing(false);
      } else {
        setValidationError(result.error);
      }

    } catch (error) {
      console.error('Error saving configuration:', error);
      setValidationError(t('configuration.item.failedToSave'));
    } finally {
      setIsSaving(false);
    }
  };

  const renderValueInput = () => {
    const commonProps = {
      value: editValue,
      onChange: (e) => setEditValue(e.target.value),
      className: `w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${validationError ? 'border-red-300' : 'border-gray-300'
        }`,
      disabled: isSaving || isValidating
    };

    switch (configuration.data_type) {
      case 'boolean':
        return (
          <select {...commonProps}>
            <option value="true">{t('configuration.item.enabled')}</option>
            <option value="false">{t('configuration.item.disabled')}</option>
          </select>
        );

      case 'integer':
        return (
          <input
            type="number"
            {...commonProps}
            min={configuration.validation_rules?.min}
            max={configuration.validation_rules?.max}
          />
        );

      case 'enum':
        const allowedValues = configuration.validation_rules?.allowed_values || [];
        return (
          <select {...commonProps}>
            <option value="">{t('configuration.item.selectValue')}</option>
            {allowedValues.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        );

      case 'json':
        return (
          <textarea
            {...commonProps}
            rows={4}
            placeholder={t('configuration.item.enterJson')}
          />
        );

      default: // string
        return (
          <input
            type="text"
            {...commonProps}
            maxLength={configuration.validation_rules?.max_length}
            minLength={configuration.validation_rules?.min_length}
          />
        );
    }
  };

  const renderDisplayValue = () => {
    const value = configuration.typed_value;

    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">{t('configuration.item.notSet')}</span>;
    }

    switch (configuration.data_type) {
      case 'boolean':
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
            {value ? t('configuration.item.enabled') : t('configuration.item.disabled')}
          </span>
        );

      case 'json':
        return (
          <pre className="text-sm bg-gray-100 p-2 rounded overflow-x-auto">
            {JSON.stringify(value, null, 2)}
          </pre>
        );

      default:
        return <span className="font-mono">{String(value)}</span>;
    }
  };

  // Helper function to get translated configuration key
  const getTranslatedKey = (key) => {
    // Use namespace to get direct object access
    const configKeys = configNamespace?.configKeys;
    if (configKeys && configKeys[key]) {
      console.log(`✅ Found translation for key: ${key} -> ${configKeys[key]}`);
      return configKeys[key];
    }
    
    // Fallback to dot notation
    const translationKey = `configuration.configKeys.${key}`;
    const translatedKey = t(translationKey);
    console.log(`🔍 Translation lookup fallback: ${translationKey} -> ${translatedKey}`);
    return translatedKey !== translationKey ? translatedKey : key;
  };

  // Helper function to get translated description
  const getTranslatedDescription = (key, fallbackDescription) => {
    // Use namespace to get direct object access
    const configDescriptions = configNamespace?.configDescriptions;
    if (configDescriptions && configDescriptions[key]) {
      console.log(`✅ Found description for key: ${key} -> ${configDescriptions[key]}`);
      return configDescriptions[key];
    }
    
    // Fallback to dot notation
    const translationKey = `configuration.configDescriptions.${key}`;
    const translatedDesc = t(translationKey);
    console.log(`🔍 Description lookup fallback: ${translationKey} -> ${translatedDesc}`);
    return translatedDesc !== translationKey ? translatedDesc : fallbackDescription;
  };

  const getDataTypeIcon = (dataType) => {
    const icons = {
      string: '📝',
      integer: '🔢',
      boolean: '✅',
      json: '📋',
      enum: '📋'
    };
    return icons[dataType] || '⚙️';
  };

  return (
    <div className={`border rounded-lg p-4 ${configuration.is_system_managed ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-300'
      }`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Configuration Header */}
          <div className="flex items-center mb-2">
            <span className="text-lg mr-2">{getDataTypeIcon(configuration.data_type)}</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                {getTranslatedKey(configuration.key)}
                {configuration.is_system_managed && (
                  <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                    {t('configuration.item.systemManaged')}
                  </span>
                )}
                {configuration.requires_restart && (
                  <span className="ml-2 px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                    {t('configuration.item.requiresRestart')}
                  </span>
                )}
              </h3>
              {configuration.description && (
                <p className="text-sm text-gray-600 mt-1">
                  {getTranslatedDescription(configuration.key, configuration.description)}
                </p>
              )}
            </div>
          </div>

          {/* Configuration Value */}
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('configuration.item.currentValue')}
            </label>
            {isEditing ? (
              <div>
                {renderValueInput()}
                {isValidating && (
                  <p className="text-sm text-blue-600 mt-1">
                    <span className="animate-spin inline-block mr-1">⏳</span>
                    {t('configuration.item.validating')}
                  </p>
                )}
                {validationError && (
                  <p className="text-sm text-red-600 mt-1">
                    <span className="mr-1">⚠️</span>
                    {validationError}
                  </p>
                )}
              </div>
            ) : (
              <div className="min-h-[2.5rem] flex items-center">
                {renderDisplayValue()}
              </div>
            )}
          </div>

          {/* Default Value */}
          {configuration.default_value && (
            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('configuration.item.defaultValue')}
              </label>
              <span className="text-sm text-gray-500 font-mono">
                {configuration.default_value}
              </span>
            </div>
          )}

          {/* Validation Rules */}
          {configuration.validation_rules && (
            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('configuration.item.validationRules')}
              </label>
              <div className="text-sm text-gray-600">
                {Object.entries(configuration.validation_rules).map(([rule, value]) => {
                  // Use namespace for validation rules
                  const validationRules = configNamespace?.validationRules;
                  const ruleLabel = (validationRules && validationRules[rule]) || rule;
                  return (
                    <span key={rule} className="inline-block bg-gray-100 px-2 py-1 rounded mr-2 mb-1">
                      {ruleLabel}: {Array.isArray(value) ? value.join(', ') : String(value)}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="ml-4 flex-shrink-0">
          {canEdit && (
            <div className="flex space-x-2">
              {isEditing ? (
                <>
                  <button
                    onClick={handleSave}
                    disabled={isSaving || isValidating}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSaving ? `💾 ${t('configuration.item.saving')}` : `💾 ${t('configuration.item.save')}`}
                  </button>
                  <button
                    onClick={handleCancel}
                    disabled={isSaving}
                    className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 disabled:opacity-50"
                  >
                    ❌ {t('configuration.item.cancel')}
                  </button>
                </>
              ) : (
                <button
                  onClick={handleEdit}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                >
                  ✏️ {t('configuration.item.edit')}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Metadata */}
      <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
        <div className="flex justify-between">
          <span>{t('configuration.item.dataType')}: {t(`configuration.dataType.${configuration.data_type}`)}</span>
          <span>{t('configuration.item.category')}: {configuration.category}</span>
        </div>
        {configuration.updated_at && (
          <div className="mt-1">
            {t('configuration.item.lastUpdated')}: {new Date(configuration.updated_at).toLocaleString()}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfigurationItem;