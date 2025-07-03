import React, { useState, useEffect } from '''react''';
import { useAuth } from '''../AuthContext''';

const Stocktake = () => {
    const [locations, setLocations] = useState([]);
    const [selectedLocation, setSelectedLocation] = useState('''''');
    const [worksheet, setWorksheet] = useState(null);
    const { token } = useAuth();

    useEffect(() => {
        const fetchLocations = async () => {
            try {
                const response = await fetch('''http://localhost:8000/stocktake/locations''', {
                    headers: {
                        '''Authorization''': `Bearer ${token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setLocations(data);
                } else {
                    console.error('''Failed to fetch locations''');
                }
            } catch (error) {
                console.error('''Error fetching locations:''', error);
            }
        };

        fetchLocations();
    }, [token]);

    const handleGenerateWorksheet = async () => {
        if (!selectedLocation) return;

        try {
            const response = await fetch('''http://localhost:8000/stocktake/worksheet''', {
                method: '''POST''',
                headers: {
                    '''Content-Type''': '''application/json''',
                    '''Authorization''': `Bearer ${token}`,
                },
                body: JSON.stringify({ name: selectedLocation }),
            });

            if (response.ok) {
                const data = await response.json();
                setWorksheet(data.data);
            } else {
                console.error('''Failed to generate worksheet''');
            }
        } catch (error) {
            console.error('''Error generating worksheet:''', error);
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Stocktake</h1>
            <div className="mb-4">
                <label htmlFor="location" className="block text-sm font-medium text-gray-700">Select Location</label>
                <select
                    id="location"
                    name="location"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                >
                    <option value="">--Please choose a location--</option>
                    {locations.map((loc) => (
                        <option key={loc.name} value={loc.name}>
                            {loc.name}
                        </option>
                    ))}
                </select>
            </div>
            <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                disabled={!selectedLocation}
                onClick={handleGenerateWorksheet}
            >
                Generate Stocktake Worksheet
            </button>

            {worksheet && (
                <div className="mt-8">
                    <h2 className="text-xl font-bold mb-4">Stocktake Worksheet for {selectedLocation}</h2>
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Part ID</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Stock</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {worksheet.map((item) => (
                                <tr key={item.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.part_id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.current_stock}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.location}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Stocktake;