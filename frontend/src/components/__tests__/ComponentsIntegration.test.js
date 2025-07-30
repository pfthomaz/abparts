// frontend/src/components/__tests__/ComponentsIntegration.test.js

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import the components we created
import PartCategoryBadge from '../PartCategoryBadge';

// Mock the services
jest.mock('../../services/partsService', () => ({
  partsService: {
    uploadImage: jest.fn().mockResolvedValue({ url: '/static/images/test.jpg' })
  }
}));

jest.mock('../../services/api', () => ({
  API_BASE_URL: 'http://localhost:8000'
}));

describe('Enhanced Parts Components Integration', () => {
  describe('PartCategoryBadge', () => {
    test('renders consumable badge correctly', () => {
      render(
        <PartCategoryBadge
          partType="consumable"
          isProprietaryPart={false}
        />
      );

      expect(screen.getByText('Consumable')).toBeInTheDocument();
    });

    test('renders bulk material badge correctly', () => {
      render(
        <PartCategoryBadge
          partType="bulk_material"
          isProprietaryPart={false}
        />
      );

      expect(screen.getByText('Bulk Material')).toBeInTheDocument();
    });

    test('displays proprietary indicator', () => {
      render(
        <PartCategoryBadge
          partType="consumable"
          isProprietaryPart={true}
        />
      );

      expect(screen.getByText(/BossAqua/)).toBeInTheDocument();
    });
  });
});