// frontend/src/components/OrderCalendarView.js

import React, { useState, useMemo } from 'react';
import { 
  subDays, 
  addDays, 
  differenceInDays, 
  eachDayOfInterval, 
  format, 
  isToday,
  isSameDay,
  parseISO
} from 'date-fns';
import Modal from './Modal';

const OrderCalendarView = ({ orders = [], onOrderClick }) => {
  const [centerDate, setCenterDate] = useState(new Date());
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showOrderModal, setShowOrderModal] = useState(false);

  const handleOrderClick = (order) => {
    setSelectedOrder(order);
    setShowOrderModal(true);
    if (onOrderClick) {
      onOrderClick(order);
    }
  };

  const closeModal = () => {
    setShowOrderModal(false);
    setSelectedOrder(null);
  };

  // Calculate date range (15 days before center, 14 days after)
  const dateRange = useMemo(() => ({
    start: subDays(centerDate, 15),
    end: addDays(centerDate, 14)
  }), [centerDate]);

  const days = useMemo(() => 
    eachDayOfInterval(dateRange), 
    [dateRange]
  );

  const goBack = () => setCenterDate(subDays(centerDate, 30));
  const goForward = () => setCenterDate(addDays(centerDate, 30));
  const goToday = () => setCenterDate(new Date());

  // Filter orders that fall within the visible date range
  const visibleOrders = useMemo(() => {
    return orders.filter(order => {
      const orderDate = parseISO(order.order_date);
      const endDate = order.actual_delivery_date 
        ? parseISO(order.actual_delivery_date)
        : order.expected_delivery_date 
          ? parseISO(order.expected_delivery_date)
          : dateRange.end;
      
      // Show order if it overlaps with visible range
      return orderDate <= dateRange.end && endDate >= dateRange.start;
    });
  }, [orders, dateRange]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Pending': return 'bg-blue-500 hover:bg-blue-600';
      case 'Shipped': return 'bg-yellow-500 hover:bg-yellow-600';
      case 'Delivered':
      case 'Received': return 'bg-green-500 hover:bg-green-600';
      case 'Cancelled': return 'bg-red-300 opacity-50';
      default: return 'bg-gray-500 hover:bg-gray-600';
    }
  };

  const calculateBarPosition = (order) => {
    const totalDays = differenceInDays(dateRange.end, dateRange.start);
    const orderDate = parseISO(order.order_date);
    const endDate = order.actual_delivery_date 
      ? parseISO(order.actual_delivery_date)
      : order.expected_delivery_date 
        ? parseISO(order.expected_delivery_date)
        : dateRange.end;

    const startOffset = Math.max(0, differenceInDays(orderDate, dateRange.start));
    const endOffset = Math.min(totalDays, differenceInDays(endDate, dateRange.start));

    return {
      left: (startOffset / totalDays) * 100,
      width: Math.max(2, ((endOffset - startOffset) / totalDays) * 100) // Minimum 2% width
    };
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header with Navigation */}
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={goBack}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm font-medium"
        >
          ◄ Previous 30 Days
        </button>
        <div className="text-center">
          <button
            onClick={goToday}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-semibold"
          >
            Today: {format(new Date(), 'MMM dd, yyyy')}
          </button>
        </div>
        <button
          onClick={goForward}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm font-medium"
        >
          Next 30 Days ►
        </button>
      </div>

      {/* Date Range Display */}
      <div className="text-center text-gray-600 mb-4">
        Showing: {format(dateRange.start, 'MMM dd')} - {format(dateRange.end, 'MMM dd, yyyy')}
      </div>

      {/* Calendar Grid */}
      <div className="relative border-t border-gray-300">
        {/* Date Axis */}
        <div className="relative h-16 border-b-2 border-gray-400 bg-gray-50">
          {days.map((day, index) => {
            const isCurrentDay = isToday(day);
            const showLabel = index % 3 === 0 || isCurrentDay; // Show every 3rd day or today
            
            return (
              <div
                key={index}
                className="absolute"
                style={{ left: `${(index / days.length) * 100}%` }}
              >
                {/* Vertical line */}
                <div className={`w-px h-16 ${isCurrentDay ? 'bg-red-500' : 'bg-gray-300'}`} />
                
                {/* Date label */}
                {showLabel && (
                  <div className={`absolute top-1 -translate-x-1/2 text-xs font-medium whitespace-nowrap ${
                    isCurrentDay ? 'text-red-600 font-bold' : 'text-gray-600'
                  }`}>
                    {format(day, 'MMM dd')}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Order Bars */}
        <div className="relative" style={{ minHeight: '400px' }}>
          {visibleOrders.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              No orders in this date range
            </div>
          ) : (
            visibleOrders.map((order, index) => {
              const { left, width } = calculateBarPosition(order);
              const color = getStatusColor(order.status);
              
              return (
                <div
                  key={order.id}
                  className={`absolute h-10 rounded-md cursor-pointer ${color} shadow-md transition-all duration-200 flex items-center px-2 text-white text-sm font-medium`}
                  style={{
                    left: `${left}%`,
                    width: `${width}%`,
                    top: `${index * 50 + 20}px`,
                    minWidth: '60px'
                  }}
                  onClick={() => handleOrderClick(order)}
                  title={`Order #${order.id.slice(0, 8)}
Customer: ${order.customer_organization_name || 'N/A'}
Status: ${order.status}
Ordered: ${format(parseISO(order.order_date), 'MMM dd, yyyy')}
${order.expected_delivery_date ? `Expected: ${format(parseISO(order.expected_delivery_date), 'MMM dd, yyyy')}` : ''}
${order.actual_delivery_date ? `Delivered: ${format(parseISO(order.actual_delivery_date), 'MMM dd, yyyy')}` : ''}`}
                >
                  <span className="truncate">
                    #{order.id.slice(0, 8)} - {order.customer_organization_name}
                    {(order.status === 'Delivered' || order.status === 'Received') && order.receiving_warehouse_name && (
                      <span className="ml-1">→ {order.receiving_warehouse_name}</span>
                    )}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 flex justify-center space-x-6 text-sm">
        <div className="flex items-center">
          <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
          <span>Pending</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
          <span>Shipped</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
          <span>Delivered</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-red-300 rounded mr-2"></div>
          <span>Cancelled</span>
        </div>
      </div>

      {/* Order Count */}
      <div className="mt-4 text-center text-gray-600 text-sm">
        Showing {visibleOrders.length} of {orders.length} orders
      </div>

      {/* Order Details Modal */}
      <Modal
        isOpen={showOrderModal}
        onClose={closeModal}
        title={`Order #${selectedOrder?.id.slice(0, 8)}`}
        size="lg"
      >
        {selectedOrder && (
          <div className="space-y-4">
            {/* Order Information */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3">Order Information</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-600">Customer:</span>
                  <p className="font-medium">{selectedOrder.customer_organization_name}</p>
                </div>
                <div>
                  <span className="text-gray-600">Status:</span>
                  <p className="font-medium">
                    <span className={`px-2 py-1 rounded text-xs ${
                      selectedOrder.status === 'Pending' ? 'bg-blue-100 text-blue-800' :
                      selectedOrder.status === 'Shipped' ? 'bg-yellow-100 text-yellow-800' :
                      selectedOrder.status === 'Delivered' || selectedOrder.status === 'Received' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {selectedOrder.status}
                    </span>
                  </p>
                </div>
                <div>
                  <span className="text-gray-600">Order Date:</span>
                  <p className="font-medium">{format(parseISO(selectedOrder.order_date), 'MMM dd, yyyy')}</p>
                </div>
                {selectedOrder.expected_delivery_date && (
                  <div>
                    <span className="text-gray-600">Expected Delivery:</span>
                    <p className="font-medium">{format(parseISO(selectedOrder.expected_delivery_date), 'MMM dd, yyyy')}</p>
                  </div>
                )}
                {selectedOrder.shipped_date && (
                  <div>
                    <span className="text-gray-600">Shipped:</span>
                    <p className="font-medium">{format(parseISO(selectedOrder.shipped_date), 'MMM dd, yyyy')}</p>
                  </div>
                )}
                {selectedOrder.actual_delivery_date && (
                  <div>
                    <span className="text-gray-600">Delivered:</span>
                    <p className="font-medium">{format(parseISO(selectedOrder.actual_delivery_date), 'MMM dd, yyyy')}</p>
                  </div>
                )}
                {selectedOrder.receiving_warehouse_name && (
                  <div>
                    <span className="text-gray-600">Receiving Warehouse:</span>
                    <p className="font-medium">{selectedOrder.receiving_warehouse_name}</p>
                  </div>
                )}
                {selectedOrder.ordered_by_username && (
                  <div>
                    <span className="text-gray-600">Ordered By:</span>
                    <p className="font-medium">{selectedOrder.ordered_by_username}</p>
                  </div>
                )}
              </div>
              {selectedOrder.notes && (
                <div className="mt-3">
                  <span className="text-gray-600">Notes:</span>
                  <p className="text-sm text-gray-700 mt-1">{selectedOrder.notes}</p>
                </div>
              )}
            </div>

            {/* Order Items */}
            <div>
              <h3 className="font-semibold text-gray-800 mb-3">Order Items</h3>
              {selectedOrder.items && selectedOrder.items.length > 0 ? (
                <div className="space-y-2">
                  {selectedOrder.items.map((item, index) => (
                    <div key={item.id || index} className="bg-white border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">
                            {item.part_name || 'Unknown Part'}
                          </p>
                          <p className="text-sm text-gray-600">
                            Part #: {item.part_number || 'N/A'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">
                            {item.quantity} {item.unit_of_measure || 'units'}
                          </p>
                          {item.unit_price && (
                            <p className="text-sm text-gray-600">
                              ${parseFloat(item.unit_price).toFixed(2)} each
                            </p>
                          )}
                        </div>
                      </div>
                      {item.unit_price && (
                        <div className="mt-2 pt-2 border-t border-gray-100">
                          <p className="text-sm text-gray-700 text-right">
                            Subtotal: ${(parseFloat(item.quantity) * parseFloat(item.unit_price)).toFixed(2)}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {/* Total */}
                  {selectedOrder.items.some(item => item.unit_price) && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-gray-800">Order Total:</span>
                        <span className="text-xl font-bold text-blue-600">
                          ${selectedOrder.items.reduce((sum, item) => 
                            sum + (parseFloat(item.quantity || 0) * parseFloat(item.unit_price || 0)), 0
                          ).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No items in this order</p>
              )}
            </div>

            {/* Close Button */}
            <div className="flex justify-end pt-4 border-t border-gray-200">
              <button
                onClick={closeModal}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md font-medium"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default OrderCalendarView;
