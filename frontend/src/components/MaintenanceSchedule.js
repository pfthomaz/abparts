// frontend/src/components/MaintenanceSchedule.js

import React, { useMemo } from 'react';
import { useAuth } from '../AuthContext';
import { getContextualPermissions } from '../utils/permissions';

const MaintenanceSchedule = ({ machine, maintenanceHistory, onScheduleUpdate }) => {
  // const [selectedSchedule, setSelectedSchedule] = useState(null);
  // const [showScheduleForm, setShowScheduleForm] = useState(false);

  const { user } = useAuth();
  const permissions = getContextualPermissions(user, 'machines');

  // Calculate maintenance recommendations based on history and machine type
  const maintenanceRecommendations = useMemo(() => {
    const recommendations = [];
    const now = new Date();
    const lastMaintenance = maintenanceHistory.length > 0 ?
      new Date(Math.max(...maintenanceHistory.map(m => new Date(m.maintenance_date)))) :
      new Date(machine.purchase_date || now);

    // Standard maintenance intervals based on machine model
    const intervals = {
      'V3.1B': {
        routine: 30, // days
        preventive: 90,
        inspection: 180,
        deep_clean: 365
      },
      'V4.0': {
        routine: 45, // days
        preventive: 120,
        inspection: 180,
        deep_clean: 365
      }
    };

    const machineIntervals = intervals[machine.model_type] || intervals['V3.1B'];

    Object.entries(machineIntervals).forEach(([type, days]) => {
      const nextDate = new Date(lastMaintenance);
      nextDate.setDate(nextDate.getDate() + days);

      const daysDiff = Math.ceil((nextDate - now) / (1000 * 60 * 60 * 24));
      const isOverdue = daysDiff < 0;
      const isDueSoon = daysDiff <= 7 && daysDiff >= 0;

      recommendations.push({
        type: type.replace('_', ' ').toUpperCase(),
        dueDate: nextDate,
        daysDiff,
        isOverdue,
        isDueSoon,
        priority: isOverdue ? 'high' : isDueSoon ? 'medium' : 'low',
        description: getMaintenanceDescription(type)
      });
    });

    return recommendations.sort((a, b) => a.daysDiff - b.daysDiff);
  }, [machine, maintenanceHistory]);

  const getMaintenanceDescription = (type) => {
    const descriptions = {
      routine: 'Basic cleaning, lubrication, and visual inspection',
      preventive: 'Comprehensive system check, filter replacement, calibration',
      inspection: 'Detailed safety and performance inspection',
      deep_clean: 'Complete disassembly, deep cleaning, and component replacement'
    };
    return descriptions[type] || 'Standard maintenance procedure';
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusText = (recommendation) => {
    if (recommendation.isOverdue) {
      return `Overdue by ${Math.abs(recommendation.daysDiff)} days`;
    } else if (recommendation.isDueSoon) {
      return `Due in ${recommendation.daysDiff} days`;
    } else {
      return `Due in ${recommendation.daysDiff} days`;
    }
  };

  return (
    <div className="space-y-6">
      {/* Schedule Overview */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Maintenance Schedule Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {maintenanceRecommendations.filter(r => r.isOverdue).length}
            </div>
            <div className="text-sm text-gray-600">Overdue</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {maintenanceRecommendations.filter(r => r.isDueSoon).length}
            </div>
            <div className="text-sm text-gray-600">Due Soon</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {maintenanceRecommendations.filter(r => r.priority === 'low').length}
            </div>
            <div className="text-sm text-gray-600">Scheduled</div>
          </div>
        </div>
      </div>

      {/* Maintenance Recommendations */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Upcoming Maintenance</h3>
          {permissions.canManage && (
            <button
              onClick={() => {/* setShowScheduleForm(true) */ }}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
            >
              Schedule Maintenance
            </button>
          )}
        </div>

        <div className="space-y-4">
          {maintenanceRecommendations.map((recommendation, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${getPriorityColor(recommendation.priority)}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-semibold">{recommendation.type}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${recommendation.isOverdue ? 'bg-red-200 text-red-800' :
                      recommendation.isDueSoon ? 'bg-yellow-200 text-yellow-800' :
                        'bg-blue-200 text-blue-800'
                      }`}>
                      {recommendation.isOverdue ? 'OVERDUE' :
                        recommendation.isDueSoon ? 'DUE SOON' : 'SCHEDULED'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{recommendation.description}</p>
                  <div className="flex items-center space-x-4 text-sm">
                    <span><strong>Due Date:</strong> {formatDate(recommendation.dueDate)}</span>
                    <span><strong>Status:</strong> {getStatusText(recommendation)}</span>
                  </div>
                </div>
                {permissions.canManage && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {/* setSelectedSchedule(recommendation) */ }}
                      className="bg-white text-gray-700 px-3 py-1 rounded border hover:bg-gray-50 text-sm"
                    >
                      Schedule
                    </button>
                    <button
                      onClick={() => {/* Handle mark as complete */ }}
                      className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-sm"
                    >
                      Complete
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Maintenance History */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Maintenance History</h3>
        {maintenanceHistory.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No maintenance history available
          </div>
        ) : (
          <div className="space-y-3">
            {maintenanceHistory.slice(0, 5).map((record) => (
              <div key={record.id} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-800">
                      {record.maintenance_type?.toUpperCase() || 'MAINTENANCE'}
                    </h4>
                    <p className="text-sm text-gray-600">{formatDate(new Date(record.maintenance_date))}</p>
                    {record.description && (
                      <p className="text-sm text-gray-700 mt-1">{record.description}</p>
                    )}
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    {record.duration_hours && <div>{record.duration_hours}h</div>}
                    {record.cost && <div>${record.cost}</div>}
                  </div>
                </div>
              </div>
            ))}
            {maintenanceHistory.length > 5 && (
              <div className="text-center">
                <button className="text-blue-600 hover:text-blue-800 text-sm">
                  View all {maintenanceHistory.length} records
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Maintenance Tips */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">Maintenance Tips</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Regular cleaning prevents buildup and extends machine life</li>
          <li>• Check filters monthly and replace when dirty</li>
          <li>• Monitor unusual noises or vibrations during operation</li>
          <li>• Keep maintenance logs for warranty and troubleshooting</li>
          <li>• Use only approved parts and cleaning solutions</li>
        </ul>
      </div>
    </div>
  );
};

export default MaintenanceSchedule;