import React, { useState, useEffect, useCallback } from 'react';
import { stocktakeService } from '../services/stocktakeService';

const Stocktake = () => {
    const [locations, setLocations] = useState([]);
    const [selectedLocation, setSelectedLocation] = useState('');
    const [worksheet, setWorksheet] = useState(null);
    const [error, setError] = useState('');
    const [isLoadingLocations, setIsLoadingLocations] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);

    useEffect(() => {
        const fetchLocations = async () => {
            setError('');
            setIsLoadingLocations(true);
            try {
                const data = await stocktakeService.getLocations();
                setLocations(data);
            } catch (err) {
                setError(err.message || 'Failed to fetch stocktake locations.');
            } finally {
                setIsLoadingLocations(false);
            }
        };

        fetchLocations();
    }, []);

    const handleGenerateWorksheet = useCallback(async (e) => {
        e.preventDefault();
        if (!selectedLocation) {
            setError('Please select a location.');
            return;
        }
        setIsGenerating(true);
        setError('');
        setWorksheet(null);

        try {
            const result = await stocktakeService.generateWorksheet(selectedLocation);
            setWorksheet(result.data);
        } catch (err) {
            setError(err.message || 'Failed to generate worksheet.');
        } finally {
            setIsGenerating(false);
        }
    }, [selectedLocation]);

    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Stocktake</h1>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            )}

            <form onSubmit={handleGenerateWorksheet} className="bg-white p-6 rounded-lg shadow-md mb-6">
                <div className="mb-4">
                    <label htmlFor="location-select" className="block text-gray-700 text-sm font-bold mb-2">
                        Select Location
                    </label>
                    <div className="flex">
                        {isLoadingLocations ? (
                            <p className="text-gray-500">Loading locations...</p>
                        ) : (
                            <>
                                <select
                                    id="location-select"
                                    value={selectedLocation}
                                    onChange={(e) => setSelectedLocation(e.target.value)}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    disabled={isGenerating || locations.length === 0}
                                >
                                    <option value="">-- Choose a location --</option>
                                    {locations.map((loc) => (
                                        <option key={loc.name} value={loc.name}>{loc.name}</option>
                                    ))}
                                </select>
                                <button
                                    type="submit"
                                    className="ml-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-blue-300"
                                    disabled={isGenerating || !selectedLocation}
                                >
                                    {isGenerating ? 'Generating...' : 'Generate Worksheet'}
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </form>

            {worksheet && (
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">Worksheet for: {selectedLocation}</h2>
                    <div className="overflow-x-auto">
                        <table className="min-w-full bg-white">
                            <thead className="bg-gray-200">
                                <tr>
                                    <th className="text-left py-3 px-4 uppercase font-semibold text-sm w-1/4">Part Number</th>
                                    <th className="text-left py-3 px-4 uppercase font-semibold text-sm w-2/4">Name</th>
                                    <th className="text-center py-3 px-4 uppercase font-semibold text-sm w-1/4">Current Stock</th>
                                    <th className="text-left py-3 px-4 uppercase font-semibold text-sm w-1/4">Counted Stock</th>
                                </tr>
                            </thead>
                            <tbody className="text-gray-700">
                                {worksheet.map((item) => (
                                    <tr key={item.id} className="border-b">
                                        <td className="text-left py-3 px-4">{item.part.part_number}</td>
                                        <td className="text-left py-3 px-4">{item.part.name}</td>
                                        <td className="text-center py-3 px-4">{item.current_stock}</td>
                                        <td className="py-3 px-4">
                                            <input type="number" className="shadow-inner appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Stocktake;

