// frontend/src/components/StocktakeWorksheetGenerator.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

const StocktakeWorksheetGenerator = ({ organizations, API_BASE_URL, onWorksheetGenerated, onLoadingChange }) => {
    const { token, user } = useAuth();
    const [selectedOrgId, setSelectedOrgId] = useState('');
    const [error, setError] = useState('');

    // Filter organizations to only include "Oraseas EE" if user is Inventory Manager
    const [availableOrganizations, setAvailableOrganizations] = useState([]);

    useEffect(() => {
        if (user && organizations) {
            if (user.role === 'Oraseas Inventory Manager') {
                const oraseasOrg = organizations.find(org => org.name === 'Oraseas EE');
                setAvailableOrganizations(oraseasOrg ? [oraseasOrg] : []);
                if (oraseasOrg) {
                    setSelectedOrgId(oraseasOrg.id); // Pre-select if only one option
                } else {
                     setError("Oraseas EE organization not found. Cannot generate worksheet.");
                }
            } else if (user.role === 'Oraseas Admin') {
                setAvailableOrganizations(organizations);
            } else {
                setAvailableOrganizations([]); // Should not happen due to button visibility
            }
        }
    }, [user, organizations]);


    const handleGenerate = async () => {
        if (!selectedOrgId) {
            setError('Please select an organization.');
            return;
        }
        setError('');
        if (onLoadingChange) onLoadingChange(true);

        try {
            const response = await fetch(`${API_BASE_URL}/inventory/worksheet/stocktake?organization_id=${selectedOrgId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to generate worksheet: ${response.statusText}`);
            }
            const data = await response.json();
            if (onWorksheetGenerated) {
                onWorksheetGenerated(data);
            }
        } catch (err) {
            console.error("Error generating stocktake worksheet:", err);
            setError(err.message || "An unexpected error occurred.");
            if (onWorksheetGenerated) { // Ensure data is cleared on error
                onWorksheetGenerated([]);
            }
        } finally {
            if (onLoadingChange) onLoadingChange(false);
        }
    };

    if (!user || (user.role !== 'Oraseas Admin' && user.role !== 'Oraseas Inventory Manager')) {
        return <p className="text-red-500">You are not authorized to generate stocktake worksheets.</p>;
    }

    if (user.role === 'Oraseas Inventory Manager' && availableOrganizations.length === 0 && !organizations.find(org => org.name === 'Oraseas EE')) {
         return <p className="text-red-500">Oraseas EE organization not configured. Contact Admin.</p>;
    }


    return (
        <div className="space-y-4">
            <div>
                <label htmlFor="organizationSelect" className="block text-sm font-medium text-gray-700">
                    Select Organization <span className="text-red-500">*</span>
                </label>
                <select
                    id="organizationSelect"
                    value={selectedOrgId}
                    onChange={(e) => setSelectedOrgId(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md disabled:bg-gray-100"
                    disabled={user.role === 'Oraseas Inventory Manager' && availableOrganizations.length === 1}
                >
                    {user.role === 'Oraseas Admin' && <option value="">-- Select an Organization --</option>}
                    {availableOrganizations.map(org => (
                        <option key={org.id} value={org.id}>
                            {org.name} ({org.type})
                        </option>
                    ))}
                </select>
            </div>

            {error && <p className="text-sm text-red-600 bg-red-100 p-2 rounded-md">{error}</p>}

            <button
                onClick={handleGenerate}
                disabled={!selectedOrgId || (onLoadingChange && typeof onLoadingChange === 'function' ? false : true)} // Bit complex, simplify if onLoadingChange is always a prop
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
            >
                Generate Worksheet
            </button>
        </div>
    );
};

export default StocktakeWorksheetGenerator;
