// frontend/src/pages/Nets.js

import { useState, useEffect, useCallback, useMemo } from 'react';
import netsService from '../services/netsService';
import farmSitesService from '../services/farmSitesService';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import Modal from '../components/Modal';
import NetForm from '../components/NetForm';

const Nets = () => {
  const [nets, setNets] = useState([]);
  const [farmSites, setFarmSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingNet, setEditingNet] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFarmSiteId, setFilterFarmSiteId] = useState('all');

  const { user } = useAuth();
  const { t } = useTranslation();
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [netsData, farmSitesData] = await Promise.all([
        netsService.getNets(),
        farmSitesService.getFarmSites()
      ]);
      setNets(netsData);
      setFarmSites(farmSitesData);
    } catch (err) {
      setError(err.message || 'Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const farmSitesMap = useMemo(() => {
    return new Map(farmSites.map(fs => [fs.id, fs]));
  }, [farmSites]);

  const filteredNets = useMemo(() => {
    return nets
      .map(net => ({
        ...net,
        farmSiteName: farmSitesMap.get(net.farm_site_id)?.name || 'Unknown'
      }))
      .filter(net => {
        if (filterFarmSiteId !== 'all' && net.farm_site_id !== filterFarmSiteId) {
          return false;
        }
        if (searchTerm) {
          const term = searchTerm.toLowerCase();
          return net.name.toLowerCase().includes(term) ||
                 net.farmSiteName.toLowerCase().includes(term);
        }
        return true;
      });
  }, [nets, farmSitesMap, searchTerm, filterFarmSiteId]);

  const handleCreateOrUpdate = async (netData) => {
    try {
      if (editingNet) {
        await netsService.updateNet(editingNet.id, netData);
      } else {
        await netsService.createNet(netData);
      }
      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating net:", err);
      throw err;
    }
  };

  const handleDelete = async (netId) => {
    if (!window.confirm(t('netCleaning.nets.confirmDelete'))) {
      return;
    }
    setError(null);
    try {
      await netsService.deleteNet(netId);
      await fetchData();
    } catch (err) {
      setError(err.message || t('netCleaning.nets.failedToDelete'));
    }
  };

  const openModal = (net = null) => {
    setEditingNet(net);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingNet(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">{t('netCleaning.nets.loading')}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">{t('netCleaning.nets.title')}</h1>
        {isAdmin && (
          <button
            onClick={() => openModal()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            {t('netCleaning.nets.addNet')}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <input
          type="text"
          placeholder={t('netCleaning.nets.searchPlaceholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <select
          value={filterFarmSiteId}
          onChange={(e) => setFilterFarmSiteId(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">{t('netCleaning.nets.allFarmSites')}</option>
          {farmSites.map(site => (
            <option key={site.id} value={site.id}>{site.name}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredNets.map((net) => (
          <div key={net.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-800">{net.name}</h3>
                <p className="text-sm text-gray-500">{net.farmSiteName}</p>
              </div>
              {!net.active && (
                <span className="bg-gray-200 text-gray-600 text-xs px-2 py-1 rounded">{t('netCleaning.nets.inactive')}</span>
              )}
            </div>
            
            <div className="space-y-1 text-sm text-gray-600 mb-4">
              {net.diameter && <p>{t('netCleaning.nets.diameter')}: {net.diameter}m</p>}
              {net.vertical_depth && <p>{t('netCleaning.nets.verticalDepth')}: {net.vertical_depth}m</p>}
              {net.cone_depth && <p>{t('netCleaning.nets.coneDepth')}: {net.cone_depth}m</p>}
              {net.mesh_size && <p>{t('netCleaning.nets.mesh')}: {net.mesh_size}</p>}
              {net.material && <p>{t('netCleaning.nets.material')}: {net.material}</p>}
            </div>
            
            <div className="text-sm text-gray-500 mb-4">
              {net.cleaning_records_count || 0} {t('netCleaning.nets.cleanings')}
              {net.last_cleaning_date && (
                <span className="block">{t('netCleaning.nets.last')}: {new Date(net.last_cleaning_date).toLocaleDateString()}</span>
              )}
            </div>

            {isAdmin && (
              <div className="flex gap-2">
                <button
                  onClick={() => openModal(net)}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded text-sm"
                >
                  {t('common.edit')}
                </button>
                <button
                  onClick={() => handleDelete(net.id)}
                  className="flex-1 bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded text-sm"
                >
                  {t('common.delete')}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredNets.length === 0 && (
        <div className="text-center text-gray-500 py-12">
          {searchTerm || filterFarmSiteId !== 'all' ? t('netCleaning.nets.noNetsFound') : t('netCleaning.nets.noNetsYet')}
        </div>
      )}

      {showModal && (
        <Modal isOpen={showModal} onClose={closeModal} title={editingNet ? t('netCleaning.nets.editNet') : t('netCleaning.nets.addNewNet')}>
          <NetForm
            net={editingNet}
            farmSites={farmSites}
            onSubmit={handleCreateOrUpdate}
            onCancel={closeModal}
          />
        </Modal>
      )}
    </div>
  );
};

export default Nets;
