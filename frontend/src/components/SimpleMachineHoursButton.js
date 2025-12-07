// Simple Machine Hours Button - Minimal version
import React, { useState } from 'react';
import { machinesService } from '../services/machinesService';
import { useTranslation } from '../hooks/useTranslation';

const SimpleMachineHoursButton = ({ machineId, machineName, onHoursSaved }) => {
  const { t } = useTranslation();
  const [showModal, setShowModal] = useState(false);
  const [hoursValue, setHoursValue] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!hoursValue || parseFloat(hoursValue) <= 0) {
      setError(t('machines.pleaseEnterValidHours'));
      return;
    }

    setIsSubmitting(true);

    try {
      // Use the machinesService which has proper API configuration
      const result = await machinesService.recordMachineHours(machineId, {
        hours_value: parseFloat(hoursValue),
        notes: notes.trim() || null
      });

      console.log('Machine hours saved successfully:', result);
      setSuccess(true);
      setHoursValue('');
      setNotes('');
      
      // Call the callback to refresh machine data
      if (onHoursSaved) {
        onHoursSaved();
      }
      
      setTimeout(() => {
        setShowModal(false);
        setSuccess(false);
      }, 1500);
    } catch (error) {
      console.error('Error saving machine hours:', error);
      
      // Extract error message from the error object
      let errorMessage = t('machines.failedToSaveHours');
      if (error.message) {
        errorMessage = error.message;
      } else if (error.response && error.response.data) {
        const errorData = error.response.data;
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (typeof errorData.detail === 'object' && errorData.detail.detail) {
          errorMessage = errorData.detail.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!showModal) {
    return (
      <button
        onClick={() => setShowModal(true)}
        className="bg-green-600 text-white px-3 py-1 rounded-md text-sm hover:bg-green-700 transition-colors"
      >
        📊 {t('machines.enterHours')}
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="bg-green-600 text-white px-6 py-4 rounded-t-lg">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">{t('machines.recordMachineHours')}</h2>
            <button
              onClick={() => setShowModal(false)}
              className="text-white hover:text-gray-200 text-2xl"
              disabled={isSubmitting}
            >
              ×
            </button>
          </div>
          <p className="text-green-100 text-sm mt-1">{machineName}</p>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
              ✅ {t('machines.hoursSavedSuccessfully')}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Hours Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('machines.currentHoursFromPLC')} *
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder={t('machines.enterHoursPlaceholder')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              value={hoursValue}
              onChange={(e) => setHoursValue(e.target.value)}
              disabled={isSubmitting}
              required
            />
          </div>

          {/* Notes Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('machines.notesOptional')}
            </label>
            <textarea
              rows="2"
              placeholder={t('machines.anyNotesPlaceholder')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Buttons */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => setShowModal(false)}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              disabled={isSubmitting}
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? t('common.saving') : t('common.save')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SimpleMachineHoursButton;