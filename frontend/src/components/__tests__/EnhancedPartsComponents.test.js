// frontend/src/components/__tests__/EnhancedPartsComponents.test.js

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import the components we created
import MultilingualPartName from '../MultilingualPartName';
import PartCategoryBadge, { PartCategorySelector, PartCategoryFilter } from '../PartCategoryBadge';
import PartPhotoGallery from '../PartPhotoGallery';

// Mock the services
jest.mock('../../services/partsService', () => ({
  partsService: {
    uploadImage: jest.fn().mockResolvedValue({ url: '/static/images/test.jpg' })
  }
}));

jest.mock('../../services/api', () => ({
  API_BASE_URL: 'http://localhost:8000'
}));

describe('Enhanced Parts Components', () => {
  describe('MultilingualPartName', () => {
    test('displays multilingual name correctly in view mode', () => {
      const multilingualName = 'Engine Filter | Φίλτρο Κινητήρα | مرشح المحرك';

      render(
        <MultilingualPartName
          value={multilingualName}
          isEditing={false}
          preferredLanguage="en"
        />
      );

      expect(screen.getByText('Engine Filter')).toBeInTheDocument();
    });

    test('shows editing interface in edit mode', () => {
      const multilingualName = 'Engine Filter | Φίλτρο Κινητήρα | مرشح المحرك';
      const mockOnChange = jest.fn();

      render(
        <MultilingualPartName
          value={multilingualName}
          isEditing={true}
          onChange={mockOnChange}
          supportedLanguages={['en', 'el', 'ar']}
        />
      );

      expect(screen.getByLabelText(/English/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Greek/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Arabic/)).toBeInTheDocument();
    });

    test('handles language input changes', () => {
      const mockOnChange = jest.fn();

      render(
        <MultilingualPartName
          value=""
          isEditing={true}
          onChange={mockOnChange}
          supportedLanguages={['en', 'el']}
        />
      );

      const englishInput = screen.getByLabelText(/English/);
      fireEvent.change(englishInput, { target: { value: 'Test Part' } });

      expect(mockOnChange).toHaveBeenCalledWith('Test Part');
    });
  });

  describe('PartCategoryBadge', () => {
    test('displays consumable badge correctly', () => {
      render(
        <PartCategoryBadge
          partType="consumable"
          isProprietaryPart={false}
        />
      );

      expect(screen.getByText('Consumable')).toBeInTheDocument();
    });

    test('displays bulk material badge correctly', () => {
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

    test('shows different sizes correctly', () => {
      const { rerender } = render(
        <PartCategoryBadge
          partType="consumable"
          size="small"
        />
      );

      expect(screen.getByText('CONS')).toBeInTheDocument();

      rerender(
        <PartCategoryBadge
          partType="consumable"
          size="medium"
        />
      );

      expect(screen.getByText('Consumable')).toBeInTheDocument();
    });
  });

  describe('PartCategorySelector', () => {
    test('renders category options', () => {
      const mockOnChange = jest.fn();

      render(
        <PartCategorySelector
          value="consumable"
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('Consumable')).toBeInTheDocument();
      expect(screen.getByText('Bulk Material')).toBeInTheDocument();
      expect(screen.getByText(/Whole units/)).toBeInTheDocument();
      expect(screen.getByText(/Measurable quantities/)).toBeInTheDocument();
    });

    test('handles selection changes', () => {
      const mockOnChange = jest.fn();

      render(
        <PartCategorySelector
          value="consumable"
          onChange={mockOnChange}
        />
      );

      const bulkMaterialOption = screen.getByDisplayValue('bulk_material');
      fireEvent.click(bulkMaterialOption);

      expect(mockOnChange).toHaveBeenCalledWith('bulk_material');
    });
  });

  describe('PartCategoryFilter', () => {
    test('renders filter options', () => {
      const mockOnChange = jest.fn();

      render(
        <PartCategoryFilter
          value="all"
          onChange={mockOnChange}
          showAll={true}
        />
      );

      expect(screen.getByText('All Types')).toBeInTheDocument();
      expect(screen.getByText('Consumable')).toBeInTheDocument();
      expect(screen.getByText('Bulk Material')).toBeInTheDocument();
    });

    test('handles filter changes', () => {
      const mockOnChange = jest.fn();

      render(
        <PartCategoryFilter
          value="all"
          onChange={mockOnChange}
        />
      );

      const consumableButton = screen.getByText('Consumable');
      fireEvent.click(consumableButton);

      expect(mockOnChange).toHaveBeenCalledWith('consumable');
    });
  });

  describe('PartPhotoGallery', () => {
    test('displays images in view mode', () => {
      const images = ['/static/images/test1.jpg', '/static/images/test2.jpg'];

      render(
        <PartPhotoGallery
          images={images}
          isEditing={false}
        />
      );

      const imageElements = screen.getAllByRole('img');
      expect(imageElements).toHaveLength(2);
    });

    test('shows upload interface in edit mode', () => {
      const mockOnImagesChange = jest.fn();

      render(
        <PartPhotoGallery
          images={[]}
          isEditing={true}
          onImagesChange={mockOnImagesChange}
        />
      );

      expect(screen.getByText(/Click to upload images/)).toBeInTheDocument();
      expect(screen.getByText(/Max 4/)).toBeInTheDocument();
    });

    test('shows no images message when empty', () => {
      render(
        <PartPhotoGallery
          images={[]}
          isEditing={false}
        />
      );

      expect(screen.getByText('No images available')).toBeInTheDocument();
    });
  });
});