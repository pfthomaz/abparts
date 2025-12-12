import { memo } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import MultilingualPartName from './MultilingualPartName';
import PartPhotoGallery from './PartPhotoGallery';
import PartCategoryBadge from './PartCategoryBadge';
import PermissionGuard from './PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';
import { formatNumber, getTranslatedUnit } from '../utils';

/**
 * Optimized PartCard component with React.memo for better performance
 * Prevents unnecessary re-renders when parent component updates
 */
const PartCard = memo(({
  part,
  onEdit,
  onDelete
}) => {
  const { t } = useTranslation();
  const handleEdit = () => onEdit(part);
  const handleDelete = () => onDelete(part.id);

  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200 group">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <MultilingualPartName
            value={part.name}
            isEditing={false}
            preferredLanguage="en"
            className="text-2xl font-semibold text-purple-700 mb-2"
          />
        </div>
        <PartCategoryBadge
          partType={part.part_type}
          isProprietaryPart={part.is_proprietary}
          size="medium"
        />
      </div>

      <div className="space-y-1 mb-3">
        <p className="text-gray-600">
          <span className="font-medium">{t('partCard.partNumber')}:</span> {part.part_number}
        </p>
        {part.description && (
          <p className="text-gray-600">
            <span className="font-medium">{t('partCard.description')}:</span> {part.description}
          </p>
        )}
        <p className="text-gray-600">
          <span className="font-medium">{t('partCard.unit')}:</span> {getTranslatedUnit(part.unit_of_measure, t)}
        </p>
        {part.manufacturer && (
          <p className="text-gray-600">
            <span className="font-medium">{t('partCard.manufacturer')}:</span> {part.manufacturer}
          </p>
        )}
        {part.part_code && (
          <p className="text-gray-600">
            <span className="font-medium">{t('partCard.partCode')}:</span> {part.part_code}
          </p>
        )}
        {part.serial_number && (
          <p className="text-gray-600">
            <span className="font-medium">{t('partCard.serialNumber')}:</span> {part.serial_number}
          </p>
        )}
        {part.manufacturer_part_number && (
          <p className="text-gray-600">
            <span className="font-medium">{t('partCard.mfgPartNumber')}:</span> {part.manufacturer_part_number}
          </p>
        )}
      </div>

      {/* Inventory Information */}
      <InventorySection part={part} />

      {/* Images */}
      {part.image_urls && part.image_urls.length > 0 && (
        <div className="mt-3">
          <span className="font-medium text-gray-600 block mb-2">{t('partCard.images')}:</span>
          <PartPhotoGallery
            images={part.image_urls}
            isEditing={false}
            className="part-images-display"
          />
        </div>
      )}

      <p className="text-sm text-gray-400 mt-3">ID: {part.id}</p>

      <div className="mt-4 flex space-x-2">
        <PermissionGuard permission={PERMISSIONS.MANAGE_PARTS} hideIfNoPermission={true}>
          <button
            onClick={handleEdit}
            className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm transition-colors duration-150"
          >
            {t('common.edit')}
          </button>
        </PermissionGuard>
        <PermissionGuard permission={PERMISSIONS.MANAGE_PARTS} hideIfNoPermission={true}>
          <button
            onClick={handleDelete}
            className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm transition-colors duration-150"
          >
            {t('common.delete')}
          </button>
        </PermissionGuard>
      </div>
    </div>
  );
});

/**
 * Optimized inventory section component
 */
const InventorySection = memo(({ part }) => {
  const { t } = useTranslation();
  
  return (
    <div className="mt-3 p-3 bg-gray-100 rounded-md">
      <div className="flex justify-between items-center mb-2">
        <span className="font-medium text-gray-700">{t('partCard.totalStock')}:</span>
        <span className={`font-semibold ${part.is_low_stock ? 'text-red-600' : 'text-green-600'}`}>
          {formatNumber(part.total_stock || 0, part.unit_of_measure)} {getTranslatedUnit(part.unit_of_measure, t)}
          {part.is_low_stock && <span className="ml-1 text-xs">({t('partCard.low')})</span>}
        </span>
      </div>

      {part.warehouse_inventory && part.warehouse_inventory.length > 0 ? (
        <div className="space-y-1">
          <span className="text-sm font-medium text-gray-600">{t('partCard.byWarehouse')}:</span>
          {part.warehouse_inventory.map((warehouse, idx) => (
            <div key={idx} className="flex justify-between text-sm">
              <span className="text-gray-600">{warehouse.warehouse_name}:</span>
              <span className={warehouse.is_low_stock ? 'text-red-600' : 'text-gray-800'}>
                {formatNumber(warehouse.current_stock, warehouse.unit_of_measure)} {getTranslatedUnit(warehouse.unit_of_measure, t)}
                {warehouse.is_low_stock && <span className="ml-1 text-xs">({t('partCard.low')})</span>}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500">{t('partCard.noInventoryData')}</p>
      )}
    </div>
  );
});

PartCard.displayName = 'PartCard';
InventorySection.displayName = 'InventorySection';

export default PartCard;