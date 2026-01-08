import React, { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';

const EscalationModal = ({ 
  isOpen, 
  onClose, 
  onEscalate, 
  sessionId,
  currentStep,
  confidenceScore 
}) => {
  const { t } = useTranslation();
  const [escalationReason, setEscalationReason] = useState('user_request');
  const [priority, setPriority] = useState('medium');
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await onEscalate({
        escalation_reason: escalationReason,
        priority: priority,
        additional_notes: additionalNotes
      });
      onClose();
    } catch (error) {
      console.error('Failed to escalate session:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  // Define translations inside render to ensure they're fresh
  const escalationReasons = [
    { value: 'user_request', label: 'Χρειάζομαι βοήθεια από ειδικό' },
    { value: 'low_confidence', label: 'Το AI έχει χαμηλή εμπιστοσύνη' },
    { value: 'steps_exceeded', label: 'Πάρα πολλά βήματα αντιμετώπισης' },
    { value: 'safety_concern', label: 'Ανησυχία ασφάλειας' },
    { value: 'complex_issue', label: 'Σύνθετο τεχνικό πρόβλημα' },
    { value: 'expert_required', label: 'Απαιτείται γνώση ειδικού' }
  ];

  const priorities = [
    { value: 'low', label: 'Χαμηλή - Μπορεί να περιμένει' },
    { value: 'medium', label: 'Μέση - Κανονική προτεραιότητα' },
    { value: 'high', label: 'Υψηλή - Επείγον' },
    { value: 'urgent', label: 'Επείγον - Κρίσιμο πρόβλημα' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Κλιμάκωση σε Ειδικό Υποστήριξης
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            Εάν δεν μπορείτε να επιλύσετε το πρόβλημα, οι ειδικοί τεχνικοί μας μπορούν να παρέχουν άμεση βοήθεια.
          </p>
          {confidenceScore !== undefined && (
            <p className="text-xs text-blue-600 mt-1">
              Εμπιστοσύνη AI: {(confidenceScore * 100).toFixed(1)}%
            </p>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Λόγος Κλιμάκωσης
            </label>
            <select
              value={escalationReason}
              onChange={(e) => setEscalationReason(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              required
            >
              {escalationReasons.map((reason) => (
                <option key={reason.value} value={reason.value}>
                  {reason.label}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Επίπεδο Προτεραιότητας
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              required
            >
              {priorities.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Επιπλέον Σημειώσεις
            </label>
            <textarea
              value={additionalNotes}
              onChange={(e) => setAdditionalNotes(e.target.value)}
              rows={3}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Περιγράψτε τυχόν επιπλέον λεπτομέρειες ή συγκεκριμένες ανησυχίες..."
            />
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Δημιουργία δελτίου...' : 'Δημιουργία Δελτίου Υποστήριξης'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EscalationModal;