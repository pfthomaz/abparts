// frontend/src/services/translationService.js

import { api } from './api';

class TranslationService {
  // Protocol Translation Methods
  async getProtocolTranslations(protocolId) {
    return api.get(`/translations/protocols/${protocolId}/translations`);
  }

  async createProtocolTranslation(protocolId, translationData) {
    return api.post(`/translations/protocols/${protocolId}/translations`, translationData);
  }

  async updateProtocolTranslation(protocolId, languageCode, translationData) {
    return api.put(`/translations/protocols/${protocolId}/translations/${languageCode}`, translationData);
  }

  async deleteProtocolTranslation(protocolId, languageCode) {
    return api.delete(`/translations/protocols/${protocolId}/translations/${languageCode}`);
  }

  async getProtocolTranslationStatus(protocolId) {
    return api.get(`/translations/protocols/${protocolId}/translation-status`);
  }

  // Checklist Item Translation Methods
  async getChecklistItemTranslations(itemId) {
    return api.get(`/translations/checklist-items/${itemId}/translations`);
  }

  async createChecklistItemTranslation(itemId, translationData) {
    return api.post(`/translations/checklist-items/${itemId}/translations`, translationData);
  }

  async updateChecklistItemTranslation(itemId, languageCode, translationData) {
    return api.put(`/translations/checklist-items/${itemId}/translations/${languageCode}`, translationData);
  }

  async deleteChecklistItemTranslation(itemId, languageCode) {
    return api.delete(`/translations/checklist-items/${itemId}/translations/${languageCode}`);
  }

  // Language-aware Display Methods
  async getLocalizedProtocol(protocolId, language = null) {
    const url = language 
      ? `/translations/protocols/${protocolId}/localized?language=${language}`
      : `/translations/protocols/${protocolId}/localized`;
    return api.get(url);
  }

  async getLocalizedChecklistItems(protocolId, language = null) {
    const url = language 
      ? `/translations/protocols/${protocolId}/checklist-items/localized?language=${language}`
      : `/translations/protocols/${protocolId}/checklist-items/localized`;
    return api.get(url);
  }

  // Bulk Operations
  async bulkCreateProtocolTranslations(protocolId, translations) {
    return api.post(`/translations/protocols/${protocolId}/translations/bulk`, translations);
  }

  async bulkCreateChecklistItemTranslations(translations) {
    return api.post(`/translations/checklist-items/translations/bulk`, translations);
  }

  // Utility Methods
  getSupportedLanguages() {
    return [
      { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
      { code: 'el', name: 'Greek', nativeName: 'Ελληνικά', flag: '🇬🇷' },
      { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' },
      { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
      { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', flag: '🇹🇷' },
      { code: 'no', name: 'Norwegian', nativeName: 'Norsk', flag: '🇳🇴' }
    ];
  }

  getLanguageByCode(code) {
    return this.getSupportedLanguages().find(lang => lang.code === code);
  }

  calculateCompletionPercentage(status) {
    if (!status || !status.completion_percentage) return {};
    return status.completion_percentage;
  }

  getTranslationStatusColor(percentage) {
    if (percentage >= 100) return 'bg-green-100 text-green-800';
    if (percentage >= 80) return 'bg-yellow-100 text-yellow-800';
    if (percentage >= 50) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  }

  getTranslationStatusIcon(percentage) {
    if (percentage >= 100) return '✅';
    if (percentage >= 80) return '🟡';
    if (percentage >= 50) return '🟠';
    return '🔴';
  }

  // Auto-translation methods
  async autoTranslateProtocol(protocolId, targetLanguages = null) {
    const response = await api.post(`/translations/protocols/${protocolId}/auto-translate`, {
      target_languages: targetLanguages
    });
    return response;
  }

  async autoTranslateProtocolChecklist(protocolId, targetLanguages = null) {
    const response = await api.post(`/translations/protocols/${protocolId}/auto-translate-checklist`, {
      target_languages: targetLanguages
    });
    return response;
  }

  async autoTranslateCompleteProtocol(protocolId, targetLanguages = null) {
    const response = await api.post(`/translations/protocols/${protocolId}/auto-translate-complete`, {
      target_languages: targetLanguages
    });
    return response;
  }

  async getAutoTranslateStatus() {
    const response = await api.get('/translations/auto-translate/status');
    return response;
  }
}

const translationService = new TranslationService();
export default translationService;