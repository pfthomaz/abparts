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

  // Auto-translation methods with extended timeout
  async autoTranslateProtocol(protocolId, targetLanguages = null) {
    let url = `/translations/protocols/${protocolId}/auto-translate`;
    if (targetLanguages && targetLanguages.length > 0) {
      const params = new URLSearchParams();
      targetLanguages.forEach(lang => params.append('target_languages', lang));
      url += `?${params.toString()}`;
    }
    const response = await this._requestWithTimeout(url, 'POST', null, 120000); // 2 minutes
    return response;
  }

  async autoTranslateProtocolChecklist(protocolId, targetLanguages = null) {
    let url = `/translations/protocols/${protocolId}/auto-translate-checklist`;
    if (targetLanguages && targetLanguages.length > 0) {
      const params = new URLSearchParams();
      targetLanguages.forEach(lang => params.append('target_languages', lang));
      url += `?${params.toString()}`;
    }
    const response = await this._requestWithTimeout(url, 'POST', null, 120000); // 2 minutes
    return response;
  }

  async autoTranslateCompleteProtocol(protocolId, targetLanguages = null) {
    let url = `/translations/protocols/${protocolId}/auto-translate-complete`;
    if (targetLanguages && targetLanguages.length > 0) {
      const params = new URLSearchParams();
      targetLanguages.forEach(lang => params.append('target_languages', lang));
      url += `?${params.toString()}`;
    }
    const response = await this._requestWithTimeout(url, 'POST', null, 180000); // 3 minutes
    return response;
  }

  // Helper method for requests with custom timeout
  async _requestWithTimeout(endpoint, method = 'GET', body = null, timeout = 30000) {
    const token = localStorage.getItem('authToken');
    const headers = new Headers();

    if (!(body instanceof FormData)) {
      headers.append('Content-Type', 'application/json');
    }

    if (token) {
      headers.append('Authorization', `Bearer ${token}`);
    }

    const config = {
      method,
      headers,
    };

    if (body) {
      config.body = body instanceof FormData ? body : JSON.stringify(body);
    }

    // Create an AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    config.signal = controller.signal;

    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 
        (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api');
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      clearTimeout(timeoutId);

      if (!response.ok) {
        // Try to parse error response as JSON
        const errorData = await response.json().catch(() => ({
          detail: `Request failed with status ${response.status}`
        }));

        // Create an error object with additional properties for better error handling
        const error = new Error(errorData.detail || `Request failed with status ${response.status}`);
        error.response = {
          status: response.status,
          data: errorData,
          headers: response.headers
        };
        throw error;
      }

      // Handle responses that might not have a body (e.g., 204 No Content)
      if (response.status === 204) {
        return null;
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      // Handle abort/timeout
      if (error.name === 'AbortError') {
        const timeoutError = new Error('Translation request timed out. This may happen with large protocols or multiple languages. Please try again or contact support.');
        timeoutError.code = 'ECONNABORTED';
        timeoutError.request = true;
        throw timeoutError;
      }

      // Handle network errors
      if (!error.response) {
        error.request = true;
      }

      // Log the error for debugging
      console.error(`API Error (${endpoint}):`, error);

      // Rethrow the original error to preserve structure for proper error handling
      throw error;
    }
  }

  async getAutoTranslateStatus() {
    const response = await api.get('/translations/auto-translate/status');
    return response;
  }
}

const translationService = new TranslationService();
export default translationService;