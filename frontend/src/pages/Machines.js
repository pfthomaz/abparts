// c:/abparts/frontend/src/pages/Machines.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { machinesService } from '../services/machinesService';
import { api } from '../services/api'; // For fetching organizations
import { useAuth } from '../AuthContext';
import { getContextualPermissions } from '../utils/permissions';
import Modal from '../components/Modal';
import MachineForm from '../components/MachineForm';
import MachineDetails from '../components/MachineDetails';
import MachineTransferForm from '../components/MachineTransferForm';
import SimpleMachineHoursButton from '../components/SimpleMachineHoursButton';

const Machines = () => {
  const [machines, setMachines] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingMachine, setEditingMachine] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOrgId, setFilterOrgId] = useState('all');
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferMachine, setTransferMachine] = useState(null);

  const { user } = useAuth();
  const permissions = getContextualPermissions(user, 'machines');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [machinesData, orgsData] = await Promise.all([
        machinesService.getMachines(),
        api.get('/organizations'),
      ]);
      setMachines(machinesData);
      setOrganizations(orgsData);
    } catch (err) {
      setError(err.message || 'Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-refresh every 10 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const organizationsMap = useMemo(() => {
    return new Map(organizations.map(o => [o.id, o]));
  }, [organizations]);

  const filteredMachines = useMemo(() => {
    return machines
      .map(machine => {
        // Augment item with organization details for easier filtering and display
        // Using a Map is more performant for lookups than Array.find() in a loop
        const organization = organizationsMap.get(machine.customer_organization_id);
        return {
          ...machine,
          organizationName: organization ? organization.name : 'Unknown',
        };
      })
      .filter(machine => {
        if (filterOrgId === 'all') return true;
        return machine.customer_organization_id === filterOrgId;
      })
      .filter(machine => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return machine.name.toLowerCase().includes(term) || machine.serial_number.toLowerCase().includes(term) || machine.model_type.toLowerCase().includes(term);
      });
  }, [machines, organizationsMap, searchTerm, filterOrgId]);

  const handleCreateOrUpdate = async (machineData) => {
    try {
      if (editingMachine) {
        await machinesService.updateMachine(editingMachine.id, machineData);
      } else {
        await machinesService.createMachine(machineData);
      }
      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating machine:", err);
      throw err; // Re-throw for form error handling
    }
  };

  const handleDelete = async (machineId) => {
    if (!window.confirm("Are you sure you want to delete this machine?")) {
      return;
    }
    setError(null);
    try {
      await machinesService.deleteMachine(machineId);
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to delete machine.');
    }
  };

  const handleTransfer = async (transferData) => {
    try {
      await machinesService.transferMachine(transferData);
      await fetchData();
      setShowTransferModal(false);
      setTransferMachine(null);
    } catch (err) {
      throw err; // Re-throw for form error handling
    }
  };

  const openMachineDetails = (machine) => {
    setSelectedMachine(machine);
    setShowDetailsModal(true);
  };

  const openTransferModal = (machine) => {
    setTransferMachine(machine);
    setShowTransferModal(true);
  };

  const openModal = (machine = null) => {
    setEditingMachine(machine);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingMachine(null);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Machines</h1>
        <div className="flex space-x-2">
          {permissions.canRegister && (
            <button
              onClick={() => openModal()}
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 font-semibold"
            >
              Register Machine
            </button>
          )}
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading machines...</p>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search Machine</label>
            <input
              type="text"
              id="search"
              placeholder="Name, model, or serial..."
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="filterOrganization" className="block text-sm font-medium text-gray-700">Filter by Owner</label>
            <select
              id="filterOrganization"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterOrgId}
              onChange={(e) => setFilterOrgId(e.target.value)}
            >
              <option value="all">All Owners</option>
              {organizations
                .filter(org => org.organization_type === 'customer')
                .map(org => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
            </select>
          </div>
        </div>
      </div>

      {!loading && filteredMachines.length === 0 ? (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700">No Machines Found</h3>
          <p className="text-gray-500 mt-2">
            {machines.length > 0 ? 'Try adjusting your search or filter criteria.' : 'There are no machines in the system yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredMachines.map((machine) => (
            <div key={machine.id} className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-semibold text-gray-800">{machine.name}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${machine.status === 'active' ? 'bg-green-100 text-green-800' :
                  machine.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                    machine.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                      'bg-red-100 text-red-800'
                  }`}>
                  {machine.status || 'Active'}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <p className="text-gray-600"><span className="font-medium">Model:</span> {machine.model_type}</p>
                <p className="text-gray-600"><span className="font-medium">Serial:</span> {machine.serial_number}</p>
                <p className="text-gray-600"><span className="font-medium">Owner:</span> {machine.organizationName}</p>
                
                {/* Debug: Log machine data */}
                {console.log('Machine data:', machine.name, 'latest_hours:', machine.latest_hours, 'type:', typeof machine.latest_hours)}
                
                {/* Latest Machine Hours */}
                {machine.latest_hours !== null && machine.latest_hours !== undefined ? (
                  <div className="bg-blue-50 border border-blue-200 rounded p-2 mt-2">
                    <p className="text-blue-900 text-sm">
                      <span className="font-semibold">Latest Hours:</span> {machine.latest_hours.toLocaleString()} hrs
                    </p>
                    {machine.latest_hours_date && (
                      <p className="text-blue-700 text-xs mt-1">
                        Recorded: {new Date(machine.latest_hours_date).toLocaleDateString()} at {new Date(machine.latest_hours_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded p-2 mt-2">
                    <p className="text-gray-600 text-sm italic">No hours recorded yet</p>
                  </div>
                )}
                
                {machine.last_maintenance_date && (
                  <p className="text-gray-600">
                    <span className="font-medium">Last Maintenance:</span> {' '}
                    {new Date(machine.last_maintenance_date).toLocaleDateString()}
                  </p>
                )}
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => openMachineDetails(machine)}
                  className="bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm flex-1"
                >
                  View Details
                </button>

                <SimpleMachineHoursButton 
                  machineId={machine.id}
                  machineName={machine.name}
                  onHoursSaved={fetchData}
                />

                {permissions.canEdit && (
                  <button
                    onClick={() => openModal(machine)}
                    className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm"
                  >
                    Edit
                  </button>
                )}

                {permissions.canManage && (
                  <button
                    onClick={() => openTransferModal(machine)}
                    className="bg-purple-500 text-white py-1 px-3 rounded-md hover:bg-purple-600 text-sm"
                  >
                    Transfer
                  </button>
                )}

                {permissions.canDelete && (
                  <button
                    onClick={() => handleDelete(machine.id)}
                    className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Machine Form Modal */}
      <Modal isOpen={showModal} onClose={closeModal} title={editingMachine ? "Edit Machine" : "Register New Machine"}>
        <MachineForm
          initialData={editingMachine || {}}
          organizations={organizations.filter(org => org.organization_type === 'customer')}
          onSubmit={handleCreateOrUpdate}
          onClose={closeModal}
        />
      </Modal>

      {/* Machine Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        title="Machine Details"
        size="large"
      >
        {selectedMachine && (
          <MachineDetails
            machineId={selectedMachine.id}
            onClose={() => setShowDetailsModal(false)}
          />
        )}
      </Modal>

      {/* Machine Transfer Modal */}
      <Modal
        isOpen={showTransferModal}
        onClose={() => setShowTransferModal(false)}
        title="Transfer Machine"
      >
        {transferMachine && (
          <MachineTransferForm
            machine={transferMachine}
            onSubmit={handleTransfer}
            onClose={() => setShowTransferModal(false)}
          />
        )}
      </Modal>
    </div>
  );
};

export default Machines;