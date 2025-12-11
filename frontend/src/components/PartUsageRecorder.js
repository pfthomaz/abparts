// frontend/src/components/PartUsageRecorder.js

import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { transactionService } from '../services/transactionService';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { machinesService } from '../services/machinesService';
import { inventoryService } from '../services/inventoryService';
import QuantityInput from './QuantityInput';
import Modal from './Modal';

const PartUsageRecorder = ({ isOpen, onClose, onUsageRecorded, initialMachineId = null }) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form data
  const [formData, setFormData] = useState({
    machine_id: initialMachineId || '',
    part_id: '',
    from_warehouse_id: '',
    quantity: '',
    usage_date: new Date().toISOString().split('T')[0],
    notes: '',
    reference_number: ''
  });

  // Supporting data
  const [machines, setMachines] = useState([]);
  const [parts, setParts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [selectedPartInventory, setSelectedPartInventory] = useState(null);
  const [warehouseInventory, setWarehouseInventory] = useState([]);

  // Fetch supporting data
  useEffect(() => {
    if (isOpen) {
      fetchSupportingData();
      resetForm();
    }
  }, [isOpen, initialMachineId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch warehouse inventory when warehouse is selected
  useEffect(() => {
    if (formData.from_warehouse_id) {
      fetchWarehouseInventory();
    } else {
      setWarehouseInventory([]);
    }
  }, [formData.from_warehouse_id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch available inventory when part and warehouse are selected
  useEffect(() => {
    if (formData.part_id && formData.from_warehouse_id) {
      fetchPartInventory();
    } else {
      setSelectedPartInventory(null);
    }
  }, [formData.part_id, formData.from_warehouse_id]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchSupportingData = async () => {
    try {
      console.log('Fetching supporting data...');
      const [machinesData, partsData, warehousesData] = await Promise.all([
        machinesService.getMachines(),
        partsService.getParts(),
        warehouseService.getWarehouses()
      ]);

      console.log('Raw parts data:', partsData);

      // Ensure data is in array format
      const machinesArray = Array.isArray(machinesData) ? machinesData : (machinesData?.data || machinesData?.items || []);
      const partsArray = Array.isArray(partsData) ? partsData : (partsData?.data || partsData?.items || []);
      const warehousesArray = Array.isArray(warehousesData) ? warehousesData : (warehousesData?.data || warehousesData?.items || []);
      
      console.log('Machines array:', machinesArray.length);
      console.log('Parts array:', partsArray.length, partsArray);
      console.log('Warehouses array:', warehousesArray.length);
      
      setMachines(machinesArray);
      setParts(partsArray);
      setWarehouses(warehousesArray);

      // Auto-select if only one option available
      if (warehousesArray.length === 1 && !formData.from_warehouse_id) {
        setFormData(prev => ({ ...prev, from_warehouse_id: warehousesArray[0].id }));
      }
      if (machinesArray.length === 1 && !formData.machine_id && !initialMachineId) {
        setFormData(prev => ({ ...prev, machine_id: machinesArray[0].id }));
      }
    } catch (err) {
      console.error('Failed to fetch supporting data:', err);
      setError(t('partUsage.failedToLoadData'));
    }
  };

  const fetchWarehouseInventory = async () => {
    try {
      console.log('Fetching inventory for warehouse:', formData.from_warehouse_id);
      const inventory = await inventoryService.getWarehouseInventory(
        formData.from_warehouse_id
      );

      console.log('Raw inventory response:', inventory);
      console.log('Response type:', typeof inventory);
      console.log('Is array?', Array.isArray(inventory));

      // Handle different response formats
      let inventoryArray = [];
      if (Array.isArray(inventory)) {
        inventoryArray = inventory;
      } else if (inventory?.data && Array.isArray(inventory.data)) {
        inventoryArray = inventory.data;
      } else if (inventory?.items && Array.isArray(inventory.items)) {
        inventoryArray = inventory.items;
      }

      console.log('Inventory array:', inventoryArray);

      // Filter to only show parts with stock > 0
      const availableInventory = inventoryArray.filter(item => {
        const stock = item.current_stock || item.quantity || 0;
        console.log(`Part ${item.part_id}: stock = ${stock}`);
        return stock > 0;
      });
      
      console.log('Available inventory (stock > 0):', availableInventory);
      console.log('First inventory item structure:', availableInventory[0]);
      setWarehouseInventory(availableInventory);

      // Auto-select if only one part available
      if (availableInventory.length === 1 && !formData.part_id) {
        setFormData(prev => ({ ...prev, part_id: availableInventory[0].part_id }));
      }
    } catch (err) {
      console.error('Failed to fetch warehouse inventory:', err);
      setWarehouseInventory([]);
    }
  };

  const fetchPartInventory = async () => {
    try {
      const inventory = await inventoryService.getInventory({
        part_id: formData.part_id,
        warehouse_id: formData.from_warehouse_id
      });

      if (inventory && inventory.length > 0) {
        setSelectedPartInventory(inventory[0]);
      } else {
        setSelectedPartInventory({ current_stock: 0, quantity: 0 });
      }
    } catch (err) {
      console.error('Failed to fetch inventory:', err);
      setSelectedPartInventory({ current_stock: 0, quantity: 0 });
    }
  };

  const resetForm = () => {
    setFormData({
      machine_id: initialMachineId || '',
      part_id: '',
      from_warehouse_id: '',
      quantity: '',
      usage_date: new Date().toISOString().split('T')[0],
      notes: '',
      reference_number: ''
    });
    setSelectedPartInventory(null);
    setError(null);
    setSuccess(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.machine_id) {
      setError(t('partUsage.pleaseSelectMachine'));
      return false;
    }

    if (!formData.part_id) {
      setError(t('partUsage.pleaseSelectPart'));
      return false;
    }

    if (!formData.from_warehouse_id) {
      setError(t('partUsage.pleaseSelectWarehouse'));
      return false;
    }

    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      setError(t('partUsage.pleaseEnterValidQuantity'));
      return false;
    }

    // Check if sufficient inventory is available
    if (selectedPartInventory && parseFloat(formData.quantity) > selectedPartInventory.quantity) {
      setError(t('partUsage.insufficientInventory', { available: selectedPartInventory.quantity }));
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Get the unit of measure from the selected part
      const selectedPartData = Array.isArray(parts) ? parts.find(p => p.id === formData.part_id) : null;
      const unitOfMeasure = selectedPartData?.unit_of_measure || selectedPartInventory?.unit_of_measure || 'pieces';

      // Create a consumption transaction
      // Use current timestamp for transaction_date to ensure proper ordering with adjustments
      const transactionData = {
        transaction_type: 'consumption',
        part_id: formData.part_id,
        from_warehouse_id: formData.from_warehouse_id,
        machine_id: formData.machine_id,
        quantity: parseFloat(formData.quantity),
        unit_of_measure: unitOfMeasure,
        transaction_date: new Date().toISOString(), // Use current timestamp, not midnight
        notes: formData.notes || null,
        reference_number: formData.reference_number || null,
        performed_by_user_id: user.id
      };

      console.log('Submitting transaction data:', transactionData);

      const result = await transactionService.createTransaction(transactionData);

      console.log('Transaction created successfully:', result);

      setSuccess(t('partUsage.recordedSuccessfully'));

      if (onUsageRecorded) {
        onUsageRecorded(result);
      }

      // Close modal after short delay to show success message
      setTimeout(() => {
        onClose();
      }, 1500);

    } catch (err) {
      console.error('Transaction creation error:', err);
      console.error('Error response:', err.response?.data);
      const errorMessage = err.response?.data?.detail || err.message || t('partUsage.failedToRecord');
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    } finally {
      setLoading(false);
    }
  };

  const selectedPart = Array.isArray(parts) ? parts.find(p => p.id === formData.part_id) : null;
  const selectedMachine = Array.isArray(machines) ? machines.find(m => m.id === formData.machine_id) : null;
  const selectedWarehouse = Array.isArray(warehouses) ? warehouses.find(w => w.id === formData.from_warehouse_id) : null;

  // Validate organizational boundaries
  const validateOrganizationalBoundary = () => {
    if (!selectedMachine || !selectedWarehouse) return true;

    // Get the correct organization IDs
    const machineOrgId = selectedMachine.customer_organization_id || selectedMachine.organization_id;
    const warehouseOrgId = selectedWarehouse.organization_id;

    // Check if machine and warehouse belong to the same organization
    if (machineOrgId !== warehouseOrgId) {
      return false;
    }

    // Check if user has access to this organization
    if (user.role !== 'super_admin' && user.organization_id !== machineOrgId) {
      return false;
    }

    return true;
  };

  const organizationalBoundaryValid = validateOrganizationalBoundary();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={t('partUsage.title')}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">{t('common.error')}:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">{t('common.success')}:</strong>
            <span className="block sm:inline ml-2">{success}</span>
          </div>
        )}

        {!organizationalBoundaryValid && selectedMachine && selectedWarehouse && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">{t('common.warning')}:</strong>
            <span className="block sm:inline ml-2">
              {t('partUsage.organizationMismatchWarning')}
            </span>
          </div>
        )}

        {/* Step 1: Select Warehouse */}
        <div>
          <label htmlFor="from_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.step1FromWarehouse')} <span className="text-red-500">*</span>
          </label>
          <select
            id="from_warehouse_id"
            name="from_warehouse_id"
            value={formData.from_warehouse_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required
          >
            <option value="">{t('partUsage.selectWarehouseFirst')}</option>
            {Array.isArray(warehouses) && warehouses.map(warehouse => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name}
                {user.role === 'super_admin' && warehouse.organization_name && ` - ${warehouse.organization_name}`}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">{t('partUsage.selectWarehouseHelp')}</p>
        </div>

        {/* Step 2: Select Part (only show parts available in selected warehouse) */}
        <div>
          <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.step2Part')} <span className="text-red-500">*</span>
          </label>
          <select
            id="part_id"
            name="part_id"
            value={formData.part_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading || !formData.from_warehouse_id}
            required
          >
            <option value="">
              {formData.from_warehouse_id 
                ? (warehouseInventory.length > 0 ? t('partUsage.selectAPart') : t('partUsage.noPartsAvailable'))
                : t('partUsage.selectWarehouseFirst')}
            </option>
            {warehouseInventory.map(inventoryItem => {
              // Use part info from inventory item if available, otherwise lookup
              const partInfo = inventoryItem.part_name ? {
                id: inventoryItem.part_id,
                part_number: inventoryItem.part_number || inventoryItem.part_id,
                name: inventoryItem.part_name,
                unit_of_measure: inventoryItem.unit_of_measure
              } : (Array.isArray(parts) ? parts.find(p => p.id === inventoryItem.part_id) : null);
              
              if (!partInfo) {
                console.log('Part info not available for:', inventoryItem.part_id);
                return null;
              }
              
              const stock = inventoryItem.current_stock || inventoryItem.quantity || 0;
              return (
                <option key={partInfo.id} value={partInfo.id}>
                  {partInfo.part_number} - {partInfo.name} ({stock} {partInfo.unit_of_measure} {t('partUsage.available')})
                </option>
              );
            })}
          </select>
          {selectedPartInventory && (
            <p className="text-xs text-gray-600 mt-1">
              {t('partUsage.availableInStock')}: <span className="font-semibold">{selectedPartInventory.current_stock || selectedPartInventory.quantity || 0}</span> {selectedPart?.unit_of_measure}
            </p>
          )}
        </div>

        {/* Step 3: Select Machine */}
        <div>
          <label htmlFor="machine_id" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.step3ToMachine')} <span className="text-red-500">*</span>
            {initialMachineId && <span className="text-blue-600 ml-2">{t('partUsage.preSelected')}</span>}
          </label>
          <select
            id="machine_id"
            name="machine_id"
            value={formData.machine_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            disabled={loading || !formData.part_id || !!initialMachineId}
            required
          >
            <option value="">
              {formData.part_id ? t('partUsage.selectDestinationMachine') : t('partUsage.selectPartFirst')}
            </option>
            {Array.isArray(machines) && machines.map(machine => (
              <option key={machine.id} value={machine.id}>
                {machine.serial_number} - {machine.model}
                {machine.name && ` (${machine.name})`}
                {user.role === 'super_admin' && machine.organization_name && ` - ${machine.organization_name}`}
              </option>
            ))}
          </select>
          {initialMachineId ? (
            <p className="text-xs text-blue-600 mt-1">
              {t('partUsage.machinePreSelectedHelp')}
            </p>
          ) : (
            <p className="text-xs text-gray-500 mt-1">{t('partUsage.selectMachineHelp')}</p>
          )}
        </div>

        {/* Inventory availability display */}
        {selectedPartInventory && formData.part_id && formData.from_warehouse_id && (
          <div className="bg-blue-50 p-3 rounded-md">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-blue-800">
                <strong>{t('partUsage.availableInventory')}:</strong> {selectedPartInventory.quantity} {selectedPart?.unit_of_measure}
                {selectedPartInventory.quantity === 0 && (
                  <span className="text-red-600 ml-2">{t('partUsage.noStockAvailable')}</span>
                )}
              </span>
            </div>
          </div>
        )}

        <div>
          <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.quantityUsed')} <span className="text-red-500">*</span>
            {selectedPart && (
              <span className="text-sm text-gray-500 ml-2">
                ({selectedPart.part_type === 'consumable' ? t('partUsage.wholeUnits') : t('partUsage.decimalAllowed')})
              </span>
            )}
          </label>
          <QuantityInput
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            partType={selectedPart?.part_type || 'consumable'}
            unitOfMeasure={selectedPart?.unit_of_measure || 'pieces'}
            min={selectedPart?.part_type === 'bulk_material' ? 0.001 : 1}
            max={selectedPartInventory?.quantity}
            required
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="usage_date" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.usageDate')} <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            id="usage_date"
            name="usage_date"
            value={formData.usage_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required
          />
        </div>

        <div>
          <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.referenceNumber')}
          </label>
          <input
            type="text"
            id="reference_number"
            name="reference_number"
            value={formData.reference_number}
            onChange={handleChange}
            placeholder={t('partUsage.referenceNumberPlaceholder')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partUsage.notes')}
          </label>
          <textarea
            id="notes"
            name="notes"
            rows="3"
            value={formData.notes}
            onChange={handleChange}
            placeholder={t('partUsage.notesPlaceholder')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          />
        </div>

        {/* Summary section */}
        {formData.machine_id && formData.part_id && formData.quantity && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">{t('partUsage.usageSummary')}</h4>
            <div className="text-sm text-gray-700 space-y-1">
              <div>
                <strong>{t('partUsage.machine')}:</strong> {selectedMachine?.serial_number} - {selectedMachine?.model}
              </div>
              <div>
                <strong>{t('partUsage.part')}:</strong> {selectedPart?.name} ({selectedPart?.part_number})
              </div>
              <div>
                <strong>{t('partUsage.quantity')}:</strong> {formData.quantity} {selectedPart?.unit_of_measure}
              </div>
              <div>
                <strong>{t('partUsage.from')}:</strong> {selectedWarehouse?.name}
              </div>
              <div>
                <strong>{t('partUsage.date')}:</strong> {new Date(formData.usage_date).toLocaleDateString()}
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            disabled={loading}
          >
            {t('common.cancel')}
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            disabled={loading || !organizationalBoundaryValid || (selectedPartInventory && selectedPartInventory.quantity === 0)}
          >
            {loading ? t('partUsage.recording') : t('partUsage.recordUsage')}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default PartUsageRecorder;