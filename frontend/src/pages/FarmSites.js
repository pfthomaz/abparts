// frontend/src/pages/FarmSites.js

import { useState, useEffect, useCallback, useMemo } from 'react';
import farmSitesService from '../services/farmSitesService';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import Modal from '../components/Modal';
import FarmSiteForm from '../components/FarmSiteForm';
import NetForm from '../components/NetForm';

const FarmSites = () => {
  const [farmSites, setFarmSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingFarmSite, setEditingFarmSite] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNetModal, setShowNetModal] = useState(false);
  const [selectedFarmSiteForNet, setSelectedFarmSiteForNet] = useState(null);

  const { user } = useAuth();
  const { t } = useTranslation();
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';

  const fetchFarmSites = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await farmSitesService.getFarmSites();
      setFarmSites(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch farm sites.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFarmSites();
  }, [fetchFarmSites]);

  const filteredFarmSites = useMemo(() => {
    if (!searchTerm) return farmSites;
    const term = searchTerm.toLowerCase();
    return farmSites.filter(site =>
      site.name.toLowerCase().includes(term) ||
      (site.location && site.location.toLowerCase().includes(term))
    );
  }, [farmSites, searchTerm]);

  const handleCreateOrUpdate = async (farmSiteData) => {
    try {
      if (editingFarmSite) {
        await farmSitesService.updateFarmSite(editingFarmSite.id, farmSiteData);
      } else {
        await farmSitesService.createFarmSite(farmSiteData);
      }
      await fetchFarmSites();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating farm site:", err);
      throw err;
    }
  };

  const handleDelete = async (farmSiteId) => {
    if (!window.confirm(t('netCleaning.farmSites.confirmDelete'))) {
      return;
    }
    setError(null);
    try {
      await farmSitesService.deleteFarmSite(farmSiteId);
      await fetchFarmSites();
    } catch (err) {
      setError(err.message || t('netCleaning.farmSites.failedToDelete'));
    }
  };

  const openModal = (farmSite = null) => {
    setEditingFarmSite(farmSite);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingFarmSite(null);
  };

  const openNetModal = (farmSite) => {
    setSelectedFarmSiteForNet(farmSite);
    setShowNetModal(true);
  };

  const closeNetModal = () => {
    setShowNetModal(false);
    setSelectedFarmSiteForNet(null);
  };

  const handleNetCreate = async (netData) => {
    try {
      // Import netsService dynamically
      const netsService = (await import('../services/netsService')).default;
      await netsService.createNet(netData);
      await fetchFarmSites(); // Refresh to update nets_count
      closeNetModal();
    } catch (err) {
      console.error("Error creating net:", err);
      throw err;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">{t('netCleaning.farmSites.loading')}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">{t('netCleaning.farmSites.title')}</h1>
        {isAdmin && (
          <button
            onClick={() => openModal()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            {t('netCleaning.farmSites.addFarmSite')}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4">
        <input
          type="text"
          placeholder={t('netCleaning.farmSites.searchPlaceholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFarmSites.map((site) => (
          <div key={site.id} className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold text-gray-800">{site.name}</h3>
              {!site.active && (
                <span className="bg-gray-200 text-gray-600 text-xs px-2 py-1 rounded">{t('netCleaning.farmSites.inactive')}</span>
              )}
            </div>
            
            {site.location && (
              <p className="text-gray-600 text-sm mb-2">
                <span className="font-medium">{t('netCleaning.farmSites.location')}:</span> {site.location}
              </p>
            )}
            
            {site.description && (
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">{site.description}</p>
            )}
            
            <div className="text-sm text-gray-500 mb-3">
              {site.nets_count || 0} {t('netCleaning.farmSites.nets')}
            </div>

            <div className="flex flex-col gap-2">
              {/* Add Cage button - available to all users */}
              <button
                onClick={() => openNetModal(site)}
                className="w-full bg-teal-500 hover:bg-teal-600 text-white px-3 py-1.5 rounded text-sm font-medium"
              >
                + {t('netCleaning.farmSites.addCage')}
              </button>

              {/* Admin buttons */}
              {isAdmin && (
                <div className="flex gap-2">
                  <button
                    onClick={() => openModal(site)}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded text-sm"
                  >
                    {t('common.edit')}
                  </button>
                  <button
                    onClick={() => handleDelete(site.id)}
                    className="flex-1 bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded text-sm"
                  >
                    {t('common.delete')}
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredFarmSites.length === 0 && (
        <div className="text-center text-gray-500 py-12">
          {searchTerm ? t('netCleaning.farmSites.noFarmSitesFound') : t('netCleaning.farmSites.noFarmSitesYet')}
        </div>
      )}

      {showModal && (
        <Modal isOpen={showModal} onClose={closeModal} title={editingFarmSite ? t('netCleaning.farmSites.editFarmSite') : t('netCleaning.farmSites.addNewFarmSite')}>
          <FarmSiteForm
            farmSite={editingFarmSite}
            onSubmit={handleCreateOrUpdate}
            onCancel={closeModal}
          />
        </Modal>
      )}

      {showNetModal && selectedFarmSiteForNet && (
        <Modal isOpen={showNetModal} onClose={closeNetModal} title={t('netCleaning.nets.addNewNet')}>
          <NetForm
            net={null}
            farmSites={[selectedFarmSiteForNet]} // Only pass the selected farm site
            onSubmit={handleNetCreate}
            onCancel={closeNetModal}
            preselectedFarmSiteId={selectedFarmSiteForNet.id} // Pass the preselected ID
          />
        </Modal>
      )}
    </div>
  );
};

export default FarmSites;
