# ABParts Product Overview

ABParts is an inventory and order management system for AutoBoss net cleaner parts distribution. The system manages the complete parts ecosystem from manufacturer to end-user consumption.

## Business Model

**Key Players:**
- **Oraseas EE**: App owner and primary distributor (single instance)
- **BossAqua**: Manufacturer of AutoBoss machines and proprietary parts (single instance)
- **Customers**: Organizations that purchase AutoBoss machines and need parts (max 100)
- **Suppliers**: Third-party suppliers serving customers or Oraseas EE

**Parts Flow:** Creation (manufacturer/suppliers) → Distribution (Oraseas EE) → Customers → Consumption (in machines)

## Scale Requirements

- Maximum 100 customer organizations
- Maximum 200 total users across all organizations  
- Parts catalog scales efficiently with proper indexing and pagination
- Maximum 150 AutoBoss machines deployed
- Maximum 150 warehouses across all organizations
- Maximum 7,500 transactions per year

## Performance Considerations

- **Parts Management**: System optimized for large parts catalogs through database indexing, efficient pagination, and search optimization
- **Database Performance**: Composite indexes on frequently queried fields ensure fast retrieval regardless of catalog size
- **API Scalability**: Pagination and caching strategies maintain responsive performance with growing datasets

## Core Features

- **Multi-organization management** with proper business relationships
- **Warehouse-based inventory tracking** with decimal quantity support
- **Machine registration and parts usage tracking**
- **Complete transaction audit trail** for all parts movements
- **Role-based access control** (user, admin, super_admin)
- **Order management** with status workflows
- **Comprehensive reporting** and analytics

## Current Status

The system has a solid technical foundation but requires business model alignment to properly represent organization types, user roles, and warehouse-based inventory management before feature enhancements can proceed.