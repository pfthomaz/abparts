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

const OrderCalendarView = ({ orders = [], onOrderClick }) => {
  const [centerDate, setCenterDate] = useState(new Date());

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
                  onClick={() => onOrderClick && onOrderClick(order)}
                  title={`Order #${order.id.slice(0, 8)}
Customer: ${order.customer_organization_name || 'N/A'}
Status: ${order.status}
Ordered: ${format(parseISO(order.order_date), 'MMM dd, yyyy')}
${order.expected_delivery_date ? `Expected: ${format(parseISO(order.expected_delivery_date), 'MMM dd, yyyy')}` : ''}
${order.actual_delivery_date ? `Delivered: ${format(parseISO(order.actual_delivery_date), 'MMM dd, yyyy')}` : ''}`}
                >
                  <span className="truncate">
                    #{order.id.slice(0, 8)} - {order.customer_organization_name}
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
    </div>
  );
};

export default OrderCalendarView;
