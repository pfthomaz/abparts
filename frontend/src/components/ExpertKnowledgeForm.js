import React, { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';

const ExpertKnowledgeForm = ({ onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    problem_description: '',
    solution: '',
    machine_version: '',
    tags: [],
    metadata: {}
  });
  const [tagInput, setTagInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const machineVersions = [
    { value: '', label: t('expert_knowledge.all_versions') },
    { value: 'V4.0', label: 'AutoBoss V4.0' },
    { value: 'V3.1B', label: 'AutoBoss V3.1B' },
    { value: 'V3.0', label: 'AutoBoss V3.0' },
    { value: 'V2.0', label: 'AutoBoss V2.0' }
  ];

  const commonTags = [
    'startup', 'cleaning_performance', 'mechanical', 'electrical', 
    'hydraulic', 'remote_control', 'maintenance', 'safety', 
    'troubleshooting', 'parts_replacement'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddTag = (tag) => {
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
    setTagInput('');
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Failed to submit expert knowledge:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        {t('expert_knowledge.add_title')}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('expert_knowledge.problem_description')} *
          </label>
          <textarea
            name="problem_description"
            value={formData.problem_description}
            onChange={handleInputChange}
            rows={3}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder={t('expert_knowledge.problem_placeholder')}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('expert_knowledge.solution')} *
          </label>
          <textarea
            name="solution"
            value={formData.solution}
            onChange={handleInputChange}
            rows={4}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder={t('expert_knowledge.solution_placeholder')}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('expert_knowledge.machine_version')}
          </label>
          <select
            name="machine_version"
            value={formData.machine_version}
            onChange={handleInputChange}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            {machineVersions.map((version) => (
              <option key={version.value} value={version.value}>
                {version.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('expert_knowledge.tags')}
          </label>
          
          {/* Common tags */}
          <div className="mb-2">
            <p className="text-xs text-gray-500 mb-1">{t('expert_knowledge.common_tags')}:</p>
            <div className="flex flex-wrap gap-1">
              {commonTags.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => handleAddTag(tag)}
                  className={`px-2 py-1 text-xs rounded-full border ${
                    formData.tags.includes(tag)
                      ? 'bg-blue-100 text-blue-800 border-blue-300'
                      : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
                  }`}
                  disabled={formData.tags.includes(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* Custom tag input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag(tagInput);
                }
              }}
              className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder={t('expert_knowledge.custom_tag_placeholder')}
            />
            <button
              type="button"
              onClick={() => handleAddTag(tagInput)}
              className="px-3 py-2 text-sm bg-gray-100 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              {t('expert_knowledge.add_tag')}
            </button>
          </div>

          {/* Selected tags */}
          {formData.tags.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-1">{t('expert_knowledge.selected_tags')}:</p>
              <div className="flex flex-wrap gap-1">
                {formData.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            {t('common.cancel')}
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !formData.problem_description || !formData.solution}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isSubmitting ? t('expert_knowledge.submitting') : t('expert_knowledge.submit')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ExpertKnowledgeForm;