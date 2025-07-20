// frontend/src/components/PartUsageChart.js

import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const PartUsageChart = ({ usageData }) => {
  const chartData = useMemo(() => {
    if (!usageData || usageData.length === 0) return [];

    // Group usage by part name and sum quantities
    const partUsage = usageData.reduce((acc, usage) => {
      const partName = usage.part_name || 'Unknown Part';
      if (!acc[partName]) {
        acc[partName] = {
          name: partName,
          quantity: 0,
          unit: usage.unit_of_measure || 'units'
        };
      }
      acc[partName].quantity += parseFloat(usage.quantity || 0);
      return acc;
    }, {});

    return Object.values(partUsage).sort((a, b) => b.quantity - a.quantity);
  }, [usageData]);

  const monthlyUsage = useMemo(() => {
    if (!usageData || usageData.length === 0) return [];

    // Group usage by month
    const monthlyData = usageData.reduce((acc, usage) => {
      const date = new Date(usage.usage_date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });

      if (!acc[monthKey]) {
        acc[monthKey] = {
          month: monthName,
          quantity: 0
        };
      }
      acc[monthKey].quantity += parseFloat(usage.quantity || 0);
      return acc;
    }, {});

    return Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));
  }, [usageData]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  if (!usageData || usageData.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No usage data available for charts
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Parts Usage Bar Chart */}
      <div className="bg-white p-4 rounded-lg border">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">Parts Usage by Type</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={80}
              fontSize={12}
            />
            <YAxis />
            <Tooltip
              formatter={(value, name) => [`${value} units`, 'Quantity Used']}
              labelFormatter={(label) => `Part: ${label}`}
            />
            <Bar dataKey="quantity" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Usage Trend */}
      {monthlyUsage.length > 1 && (
        <div className="bg-white p-4 rounded-lg border">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Monthly Usage Trend</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyUsage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value) => [`${value} units`, 'Total Usage']}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Bar dataKey="quantity" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Parts Distribution Pie Chart */}
      {chartData.length > 1 && (
        <div className="bg-white p-4 rounded-lg border">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Parts Usage Distribution</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="quantity"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} units`, 'Quantity']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Usage Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {usageData.length}
          </div>
          <div className="text-sm text-gray-600">Total Usage Records</div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {chartData.length}
          </div>
          <div className="text-sm text-gray-600">Different Parts Used</div>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {usageData.reduce((sum, usage) => sum + parseFloat(usage.quantity || 0), 0).toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Total Quantity Used</div>
        </div>
      </div>
    </div>
  );
};

export default PartUsageChart;