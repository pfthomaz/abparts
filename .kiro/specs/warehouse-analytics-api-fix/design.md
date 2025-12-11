# Design Document

## Overview

The warehouse inventory analytics feature is failing because the required API endpoints are missing from the backend. The frontend component `WarehouseInventoryAnalytics.js` is attempting to call `/inventory/warehouse/{warehouseId}/analytics` endpoints that don't exist in the current `backend/app/routers/inventory.py` router.

This design addresses the missing API endpoints by implementing warehouse-specific analytics endpoints that provide inventory insights, trends, and metrics for individual warehouses.

## Architecture

### Backend Components

**API Layer:**
- Add new analytics endpoints to `backend/app/routers/inventory.py`
- Implement proper authentication and authorization checks
- Add comprehensive error handling and validation

**Business Logic Layer:**
- Create new CRUD functions in `backend/app/crud/inventory.py`
- Implement analytics calculations and data aggregation
- Add caching mechanisms for performance optimization

**Data Layer:**
- Utilize existing database models (`Inventory`, `Warehouse`, `Part`, `Transaction`)
- Implement efficient queries with proper joins and aggregations
- Add database indexes if needed for performance

### Frontend Integration

**Service Layer:**
- The existing `inventoryService.getWarehouseInventoryAnalytics()` function will work once backend endpoints are implemented
- No changes needed to frontend service calls

**Component Layer:**
- The existing `WarehouseInventoryAnalytics.js` component will work once backend returns proper data
- Error handling is already implemented in the component

## Components and Interfaces

### API Endpoints

#### GET /inventory/warehouse/{warehouse_id}/analytics
**Purpose:** Get comprehensive analytics for a specific warehouse
**Parameters:**
- `warehouse_id` (path): UUID of the warehouse
- `start_date` (query, optional): Start date for analytics period
- `end_date` (query, optional): End date for analytics period
- `days` (query, optional): Number of days to include (default: 30)

**Response Schema:**
```json
{
  "warehouse_id": "uuid",
  "warehouse_name": "string",
  "analytics_period": {
    "start_date": "date",
    "end_date": "date",
    "days": "integer"
  },
  "inventory_summary": {
    "total_parts": "integer",
    "total_value": "decimal",
    "low_stock_parts": "integer",
    "out_of_stock_parts": "integer"
  },
  "top_parts_by_value": [
    {
      "part_id": "uuid",
      "part_name": "string",
      "quantity": "decimal",
      "unit_price": "decimal",
      "total_value": "decimal"
    }
  ],
  "stock_movements": {
    "total_inbound": "decimal",
    "total_outbound": "decimal",
    "net_change": "decimal"
  },
  "turnover_metrics": {
    "average_turnover_days": "decimal",
    "fast_moving_parts": "integer",
    "slow_moving_parts": "integer"
  }
}
```

#### GET /inventory/warehouse/{warehouse_id}/analytics/trends
**Purpose:** Get trend data for warehouse analytics charts
**Parameters:**
- `warehouse_id` (path): UUID of the warehouse
- `period` (query): "daily", "weekly", "monthly" (default: "daily")
- `days` (query): Number of days to include (default: 30)

**Response Schema:**
```json
{
  "warehouse_id": "uuid",
  "period": "string",
  "trends": [
    {
      "date": "date",
      "total_value": "decimal",
      "total_quantity": "decimal",
      "parts_count": "integer",
      "transactions_count": "integer"
    }
  ]
}
```

### CRUD Functions

#### get_warehouse_analytics()
**Purpose:** Calculate comprehensive analytics for a warehouse
**Parameters:**
- `db`: Database session
- `warehouse_id`: UUID of the warehouse
- `start_date`: Optional start date
- `end_date`: Optional end date
- `days`: Number of days (default: 30)

**Returns:** Dictionary with analytics data

#### get_warehouse_analytics_trends()
**Purpose:** Calculate trend data for warehouse analytics
**Parameters:**
- `db`: Database session
- `warehouse_id`: UUID of the warehouse
- `period`: Aggregation period ("daily", "weekly", "monthly")
- `days`: Number of days to include

**Returns:** List of trend data points

## Data Models

### Existing Models Used
- `models.Inventory`: Current inventory levels
- `models.Warehouse`: Warehouse information
- `models.Part`: Part details and pricing
- `models.Transaction`: Historical inventory movements
- `models.Organization`: Organization context for access control

### New Schema Classes
```python
class WarehouseAnalyticsResponse(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str
    analytics_period: Dict[str, Any]
    inventory_summary: Dict[str, Any]
    top_parts_by_value: List[Dict[str, Any]]
    stock_movements: Dict[str, Any]
    turnover_metrics: Dict[str, Any]

class WarehouseAnalyticsTrendsResponse(BaseModel):
    warehouse_id: uuid.UUID
    period: str
    trends: List[Dict[str, Any]]

class WarehouseAnalyticsRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days: int = 30
```

## Error Handling

### API Level Error Handling
- **404 Not Found**: When warehouse doesn't exist
- **403 Forbidden**: When user lacks access to warehouse
- **400 Bad Request**: When parameters are invalid
- **500 Internal Server Error**: When calculations fail

### Business Logic Error Handling
- Graceful handling of missing data
- Default values for incomplete analytics
- Logging of calculation errors
- Fallback to basic metrics when complex calculations fail

### Database Error Handling
- Connection timeout handling
- Query optimization for large datasets
- Proper transaction management
- Index usage validation

## Testing Strategy

### Unit Tests
- Test analytics calculation functions with various data scenarios
- Test error handling with invalid inputs
- Test permission checking logic
- Test data aggregation accuracy

### Integration Tests
- Test complete API endpoints with real database
- Test authentication and authorization flows
- Test performance with large datasets
- Test error scenarios end-to-end

### API Tests
- Test all endpoint responses match schema
- Test query parameter validation
- Test error response formats
- Test rate limiting and caching

### Performance Tests
- Test response times with large warehouses
- Test concurrent request handling
- Test database query efficiency
- Test memory usage during calculations

## Security Considerations

### Authentication
- All endpoints require valid JWT token
- Token validation using existing auth middleware
- Proper error responses for invalid tokens

### Authorization
- Users can only access warehouses in their organization
- Super admins can access all warehouses
- Proper organization-scoped queries
- Access logging for audit trails

### Data Protection
- No sensitive data exposure in analytics
- Proper input sanitization
- SQL injection prevention through ORM
- Rate limiting to prevent abuse

## Performance Optimization

### Caching Strategy
- Cache analytics results for 15 minutes
- Use Redis for distributed caching
- Cache invalidation on inventory changes
- Separate cache keys per warehouse and time period

### Database Optimization
- Add indexes on frequently queried columns
- Use efficient JOIN queries
- Implement query result pagination
- Use database views for complex aggregations

### Response Optimization
- Compress large response payloads
- Use appropriate HTTP caching headers
- Implement response streaming for large datasets
- Optimize JSON serialization