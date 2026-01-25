// frontend/src/pages/NetCleaningRecords.js

import { useState, useEffect, useCallback, useMemo } from 'react';
import netCleaningRecordsService from '../services/netCleaningRecordsService';
import netsService from '../services/netsService';
import farmSitesService from '../services/farmSitesService';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import Modal from '../components/Modal';
import NetCleaningRecordForm from '../components/NetCleaningRecordForm';

const NetCleaningRecords = () => {
  const [records, setRecords] = useState([]);
  const [nets, setNets] = useState([]);
  const [farmSites, setFarmSites] = useState([]);
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [filterNetId, setFilterNetId] = useState('all');
  const [filterFarmSiteId, setFilterFarmSiteId] = useState('all');

  const { user } = useAuth();
  const { t } = useTranslation();
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [recordsData, netsData, farmSitesData, machinesData] = await Promise.all([
        netCleaningRecordsService.getCleaningRecords(),
        netsService.getNets(),
        farmSitesService.getFarmSites(),
        machinesService.getMachines()
      ]);
      setRecords(recordsData);
      setNets(netsData);
      setFarmSites(farmSitesData);
      setMachines(machinesData);
    } catch (err) {
      setError(err.message || 'Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const netsMap = useMemo(() => new Map(nets.map(n => [n.id, n])), [nets]);
  const farmSitesMap = useMemo(() => new Map(farmSites.map(fs => [fs.id, fs])), [farmSites]);
  const machinesMap = useMemo(() => new Map(machines.map(m => [m.id, m])), [machines]);

  const filteredRecords = useMemo(() => {
    return records
      .map(record => {
        const net = netsMap.get(record.net_id);
        const farmSite = net ? farmSitesMap.get(net.farm_site_id) : null;
        const machine = record.machine_id ? machinesMap.get(record.machine_id) : null;
        return {
          ...record,
          netName: net?.name || 'Unknown',
          farmSiteName: farmSite?.name || 'Unknown',
          machineName: machine?.name || 'N/A',
          farmSiteId: net?.farm_site_id
        };
      })
      .filter(record => {
        if (filterNetId !== 'all' && record.net_id !== filterNetId) return false;
        if (filterFarmSiteId !== 'all' && record.farmSiteId !== filterFarmSiteId) return false;
        return true;
      });
  }, [records, netsMap, farmSitesMap, machinesMap, filterNetId, filterFarmSiteId]);

  const handleCreateOrUpdate = async (recordData) => {
    try {
      if (editingRecord) {
        await netCleaningRecordsService.updateCleaningRecord(editingRecord.id, recordData);
      } else {
        await netCleaningRecordsService.createCleaningRecord(recordData);
      }
      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating cleaning record:", err);
      throw err;
    }
  };

  const handleDelete = async (recordId) => {
    if (!window.confirm(t('netCleaning.records.confirmDelete'))) {
      return;
    }
    setError(null);
    try {
      await netCleaningRecordsService.deleteCleaningRecord(recordId);
      await fetchData();
    } catch (err) {
      setError(err.message || t('netCleaning.records.failedToDelete'));
    }
  };

  const openModal = (record = null) => {
    setEditingRecord(record);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingRecord(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">{t('netCleaning.records.loading')}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">{t('netCleaning.records.title')}</h1>
        <button
          onClick={() => openModal()}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          {t('netCleaning.records.addRecord')}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <select
          value={filterFarmSiteId}
          onChange={(e) => {
            setFilterFarmSiteId(e.target.value);
            setFilterNetId('all');
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">{t('netCleaning.records.allFarmSites')}</option>
          {farmSites.map(site => (
            <option key={site.id} value={site.id}>{site.name}</option>
          ))}
        </select>

        <select
          value={filterNetId}
          onChange={(e) => setFilterNetId(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">{t('netCleaning.records.allNets')}</option>
          {nets
            .filter(net => filterFarmSiteId === 'all' || net.farm_site_id === filterFarmSiteId)
            .map(net => (
              <option key={net.id} value={net.id}>{net.name}</option>
            ))}
        </select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.date')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.farmSite')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.net')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.operator')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.mode')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.duration')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('netCleaning.records.actions')}</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredRecords.map((record) => {
              const isIncomplete = record.status === 'in_progress';
              return (
                <tr key={record.id} className={`hover:bg-gray-50 ${isIncomplete ? 'bg-yellow-50' : ''}`}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      <span>{new Date(record.start_time).toLocaleDateString()}</span>
                      {isIncomplete && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          {t('netCleaning.records.inProgress')}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.farmSiteName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.netName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.operator_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {t('netCleaning.records.mode')} {record.cleaning_mode}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.duration_minutes ? `${record.duration_minutes} ${t('netCleaning.records.min')}` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => openModal(record)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      {t('common.edit')}
                    </button>
                    {isAdmin && (
                      <button
                        onClick={() => handleDelete(record.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        {t('common.delete')}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {filteredRecords.length === 0 && (
        <div className="text-center text-gray-500 py-12">
          {t('netCleaning.records.noRecordsFound')}
        </div>
      )}

      {showModal && (
        <Modal isOpen={showModal} onClose={closeModal} title={editingRecord ? t('netCleaning.records.editRecord') : t('netCleaning.records.addNewRecord')}>
          <NetCleaningRecordForm
            record={editingRecord}
            nets={nets}
            farmSites={farmSites}
            machines={machines}
            onSubmit={handleCreateOrUpdate}
            onCancel={closeModal}
          />
        </Modal>
      )}
    </div>
  );
};

export default NetCleaningRecords;
