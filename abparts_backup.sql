--
-- PostgreSQL database dump
--

\restrict w5I08gy0xqu20Z9QKaAKtxzvDvQ7TQ295A8P4RyLjpSRug4iTeC3dzjJgi0Nw8M

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 16.11 (Debian 16.11-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: configurationcategory; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.configurationcategory AS ENUM (
    'ORGANIZATION',
    'PARTS',
    'USER_MANAGEMENT',
    'LOCALIZATION',
    'SYSTEM'
);


ALTER TYPE public.configurationcategory OWNER TO abparts_user;

--
-- Name: configurationdatatype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.configurationdatatype AS ENUM (
    'STRING',
    'INTEGER',
    'BOOLEAN',
    'JSON',
    'ENUM'
);


ALTER TYPE public.configurationdatatype OWNER TO abparts_user;

--
-- Name: inventoryalertseverity; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.inventoryalertseverity AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);


ALTER TYPE public.inventoryalertseverity OWNER TO abparts_user;

--
-- Name: inventoryalerttype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.inventoryalerttype AS ENUM (
    'low_stock',
    'stockout',
    'expiring',
    'expired',
    'excess',
    'discrepancy'
);


ALTER TYPE public.inventoryalerttype OWNER TO abparts_user;

--
-- Name: machinestatus; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.machinestatus AS ENUM (
    'active',
    'inactive',
    'maintenance',
    'decommissioned'
);


ALTER TYPE public.machinestatus OWNER TO abparts_user;

--
-- Name: maintenancepriority; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.maintenancepriority AS ENUM (
    'low',
    'medium',
    'high',
    'urgent'
);


ALTER TYPE public.maintenancepriority OWNER TO abparts_user;

--
-- Name: maintenancerisklevel; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.maintenancerisklevel AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);


ALTER TYPE public.maintenancerisklevel OWNER TO abparts_user;

--
-- Name: maintenancestatus; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.maintenancestatus AS ENUM (
    'pending',
    'scheduled',
    'in_progress',
    'completed',
    'cancelled'
);


ALTER TYPE public.maintenancestatus OWNER TO abparts_user;

--
-- Name: maintenancetype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.maintenancetype AS ENUM (
    'scheduled',
    'unscheduled',
    'repair',
    'inspection',
    'cleaning',
    'calibration',
    'other'
);


ALTER TYPE public.maintenancetype OWNER TO abparts_user;

--
-- Name: orderpriority; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.orderpriority AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'URGENT'
);


ALTER TYPE public.orderpriority OWNER TO abparts_user;

--
-- Name: orderstatus; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.orderstatus AS ENUM (
    'REQUESTED',
    'APPROVED',
    'ORDERED',
    'SHIPPED',
    'RECEIVED',
    'CANCELLED'
);


ALTER TYPE public.orderstatus OWNER TO abparts_user;

--
-- Name: organizationtype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.organizationtype AS ENUM (
    'oraseas_ee',
    'bossaqua',
    'customer',
    'supplier'
);


ALTER TYPE public.organizationtype OWNER TO abparts_user;

--
-- Name: parttype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.parttype AS ENUM (
    'consumable',
    'bulk_material'
);


ALTER TYPE public.parttype OWNER TO abparts_user;

--
-- Name: stocktakestatus; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.stocktakestatus AS ENUM (
    'planned',
    'in_progress',
    'completed',
    'cancelled'
);


ALTER TYPE public.stocktakestatus OWNER TO abparts_user;

--
-- Name: suppliertype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.suppliertype AS ENUM (
    'ORASEAS_EE',
    'EXTERNAL_SUPPLIER'
);


ALTER TYPE public.suppliertype OWNER TO abparts_user;

--
-- Name: transactionapprovalstatus; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.transactionapprovalstatus AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED'
);


ALTER TYPE public.transactionapprovalstatus OWNER TO abparts_user;

--
-- Name: transactiontype; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.transactiontype AS ENUM (
    'creation',
    'transfer',
    'consumption',
    'adjustment'
);


ALTER TYPE public.transactiontype OWNER TO abparts_user;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.userrole AS ENUM (
    'user',
    'admin',
    'super_admin'
);


ALTER TYPE public.userrole OWNER TO abparts_user;

--
-- Name: userstatus; Type: TYPE; Schema: public; Owner: abparts_user
--

CREATE TYPE public.userstatus AS ENUM (
    'active',
    'inactive',
    'pending_invitation',
    'locked'
);


ALTER TYPE public.userstatus OWNER TO abparts_user;

--
-- Name: check_inventory_balance(); Type: FUNCTION; Schema: public; Owner: abparts_user
--

CREATE FUNCTION public.check_inventory_balance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.current_stock < 0 THEN
        RAISE EXCEPTION 'Inventory cannot be negative. Current stock would be: %', NEW.current_stock;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_inventory_balance() OWNER TO abparts_user;

--
-- Name: update_inventory_on_transaction(); Type: FUNCTION; Schema: public; Owner: abparts_user
--

CREATE FUNCTION public.update_inventory_on_transaction() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Handle different transaction types
    CASE NEW.transaction_type
        WHEN 'creation' THEN
            -- Increase inventory in to_warehouse
            IF NEW.to_warehouse_id IS NOT NULL THEN
                INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                ON CONFLICT (warehouse_id, part_id)
                DO UPDATE SET 
                    current_stock = inventory.current_stock + NEW.quantity,
                    last_updated = NOW();
            END IF;
            
        WHEN 'transfer' THEN
            -- Decrease from source warehouse
            IF NEW.from_warehouse_id IS NOT NULL THEN
                UPDATE inventory 
                SET current_stock = current_stock - NEW.quantity,
                    last_updated = NOW()
                WHERE warehouse_id = NEW.from_warehouse_id AND part_id = NEW.part_id;
            END IF;
            
            -- Increase in destination warehouse
            IF NEW.to_warehouse_id IS NOT NULL THEN
                INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                ON CONFLICT (warehouse_id, part_id)
                DO UPDATE SET 
                    current_stock = inventory.current_stock + NEW.quantity,
                    last_updated = NOW();
            END IF;
            
        WHEN 'consumption' THEN
            -- Decrease inventory in from_warehouse
            IF NEW.from_warehouse_id IS NOT NULL THEN
                UPDATE inventory 
                SET current_stock = current_stock - NEW.quantity,
                    last_updated = NOW()
                WHERE warehouse_id = NEW.from_warehouse_id AND part_id = NEW.part_id;
            END IF;
            
        WHEN 'adjustment' THEN
            -- Adjust inventory in specified warehouse
            IF NEW.to_warehouse_id IS NOT NULL THEN
                INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                ON CONFLICT (warehouse_id, part_id)
                DO UPDATE SET 
                    current_stock = inventory.current_stock + NEW.quantity,
                    last_updated = NOW();
            END IF;
    END CASE;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_inventory_on_transaction() OWNER TO abparts_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO abparts_user;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.audit_logs (
    id uuid NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    user_id uuid NOT NULL,
    organization_id uuid,
    resource_type character varying(100) NOT NULL,
    resource_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    old_values text,
    new_values text,
    details text,
    ip_address character varying(45),
    user_agent text,
    endpoint character varying(255),
    http_method character varying(10),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO abparts_user;

--
-- Name: customer_order_items; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.customer_order_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_order_id uuid NOT NULL,
    part_id uuid NOT NULL,
    quantity numeric(10,3) DEFAULT 1 NOT NULL,
    unit_price numeric(10,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.customer_order_items OWNER TO abparts_user;

--
-- Name: customer_orders; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.customer_orders (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_organization_id uuid NOT NULL,
    oraseas_organization_id uuid NOT NULL,
    order_date timestamp with time zone NOT NULL,
    expected_delivery_date timestamp with time zone,
    actual_delivery_date timestamp with time zone,
    status character varying(50) NOT NULL,
    ordered_by_user_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    shipped_by_user_id uuid
);


ALTER TABLE public.customer_orders OWNER TO abparts_user;

--
-- Name: inventory; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.inventory (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    warehouse_id uuid NOT NULL,
    part_id uuid NOT NULL,
    current_stock numeric(10,3) DEFAULT 0 NOT NULL,
    minimum_stock_recommendation numeric(10,3) DEFAULT 0 NOT NULL,
    unit_of_measure character varying(50) NOT NULL,
    reorder_threshold_set_by character varying(50),
    last_recommendation_update timestamp with time zone,
    last_updated timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.inventory OWNER TO abparts_user;

--
-- Name: inventory_adjustments; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.inventory_adjustments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    warehouse_id uuid NOT NULL,
    part_id uuid NOT NULL,
    quantity_change numeric(10,3) NOT NULL,
    previous_quantity numeric(10,3) NOT NULL,
    new_quantity numeric(10,3) NOT NULL,
    reason character varying(255) NOT NULL,
    notes text,
    adjusted_by_user_id uuid NOT NULL,
    adjustment_date timestamp with time zone NOT NULL,
    stocktake_id uuid,
    transaction_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.inventory_adjustments OWNER TO abparts_user;

--
-- Name: inventory_alerts; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.inventory_alerts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    warehouse_id uuid NOT NULL,
    part_id uuid NOT NULL,
    alert_type public.inventoryalerttype NOT NULL,
    severity public.inventoryalertseverity NOT NULL,
    threshold_value numeric(10,3),
    current_value numeric(10,3) NOT NULL,
    message text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    resolved_at timestamp with time zone,
    resolved_by_user_id uuid,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.inventory_alerts OWNER TO abparts_user;

--
-- Name: invitation_audit_logs; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.invitation_audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    performed_by_user_id uuid,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    details text
);


ALTER TABLE public.invitation_audit_logs OWNER TO abparts_user;

--
-- Name: machine_hours; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.machine_hours (
    id uuid NOT NULL,
    machine_id uuid NOT NULL,
    recorded_by_user_id uuid NOT NULL,
    hours_value numeric(10,2) NOT NULL,
    recorded_date timestamp with time zone NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.machine_hours OWNER TO abparts_user;

--
-- Name: machine_maintenance; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.machine_maintenance (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    machine_id uuid NOT NULL,
    maintenance_date timestamp with time zone NOT NULL,
    maintenance_type public.maintenancetype NOT NULL,
    performed_by_user_id uuid NOT NULL,
    description text NOT NULL,
    hours_spent numeric(5,2),
    cost numeric(10,2),
    next_maintenance_date timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.machine_maintenance OWNER TO abparts_user;

--
-- Name: machine_part_compatibility; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.machine_part_compatibility (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    machine_id uuid NOT NULL,
    part_id uuid NOT NULL,
    is_recommended boolean DEFAULT false NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.machine_part_compatibility OWNER TO abparts_user;

--
-- Name: machine_predictions; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.machine_predictions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    machine_id uuid NOT NULL,
    predictive_model_id uuid NOT NULL,
    prediction_date timestamp with time zone DEFAULT now() NOT NULL,
    failure_probability numeric(5,4),
    remaining_useful_life integer,
    predicted_failure_date timestamp with time zone,
    risk_level public.maintenancerisklevel NOT NULL,
    prediction_details text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.machine_predictions OWNER TO abparts_user;

--
-- Name: machine_sales; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.machine_sales (
    id uuid NOT NULL,
    machine_id uuid NOT NULL,
    from_organization_id uuid NOT NULL,
    to_organization_id uuid NOT NULL,
    sale_price numeric(10,2),
    sale_date timestamp with time zone NOT NULL,
    performed_by_user_id uuid NOT NULL,
    notes text,
    reference_number character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.machine_sales OWNER TO abparts_user;

--
-- Name: machines; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.machines (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_organization_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    serial_number character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    purchase_date date,
    warranty_expiry_date date,
    last_service_date date,
    next_service_due date,
    service_interval_hours integer,
    installation_date date,
    machine_condition character varying(50),
    notes text,
    status character varying(50) DEFAULT 'active'::character varying,
    machine_status character varying(50) DEFAULT 'operational'::character varying,
    operational_status character varying(50) DEFAULT 'running'::character varying,
    maintenance_status character varying(50) DEFAULT 'up_to_date'::character varying,
    location character varying(255),
    operator_name character varying(255),
    last_maintenance_date date,
    next_maintenance_date date,
    maintenance_interval_days integer DEFAULT 90,
    total_operating_hours integer DEFAULT 0,
    hours_since_maintenance integer DEFAULT 0,
    maintenance_notes text,
    technician_name character varying(255),
    maintenance_cost numeric(10,2),
    manufacturer character varying(255) DEFAULT 'BossAqua'::character varying,
    year_manufactured integer,
    current_hours integer DEFAULT 0,
    max_operating_hours integer DEFAULT 10000,
    model_type character varying(10) NOT NULL
);


ALTER TABLE public.machines OWNER TO abparts_user;

--
-- Name: maintenance_part_usage; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.maintenance_part_usage (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    maintenance_id uuid NOT NULL,
    part_id uuid NOT NULL,
    quantity numeric(10,3) NOT NULL,
    warehouse_id uuid NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.maintenance_part_usage OWNER TO abparts_user;

--
-- Name: maintenance_recommendations; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.maintenance_recommendations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    machine_id uuid NOT NULL,
    prediction_id uuid NOT NULL,
    recommendation_date timestamp with time zone DEFAULT now() NOT NULL,
    recommended_maintenance_type character varying(50) NOT NULL,
    priority public.maintenancepriority NOT NULL,
    recommended_completion_date timestamp with time zone NOT NULL,
    description text NOT NULL,
    status public.maintenancestatus NOT NULL,
    resolved_by_maintenance_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.maintenance_recommendations OWNER TO abparts_user;

--
-- Name: organization_configurations; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.organization_configurations (
    id uuid NOT NULL,
    organization_id uuid NOT NULL,
    configuration_key character varying(255) NOT NULL,
    value text,
    is_active boolean DEFAULT true NOT NULL,
    created_by_user_id uuid,
    updated_by_user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.organization_configurations OWNER TO abparts_user;

--
-- Name: organizations; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.organizations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    organization_type public.organizationtype NOT NULL,
    parent_organization_id uuid,
    address text,
    contact_info text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    country character varying(100),
    logo_url character varying(500),
    CONSTRAINT supplier_must_have_parent CHECK (((organization_type <> 'supplier'::public.organizationtype) OR (parent_organization_id IS NOT NULL)))
);


ALTER TABLE public.organizations OWNER TO abparts_user;

--
-- Name: part_order_items; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.part_order_items (
    id uuid NOT NULL,
    order_request_id uuid NOT NULL,
    part_id uuid NOT NULL,
    quantity numeric(10,3) NOT NULL,
    unit_price numeric(10,2),
    destination_warehouse_id uuid NOT NULL,
    received_quantity numeric(10,3) DEFAULT '0'::numeric,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.part_order_items OWNER TO abparts_user;

--
-- Name: part_order_requests; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.part_order_requests (
    id uuid NOT NULL,
    order_number character varying(50) NOT NULL,
    customer_organization_id uuid NOT NULL,
    supplier_type public.suppliertype NOT NULL,
    supplier_organization_id uuid,
    supplier_name character varying(255),
    status public.orderstatus NOT NULL,
    priority public.orderpriority NOT NULL,
    requested_delivery_date timestamp with time zone,
    expected_delivery_date timestamp with time zone,
    actual_delivery_date timestamp with time zone,
    notes text,
    fulfillment_notes text,
    requested_by_user_id uuid NOT NULL,
    approved_by_user_id uuid,
    received_by_user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.part_order_requests OWNER TO abparts_user;

--
-- Name: part_usage; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.part_usage (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_organization_id uuid NOT NULL,
    part_id uuid NOT NULL,
    usage_date timestamp with time zone NOT NULL,
    quantity numeric(10,3) DEFAULT 1 NOT NULL,
    machine_id uuid,
    recorded_by_user_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    warehouse_id uuid NOT NULL
);


ALTER TABLE public.part_usage OWNER TO abparts_user;

--
-- Name: part_usage_items; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.part_usage_items (
    id uuid NOT NULL,
    usage_record_id uuid NOT NULL,
    part_id uuid NOT NULL,
    quantity numeric(10,3) NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.part_usage_items OWNER TO abparts_user;

--
-- Name: part_usage_records; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.part_usage_records (
    id uuid NOT NULL,
    machine_id uuid NOT NULL,
    from_warehouse_id uuid NOT NULL,
    usage_date timestamp with time zone NOT NULL,
    performed_by_user_id uuid NOT NULL,
    service_type character varying(50),
    machine_hours numeric(10,2),
    notes text,
    reference_number character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.part_usage_records OWNER TO abparts_user;

--
-- Name: parts; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.parts (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    part_number character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    part_type public.parttype DEFAULT 'consumable'::public.parttype NOT NULL,
    is_proprietary boolean DEFAULT false NOT NULL,
    unit_of_measure character varying(50) DEFAULT 'pieces'::character varying NOT NULL,
    manufacturer_part_number character varying(255),
    manufacturer_delivery_time_days integer,
    local_supplier_delivery_time_days integer,
    image_urls text[],
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    supplier_part_number character varying(255),
    manufacturer character varying(255),
    category character varying(100),
    weight numeric(10,3),
    dimensions character varying(255),
    material character varying(100),
    color character varying(50),
    warranty_period integer,
    part_code character varying(100),
    serial_number character varying(255)
);


ALTER TABLE public.parts OWNER TO abparts_user;

--
-- Name: predictive_maintenance_models; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.predictive_maintenance_models (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    model_type character varying(100) NOT NULL,
    target_metric character varying(100) NOT NULL,
    features text NOT NULL,
    hyperparameters text,
    performance_metrics text,
    version character varying(50) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL
);


ALTER TABLE public.predictive_maintenance_models OWNER TO abparts_user;

--
-- Name: security_event_logs; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.security_event_logs (
    id uuid NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    event_type character varying(100) NOT NULL,
    severity character varying(20) NOT NULL,
    user_id uuid,
    organization_id uuid,
    description text NOT NULL,
    details text,
    ip_address character varying(45),
    user_agent text,
    endpoint character varying(255),
    resolved character varying(20) NOT NULL,
    resolved_at timestamp with time zone,
    resolved_by uuid,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.security_event_logs OWNER TO abparts_user;

--
-- Name: security_events; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.security_events (
    id uuid NOT NULL,
    user_id uuid,
    event_type character varying(50) NOT NULL,
    ip_address character varying(45),
    user_agent text,
    session_id character varying(255),
    details text,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    risk_level character varying(20) DEFAULT 'low'::character varying NOT NULL
);


ALTER TABLE public.security_events OWNER TO abparts_user;

--
-- Name: stock_adjustments; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.stock_adjustments (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    inventory_id uuid NOT NULL,
    user_id uuid NOT NULL,
    adjustment_date timestamp with time zone DEFAULT now() NOT NULL,
    quantity_adjusted numeric(10,3) NOT NULL,
    reason_code character varying(100) NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.stock_adjustments OWNER TO abparts_user;

--
-- Name: stocktake_items; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.stocktake_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    stocktake_id uuid NOT NULL,
    part_id uuid NOT NULL,
    expected_quantity numeric(10,3) NOT NULL,
    actual_quantity numeric(10,3),
    counted_at timestamp with time zone,
    counted_by_user_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.stocktake_items OWNER TO abparts_user;

--
-- Name: stocktakes; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.stocktakes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    warehouse_id uuid NOT NULL,
    scheduled_date timestamp with time zone NOT NULL,
    status public.stocktakestatus DEFAULT 'planned'::public.stocktakestatus NOT NULL,
    notes text,
    scheduled_by_user_id uuid NOT NULL,
    completed_date timestamp with time zone,
    completed_by_user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.stocktakes OWNER TO abparts_user;

--
-- Name: supplier_order_items; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.supplier_order_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    supplier_order_id uuid NOT NULL,
    part_id uuid NOT NULL,
    quantity numeric(10,3) DEFAULT 1 NOT NULL,
    unit_price numeric(10,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.supplier_order_items OWNER TO abparts_user;

--
-- Name: supplier_orders; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.supplier_orders (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ordering_organization_id uuid NOT NULL,
    supplier_name character varying(255) NOT NULL,
    order_date timestamp with time zone NOT NULL,
    expected_delivery_date timestamp with time zone,
    actual_delivery_date timestamp with time zone,
    status character varying(50) NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.supplier_orders OWNER TO abparts_user;

--
-- Name: system_configurations; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.system_configurations (
    id uuid NOT NULL,
    category public.configurationcategory NOT NULL,
    key character varying(255) NOT NULL,
    value text,
    data_type public.configurationdatatype NOT NULL,
    description text,
    is_system_managed boolean DEFAULT false NOT NULL,
    is_user_configurable boolean DEFAULT true NOT NULL,
    requires_restart boolean DEFAULT false NOT NULL,
    validation_rules json,
    default_value text,
    created_by_user_id uuid,
    updated_by_user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.system_configurations OWNER TO abparts_user;

--
-- Name: transaction_approvals; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.transaction_approvals (
    id uuid NOT NULL,
    transaction_id uuid NOT NULL,
    approver_id uuid NOT NULL,
    status public.transactionapprovalstatus NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.transaction_approvals OWNER TO abparts_user;

--
-- Name: transactions; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.transactions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    transaction_type public.transactiontype NOT NULL,
    part_id uuid NOT NULL,
    from_warehouse_id uuid,
    to_warehouse_id uuid,
    machine_id uuid,
    quantity numeric(10,3) NOT NULL,
    unit_of_measure character varying(50) NOT NULL,
    performed_by_user_id uuid NOT NULL,
    transaction_date timestamp with time zone NOT NULL,
    notes text,
    reference_number character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.transactions OWNER TO abparts_user;

--
-- Name: user_management_audit_logs; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.user_management_audit_logs (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    performed_by_user_id uuid NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    details text
);


ALTER TABLE public.user_management_audit_logs OWNER TO abparts_user;

--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.user_sessions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    session_token character varying(255) NOT NULL,
    ip_address character varying(45),
    user_agent text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_activity timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    terminated_reason character varying(100)
);


ALTER TABLE public.user_sessions OWNER TO abparts_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    username character varying(255) NOT NULL,
    password_hash text NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(255),
    role public.userrole NOT NULL,
    user_status public.userstatus DEFAULT 'active'::public.userstatus NOT NULL,
    failed_login_attempts integer DEFAULT 0 NOT NULL,
    locked_until timestamp with time zone,
    last_login timestamp with time zone,
    invitation_token character varying(255),
    invitation_expires_at timestamp with time zone,
    password_reset_token character varying(255),
    password_reset_expires_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    invited_by_user_id uuid,
    email_verification_token character varying(255),
    email_verification_expires_at timestamp without time zone,
    pending_email character varying(255),
    preferred_language character varying(10),
    preferred_country character varying(10),
    localization_preferences jsonb,
    profile_photo_url character varying(500)
);


ALTER TABLE public.users OWNER TO abparts_user;

--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: abparts_user
--

CREATE TABLE public.warehouses (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    location character varying(500),
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    address text,
    contact_person character varying(255),
    phone character varying(50),
    email character varying(255),
    capacity_limit integer,
    warehouse_type character varying(50)
);


ALTER TABLE public.warehouses OWNER TO abparts_user;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.alembic_version (version_num) FROM stdin;
add_parts_perf_idx
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.audit_logs (id, "timestamp", user_id, organization_id, resource_type, resource_id, action, old_values, new_values, details, ip_address, user_agent, endpoint, http_method, created_at) FROM stdin;
d4b5e64c-8315-4336-84c5-8db7617885f5	2025-07-31 11:45:24.002002+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	TEST_RESOURCE	a28a092a-1900-4853-83e0-3ed409fa4e53	READ	\N	\N	{"test": "data_access"}	127.0.0.1	test-agent	/test	GET	2025-07-31 11:45:23.996783+00
31817f43-6ccb-44cb-a074-d51107a013af	2025-07-31 11:45:24.010205+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	TEST_RESOURCE	a28a092a-1900-4853-83e0-3ed409fa4e53	UPDATE	{"field": "old_value"}	{"field": "new_value"}	\N	127.0.0.1	test-agent	/test	PUT	2025-07-31 11:45:24.00871+00
8bbb9092-aa21-4f1c-b4bd-cebb8de8761a	2025-07-31 11:45:24.110594+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	TEST_CONTEXT_RESOURCE	8c36439f-a9d5-4863-9c3b-e4fd91a2f2fc	READ	\N	\N	{"context_test": true}	\N	\N	\N	\N	2025-07-31 11:45:24.109511+00
f850f122-4ac0-4d12-a145-7729e5af43fd	2025-07-31 11:45:24.113705+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	TEST_CONTEXT_RESOURCE	8c36439f-a9d5-4863-9c3b-e4fd91a2f2fc	UPDATE	{"field": "old"}	{"field": "new"}	\N	\N	\N	\N	\N	2025-07-31 11:45:24.112693+00
a7fbe8dc-c9a1-4b26-b6bf-e412fa619c04	2025-07-31 11:46:09.036175+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	ORGANIZATION_ACCESS	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	VALIDATE_ACCESS	\N	\N	{"access_granted": true, "reason": "superadmin_privilege"}	\N	\N	\N	\N	2025-07-31 11:46:09.036323+00
70ef55f8-5a7d-405a-b1b5-542a904feec0	2025-07-31 11:46:09.303908+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	ORGANIZATION_LIST	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GET_ACCESSIBLE_ORGS	\N	\N	{"accessible_count": 18, "reason": "superadmin_privilege"}	\N	\N	\N	\N	2025-07-31 11:46:09.304163+00
1a510cda-bfd8-44f9-8975-962078332104	2025-07-31 11:46:09.558236+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	SUPPLIER_LIST	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GET_VISIBLE_SUPPLIERS	\N	\N	{"visible_count": 3, "reason": "superadmin_privilege", "scope": "all_suppliers"}	\N	\N	\N	\N	2025-07-31 11:46:09.558372+00
cbbdfa2a-a590-4642-9636-ad754e2b5bd3	2025-07-31 11:46:09.780305+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	BOSSAQUA_DATA	f6abc555-5b6c-6f7a-8b9c-0d123456789a	READ	\N	\N	{"user_role": "super_admin", "access_granted": true, "reason": "superadmin_privilege"}	\N	\N	\N	\N	2025-07-31 11:46:09.780498+00
15595f49-0747-406e-adbf-c86cc7137417	2025-07-31 11:52:39.649532+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	ORGANIZATION_ACCESS	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	VALIDATE_ACCESS	\N	\N	{"access_granted": true, "reason": "superadmin_privilege"}	\N	\N	\N	\N	2025-07-31 11:52:39.649727+00
d920a3f1-38e6-4427-8d6a-564923c0a288	2025-07-31 11:52:39.894993+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	ORGANIZATION_LIST	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GET_ACCESSIBLE_ORGS	\N	\N	{"accessible_count": 18, "reason": "superadmin_privilege"}	\N	\N	\N	\N	2025-07-31 11:52:39.895129+00
c603474f-d1a3-4979-8ce7-00bc9b0c1ad9	2025-07-31 11:52:40.133397+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	SUPPLIER_LIST	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GET_VISIBLE_SUPPLIERS	\N	\N	{"visible_count": 3, "reason": "superadmin_privilege", "scope": "all_suppliers"}	\N	\N	\N	\N	2025-07-31 11:52:40.13356+00
fb80e27f-22fe-4eee-8792-f8272f5e670a	2025-07-31 11:52:40.370592+00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	BOSSAQUA_DATA	f6abc555-5b6c-6f7a-8b9c-0d123456789a	READ	\N	\N	{"user_role": "super_admin", "access_granted": true, "reason": "superadmin_privilege"}	\N	\N	\N	\N	2025-07-31 11:52:40.37078+00
\.


--
-- Data for Name: customer_order_items; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.customer_order_items (id, customer_order_id, part_id, quantity, unit_price, created_at, updated_at) FROM stdin;
b42e5d9a-f904-46a5-9fb3-0e0412384cc5	45f88201-173d-4862-bfcb-ec3c4d5968f8	a7aaa666-6a7a-7a8b-9c01-234567890123	4.000	500.00	2025-08-06 14:22:08.120933+00	2025-08-06 14:22:08.120933+00
13cd4d82-c52c-4f43-af5f-8f4c97ae89da	53ae4a63-b7e4-4a49-8f59-0a768edc6d37	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	2.000	\N	2025-10-21 10:08:30.727158+00	2025-10-21 10:08:30.727158+00
676182d7-a1a0-42fe-90e3-e698405c6ba9	26f2d136-c8b9-48cd-84f5-0cd5e94ce9b8	e1457957-9441-48d9-a161-75faff16bd5d	2.000	\N	2025-10-22 15:49:51.715368+00	2025-10-22 15:49:51.715368+00
b54fe744-2ce2-43ab-aa49-739dd3bf63d9	ded5c939-0358-4767-a44e-ef66bb0b7f83	e1457957-9441-48d9-a161-75faff16bd5d	8.000	\N	2025-11-12 12:08:11.887191+00	2025-11-12 12:08:11.887191+00
e8492c7d-51d2-4e38-bdfc-d589eddeca36	ded5c939-0358-4767-a44e-ef66bb0b7f83	c7e77564-90c2-4052-82b7-52b4eece06c6	1.000	\N	2025-11-12 12:08:12.195926+00	2025-11-12 12:08:12.195926+00
\.


--
-- Data for Name: customer_orders; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.customer_orders (id, customer_organization_id, oraseas_organization_id, order_date, expected_delivery_date, actual_delivery_date, status, ordered_by_user_id, notes, created_at, updated_at, shipped_by_user_id) FROM stdin;
247ee0a5-46e2-4f31-8b40-f6a831e12b77	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-07-21 00:00:00+00	2025-08-01 00:00:00+00	\N	Pending	\N		2025-07-21 22:55:30.513687+00	2025-07-21 22:55:30.513687+00	\N
40bcd99c-7f74-44d6-ab17-b090cb90d8f9	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-07-21 00:00:00+00	2025-08-15 00:00:00+00	\N	Requested	f6abc555-5b6c-6f7a-8b9c-0d123456789a		2025-07-21 22:57:25.276285+00	2025-07-21 22:57:25.276285+00	\N
00a782f5-4fe4-47ac-8577-ea592d3753b5	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-07-21 00:00:00+00	2025-08-08 00:00:00+00	\N	Pending	f6abc555-5b6c-6f7a-8b9c-0d123456789a		2025-07-21 22:17:48.855023+00	2025-08-06 13:10:11.649839+00	\N
45f88201-173d-4862-bfcb-ec3c4d5968f8	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-08-06 00:00:00+00	\N	\N	Requested	f6abc555-5b6c-6f7a-8b9c-0d123456789a		2025-08-06 14:22:08.070365+00	2025-08-06 14:22:08.070365+00	\N
53ae4a63-b7e4-4a49-8f59-0a768edc6d37	0f676a79-6c15-4c67-9096-0ac3467d404f	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-10-21 00:00:00+00	2025-11-04 00:00:00+00	2025-10-21 00:00:00+00	Received	\N		2025-10-21 10:08:30.257719+00	2025-10-21 10:09:11.296726+00	\N
26f2d136-c8b9-48cd-84f5-0cd5e94ce9b8	0f676a79-6c15-4c67-9096-0ac3467d404f	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-10-01 00:00:00+00	2025-10-08 00:00:00+00	2025-10-14 00:00:00+00	Received	\N		2025-10-22 15:49:51.157681+00	2025-10-22 15:50:10.961949+00	\N
ded5c939-0358-4767-a44e-ef66bb0b7f83	0f676a79-6c15-4c67-9096-0ac3467d404f	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-11-12 00:00:00+00	2025-11-26 00:00:00+00	\N	Pending	\N		2025-11-12 12:08:11.323781+00	2025-11-12 12:08:11.323781+00	\N
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.inventory (id, warehouse_id, part_id, current_stock, minimum_stock_recommendation, unit_of_measure, reorder_threshold_set_by, last_recommendation_update, last_updated, created_at) FROM stdin;
d800ed99-e99b-49c4-8dc5-20e46588de82	11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	a7aaa666-6a7a-7a8b-9c01-234567890123	150.000	70.000	pieces	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
87d38724-c505-4f34-b357-cab9a0ac1a2c	11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	b8bbb777-7b8b-8b9c-0123-456789012345	25.000	10.000	pieces	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
7d18d5e7-e323-4075-a04d-09bfafaed091	11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d7	15.000	7.000	pieces	user	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
6488ebe7-20f7-403f-b280-dc144bac3070	11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	200.000	100.000	pieces	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
aaca185c-ee1f-4e13-8773-a5c6fe3c9ce3	22eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e70	500.500	200.000	meters	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
317a5379-4a1d-421e-9ae0-4a3b440078cf	33cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	a7aaa666-6a7a-7a8b-9c01-234567890123	30.000	15.000	pieces	user	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
eaa4b116-375d-4c13-8129-77b103349a68	33cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	40.000	20.000	pieces	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
c3fb53ee-af52-4534-8f30-d3a19bc5cf4d	33cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e70	25.750	10.000	meters	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
3d99f8f3-87cd-474d-8303-cbe22e47118e	33cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	b8bbb777-7b8b-8b9c-0123-456789012345	5.000	2.000	pieces	user	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
9432e209-7cd2-4cef-b6af-154e291f88fc	44eff222-2f3e-3c4d-5e6f-7a8b9c012346	a7aaa666-6a7a-7a8b-9c01-234567890123	10.000	5.000	pieces	user	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
1f57cbbb-2b6b-4f1e-8195-de653b39bc44	44eff222-2f3e-3c4d-5e6f-7a8b9c012346	c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e70	15.250	8.000	meters	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
07da4d89-8ab2-4bfd-9130-d67f78273981	44eff222-2f3e-3c4d-5e6f-7a8b9c012346	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	5.000	2.000	pieces	user	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
1d1c620b-3524-420c-9382-5840db9a45dc	44eff222-2f3e-3c4d-5e6f-7a8b9c012346	a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d7	2.000	1.000	pieces	system	\N	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00
c29669af-e0a6-4681-83b8-77114482c833	1e019a80-2852-4269-b3d3-2c5a46ded47f	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	4.000	0.000	pieces	\N	\N	2025-10-21 10:09:11.296726+00	2025-10-21 10:09:11.296726+00
48ed4676-87fd-4c8e-9693-1341034f33d2	22eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a7aaa666-6a7a-7a8b-9c01-234567890123	40.000	25.000	pieces	user	\N	2025-09-15 14:54:03.837802+00	2025-08-03 14:53:16.435722+00
74d1682c-fe6a-4892-9163-9ca693f12820	1e019a80-2852-4269-b3d3-2c5a46ded47f	e1457957-9441-48d9-a161-75faff16bd5d	4.000	0.000	pieces	\N	\N	2025-10-22 15:50:10.961949+00	2025-10-22 15:50:10.961949+00
b75380a3-7fbd-4208-90a8-00e3a43f66f9	11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	9b6b218d-6f66-4f12-ad1b-b61825af7265	1.000	2.000	pieces	system	\N	2025-11-20 09:30:26.447066+00	2025-11-20 09:30:26.447066+00
e883361b-12fd-45dc-afa6-faeefbb929af	402317bf-7d65-432f-9099-6ed4a852b95c	a7aaa666-6a7a-7a8b-9c01-234567890123	0.000	0.000	pieces	\N	\N	2025-09-29 17:28:39.65465+00	2025-09-15 14:54:03.837802+00
90c7ca6f-6c80-402a-8c5e-ff8903c94216	70851ed9-1146-4abb-8463-699907dfefe9	a7aaa666-6a7a-7a8b-9c01-234567890123	160.000	0.000	pieces	\N	\N	2025-09-29 17:28:39.65465+00	2025-09-15 15:23:48.853048+00
\.


--
-- Data for Name: inventory_adjustments; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.inventory_adjustments (id, warehouse_id, part_id, quantity_change, previous_quantity, new_quantity, reason, notes, adjusted_by_user_id, adjustment_date, stocktake_id, transaction_id, created_at) FROM stdin;
\.


--
-- Data for Name: inventory_alerts; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.inventory_alerts (id, warehouse_id, part_id, alert_type, severity, threshold_value, current_value, message, is_active, resolved_at, resolved_by_user_id, resolution_notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: invitation_audit_logs; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.invitation_audit_logs (id, user_id, action, performed_by_user_id, "timestamp", details) FROM stdin;
\.


--
-- Data for Name: machine_hours; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.machine_hours (id, machine_id, recorded_by_user_id, hours_value, recorded_date, notes, created_at, updated_at) FROM stdin;
012ff10c-91ce-41bd-ba4c-1c51e59d9125	1a2b3c4d-5e6f-7a8b-9c0d-e1f2a3b4c5d6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	0.00	2025-07-31 10:59:50.299063+00	Initial hours record created during data migration	2025-07-31 10:59:50.299063+00	2025-07-31 10:59:50.299063+00
62c21452-36a8-4ca5-b7ab-0f35e694dec5	6d5c4b3a-2f1e-8b7a-9d0c-e3f4a5b6c7d8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	0.00	2025-07-31 10:59:50.299063+00	Initial hours record created during data migration	2025-07-31 10:59:50.299063+00	2025-07-31 10:59:50.299063+00
\.


--
-- Data for Name: machine_maintenance; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.machine_maintenance (id, machine_id, maintenance_date, maintenance_type, performed_by_user_id, description, hours_spent, cost, next_maintenance_date, notes, created_at, updated_at) FROM stdin;
5891e095-aeca-413f-870d-2d110a4f3ccc	1a2b3c4d-5e6f-7a8b-9c0d-e1f2a3b4c5d6	2025-08-06 00:00:00+00	scheduled	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Test maintenance	\N	3000.00	2025-08-08 00:00:00+00	\N	2025-08-06 13:26:21.396644+00	2025-08-06 13:26:21.396644+00
37bfda09-4d25-4800-8f3f-ac3b3d1dffca	6d5c4b3a-2f1e-8b7a-9d0c-e3f4a5b6c7d8	2025-08-06 00:00:00+00	repair	f6abc555-5b6c-6f7a-8b9c-0d123456789a		3.00	3000.00	2025-08-08 00:00:00+00	\N	2025-08-06 13:28:23.475971+00	2025-08-06 13:28:23.475971+00
\.


--
-- Data for Name: machine_part_compatibility; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.machine_part_compatibility (id, machine_id, part_id, is_recommended, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: machine_predictions; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.machine_predictions (id, machine_id, predictive_model_id, prediction_date, failure_probability, remaining_useful_life, predicted_failure_date, risk_level, prediction_details, created_at) FROM stdin;
\.


--
-- Data for Name: machine_sales; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.machine_sales (id, machine_id, from_organization_id, to_organization_id, sale_price, sale_date, performed_by_user_id, notes, reference_number, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: machines; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.machines (id, customer_organization_id, name, serial_number, created_at, updated_at, purchase_date, warranty_expiry_date, last_service_date, next_service_due, service_interval_hours, installation_date, machine_condition, notes, status, machine_status, operational_status, maintenance_status, location, operator_name, last_maintenance_date, next_maintenance_date, maintenance_interval_days, total_operating_hours, hours_since_maintenance, maintenance_notes, technician_name, maintenance_cost, manufacturer, year_manufactured, current_hours, max_operating_hours, model_type) FROM stdin;
1a2b3c4d-5e6f-7a8b-9c0d-e1f2a3b4c5d6	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Main Production Line Machine	ABV31B-SN001	2025-08-03 14:53:16.435722+00	2025-08-06 13:26:21.396644+00	\N	\N	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	2025-08-06	2025-08-08	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V3.1B
6d5c4b3a-2f1e-8b7a-9d0c-e3f4a5b6c7d8	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Assembly Robot 2000	ABV40-SN002	2025-08-03 14:53:16.435722+00	2025-08-06 13:28:23.475971+00	\N	\N	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	2025-08-06	2025-08-08	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V4.0
4efec977-f8ca-4b31-a9ef-2884c052c079	0f676a79-6c15-4c67-9096-0ac3467d404f	KEF-1	25	2025-10-24 11:30:01.40742+00	2025-10-24 11:30:01.40742+00	2019-08-30	2019-09-30	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	\N	\N	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V3.1B
1dd2ed88-e18a-4011-9c07-e589b89eba99	0f676a79-6c15-4c67-9096-0ac3467d404f	KEF-2	28	2025-10-24 11:30:35.913862+00	2025-10-24 11:30:35.913862+00	2020-09-01	\N	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	\N	\N	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V3.1B
a3695179-a60e-4b94-9930-014863adca74	0f676a79-6c15-4c67-9096-0ac3467d404f	KEF-3	32	2025-10-24 11:31:07.611022+00	2025-10-24 11:31:07.611022+00	2021-05-12	\N	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	\N	\N	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V3.1B
201c021a-478e-4465-b310-53b12c15a18a	0f676a79-6c15-4c67-9096-0ac3467d404f	KEF-4	35	2025-10-24 11:31:38.346002+00	2025-10-24 11:31:38.346002+00	2023-10-01	\N	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	\N	\N	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V3.1B
56c7a530-f828-41d8-b033-8dddd46fa6c0	160d8213-2d5b-4d58-84cc-fbf53becb528	T-Boss-1	054	2025-10-24 11:36:18.97114+00	2025-10-24 11:36:53.44117+00	2025-05-21	2026-06-20	\N	\N	\N	\N	\N	\N	active	operational	running	up_to_date	\N	\N	\N	\N	90	0	0	\N	\N	\N	BossAqua	\N	0	10000	V4.0
\.


--
-- Data for Name: maintenance_part_usage; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.maintenance_part_usage (id, maintenance_id, part_id, quantity, warehouse_id, notes, created_at) FROM stdin;
\.


--
-- Data for Name: maintenance_recommendations; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.maintenance_recommendations (id, machine_id, prediction_id, recommendation_date, recommended_maintenance_type, priority, recommended_completion_date, description, status, resolved_by_maintenance_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: organization_configurations; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.organization_configurations (id, organization_id, configuration_key, value, is_active, created_by_user_id, updated_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: organizations; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.organizations (id, name, organization_type, parent_organization_id, address, contact_info, is_active, created_at, updated_at, country, logo_url) FROM stdin;
b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Autoboss Inc	customer	\N	456 Tech Park, Wellington, NZ	+64 4 987 6543	f	2025-08-03 14:53:16.435722+00	2025-09-15 09:11:46.626682+00	\N	\N
c2dee111-1e2d-2b3c-4d5e-6f7a8b9c0123	AutoParts Ltd	supplier	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	789 Supply Rd, Christchurch, NZ	+64 3 234 5678	f	2025-08-03 14:53:16.435722+00	2025-09-15 09:13:52.243063+00	\N	\N
d3eff222-2f3e-3c4d-5e6f-7a8b9c012346	RoboMech Solutions	customer	\N	101 Automation Drive, Hamilton, NZ	+64 7 222 3333	f	2025-08-03 14:53:16.435722+00	2025-09-15 09:13:55.30522+00	\N	\N
e4fac333-3c4f-4d5e-6f7a-8b9c01234568	Industrial Innovators	customer	\N	202 Factory Rd, Dunedin, NZ	+64 3 444 5555	f	2025-08-03 14:53:16.435722+00	2025-09-15 09:13:58.618702+00	\N	\N
d5b34232-ad40-45dd-8e8a-c57e0b993aa5	Leros Fishfarming SA	customer	\N	Leros Island	\N	t	2025-09-15 09:15:37.089615+00	2025-09-15 09:15:37.089615+00	GR	\N
ed6d6318-8c68-49e6-9f73-f5b8346ef0db	Korfos Fishfarming	customer	\N	Korfos, Greece	\N	t	2025-09-15 09:16:01.431969+00	2025-09-15 09:16:01.431969+00	GR	\N
81b293ec-0a56-463a-a75a-df699b125779	Philosofish SA	customer	\N	Athens, Greece	\N	t	2025-09-15 09:16:24.580413+00	2025-09-15 09:16:24.580413+00	GR	\N
160d8213-2d5b-4d58-84cc-fbf53becb528	Tharawat Seas LLC	customer	\N	Jeddah, KSA	\N	t	2025-09-15 09:16:54.905515+00	2025-09-15 09:16:54.905515+00	KSA	\N
3833cea1-8178-4ce6-a705-01492d91c850	Temri	customer	\N	Cyprus	\N	t	2025-09-15 09:17:15.115587+00	2025-09-15 09:17:15.115587+00	CY	\N
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	Oraseas EE	oraseas_ee	\N	123 Main St, Auckland, NZ	+64 9 123 4567	t	2025-08-03 14:53:16.435722+00	2025-11-21 10:50:20.479493+00	\N	/static/images/org_logo_0ed901c0-d628-4c1f-94ad-84699f4761fd.jpg
0f676a79-6c15-4c67-9096-0ac3467d404f	Kefalonia Fisheries SA	customer	\N	Kefalonia	\N	t	2025-09-15 09:14:21.006573+00	2025-11-21 10:50:53.126032+00	GR	/static/images/org_logo_134d1dc4-8a36-4490-9892-217c47314343.png
1f7dcfa6-0e84-4597-8285-33c1bfbaca5d	Petalas Bros SA	customer	\N	Kalymnos Island	\N	t	2025-09-15 09:15:10.176478+00	2025-11-21 11:38:25.185321+00	GR	/static/images/org_logo_99c897d3-4837-4b71-8116-6b759734b899.png
0449761e-0b70-4f21-a4ab-f526e7c1528b	Kito Fishfarming SA	customer	\N	Leros Island	\N	t	2025-09-15 09:14:44.411313+00	2025-11-21 11:38:32.724306+00	GR	/static/images/org_logo_2b1c6f65-c30c-4e94-b03e-ce73345ea254.jpeg
b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	BossAqua	bossaqua	\N	456 Manufacturing Ave, Auckland, NZ	+64 9 234 5678	t	2025-08-03 14:53:16.435722+00	2025-11-21 11:47:08.016813+00	\N	/static/images/org_logo_051b4114-ceec-464f-8ba7-9a223db68a27.png
434b0c43-4461-462c-8e0d-b6dd4236c8fa	BossServ LLC	supplier	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	Scotland	\N	t	2025-09-15 09:13:42.724307+00	2025-11-21 11:47:31.499143+00	\N	/static/images/org_logo_85b917b8-4c8f-4910-a722-592fee912351.png
\.


--
-- Data for Name: part_order_items; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.part_order_items (id, order_request_id, part_id, quantity, unit_price, destination_warehouse_id, received_quantity, notes, created_at, updated_at) FROM stdin;
f0224d42-ac72-494c-ab33-7969e040d69c	42261ed2-bdbd-4bbc-881f-d8b3a9806287	b8bbb777-7b8b-8b9c-0123-456789012345	10.000	25.50	8048dd21-205f-4ce9-adbe-b24dd32d4750	0.000	Test part order item	2025-07-30 18:03:11.271914+00	2025-07-30 18:03:11.271914+00
0fe916da-aaa1-4527-a734-2f57a933d498	6aec15c1-db9a-4e4b-8353-85f9ced6ad92	b8bbb777-7b8b-8b9c-0123-456789012345	10.000	25.50	8048dd21-205f-4ce9-adbe-b24dd32d4750	0.000	Test part order item	2025-07-30 18:04:48.384624+00	2025-07-30 18:04:48.384624+00
14239ca6-146d-4ec6-aec3-547fb776c6d8	7b9d7460-25bb-4217-ad8a-90f04049ddbd	b8bbb777-7b8b-8b9c-0123-456789012345	10.000	25.50	8048dd21-205f-4ce9-adbe-b24dd32d4750	0.000	Test part order item	2025-07-30 18:06:07.102158+00	2025-07-30 18:06:07.102158+00
3abaf0fb-80fd-4f83-83a3-594b8bb422aa	3592da6a-aa97-413c-a770-e4025ca9dceb	b8bbb777-7b8b-8b9c-0123-456789012345	10.000	25.50	8048dd21-205f-4ce9-adbe-b24dd32d4750	0.000	Test part order item	2025-07-30 18:07:02.172738+00	2025-07-30 18:07:02.172738+00
56452b03-8c52-4b84-99b6-28f724d3d337	d844fd21-a07d-4e32-934b-501a3409f41f	b8bbb777-7b8b-8b9c-0123-456789012345	10.000	25.50	8048dd21-205f-4ce9-adbe-b24dd32d4750	0.000	Test part order item	2025-07-30 18:07:16.21344+00	2025-07-30 18:07:16.21344+00
\.


--
-- Data for Name: part_order_requests; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.part_order_requests (id, order_number, customer_organization_id, supplier_type, supplier_organization_id, supplier_name, status, priority, requested_delivery_date, expected_delivery_date, actual_delivery_date, notes, fulfillment_notes, requested_by_user_id, approved_by_user_id, received_by_user_id, created_at, updated_at) FROM stdin;
42261ed2-bdbd-4bbc-881f-d8b3a9806287	PO-20250730-0001	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	ORASEAS_EE	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Autoboss Inc	REQUESTED	MEDIUM	\N	2025-07-30 19:03:11.31112+00	\N	Test part order	\N	f6abc555-5b6c-6f7a-8b9c-0d123456789a	\N	\N	2025-07-30 18:03:11.271914+00	2025-07-30 18:03:11.271914+00
6aec15c1-db9a-4e4b-8353-85f9ced6ad92	PO-20250730-0002	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	ORASEAS_EE	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Autoboss Inc	REQUESTED	MEDIUM	\N	2025-07-30 19:04:48.491466+00	\N	Test part order	\N	f6abc555-5b6c-6f7a-8b9c-0d123456789a	\N	\N	2025-07-30 18:04:48.384624+00	2025-07-30 18:04:48.384624+00
7b9d7460-25bb-4217-ad8a-90f04049ddbd	PO-20250730-0003	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	ORASEAS_EE	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Autoboss Inc	REQUESTED	MEDIUM	\N	2025-07-30 19:06:07.07895+00	\N	Test part order	\N	f6abc555-5b6c-6f7a-8b9c-0d123456789a	\N	\N	2025-07-30 18:06:07.102158+00	2025-07-30 18:06:07.102158+00
3592da6a-aa97-413c-a770-e4025ca9dceb	PO-20250730-0004	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	ORASEAS_EE	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Autoboss Inc	REQUESTED	MEDIUM	\N	2025-07-30 19:07:02.097715+00	\N	Test part order	\N	f6abc555-5b6c-6f7a-8b9c-0d123456789a	\N	\N	2025-07-30 18:07:02.172738+00	2025-07-30 18:07:02.172738+00
d844fd21-a07d-4e32-934b-501a3409f41f	PO-20250730-0005	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	ORASEAS_EE	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Autoboss Inc	REQUESTED	MEDIUM	\N	2025-07-30 19:07:16.293476+00	\N	Test part order	\N	f6abc555-5b6c-6f7a-8b9c-0d123456789a	\N	\N	2025-07-30 18:07:16.21344+00	2025-07-30 18:07:16.21344+00
\.


--
-- Data for Name: part_usage; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.part_usage (id, customer_organization_id, part_id, usage_date, quantity, machine_id, recorded_by_user_id, notes, created_at, updated_at, warehouse_id) FROM stdin;
\.


--
-- Data for Name: part_usage_items; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.part_usage_items (id, usage_record_id, part_id, quantity, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: part_usage_records; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.part_usage_records (id, machine_id, from_warehouse_id, usage_date, performed_by_user_id, service_type, machine_hours, notes, reference_number, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: parts; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.parts (id, part_number, name, description, part_type, is_proprietary, unit_of_measure, manufacturer_part_number, manufacturer_delivery_time_days, local_supplier_delivery_time_days, image_urls, created_at, updated_at, supplier_part_number, manufacturer, category, weight, dimensions, material, color, warranty_period, part_code, serial_number) FROM stdin;
b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	PN-004-D	Proximity Sensor Module	Detects object presence and distance	consumable	f	pieces	MFG-SENS-004	\N	5	{/static/images/default_part_sensor_module.jpg}	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3ca34565-a716-4fc1-b7c9-8a8d53530d6c	CPW-016	Charge pump - complete	Charge pump - complete	consumable	f	pieces	CPW-016	\N	\N	{}	2025-09-20 08:07:08.889116+00	2025-09-20 08:07:08.889116+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
81d5c447-2d8f-428d-b7d5-36ef901eb5b0	CPW-017	Camlock fitting primary strainer Male	Camlock fitting primary strainer Male	consumable	f	pieces	CPW-017	\N	\N	{}	2025-09-20 08:07:34.587495+00	2025-09-20 08:07:34.587495+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ce6359ec-c30e-4a4d-9927-67e2b31ac7ef	CPW-018	Camlock fitting primary strainer Female	Camlock fitting primary strainer Female	consumable	f	pieces	CPW-018	\N	\N	{}	2025-09-20 08:08:01.065666+00	2025-09-20 08:08:01.065666+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0337fed1-1e09-4ccd-b99f-9776f7e7ea12	CPW-019	Charge pressure sensor	Charge pressure sensor	consumable	f	pieces	CPW-019	\N	\N	{}	2025-09-20 08:08:25.841434+00	2025-09-20 08:08:25.841434+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6bb120e5-9847-4467-9978-49944f09e9b2	CPW-020	Filter chamber lid cover	Filter chamber lid cover	consumable	f	pieces	CPW-020	\N	\N	{}	2025-09-20 08:08:48.577311+00	2025-09-20 08:08:48.577311+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5f20d41e-e257-43de-af11-3c00374de5c3	CPW-021	Charge pressure gauge	Charge pressure gauge	consumable	f	pieces	CPW-021	\N	\N	{}	2025-09-20 08:09:09.856582+00	2025-09-20 08:09:09.856582+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e81415be-85d5-4be9-a72f-3972b3cddca9	CPW-022	Taper Lock bush	Taper Lock bush	consumable	f	pieces	CPW-022	\N	\N	{}	2025-09-20 08:09:33.809056+00	2025-09-20 08:09:33.809056+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b76d9f26-47b4-44f5-85eb-4eeb5ac2d40e	CPW-023	Header tank anode plug	Header tank anode plug	consumable	f	pieces	CPW-023	\N	\N	{}	2025-09-20 08:10:17.642766+00	2025-09-20 08:11:00.032451+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a26d6674-c2c8-463f-a054-48d6ca330f88	EP-001	RPM linear actuator	RPM linear actuator	consumable	f	pieces	EP-001	\N	\N	{}	2025-09-20 08:11:24.859268+00	2025-09-20 08:11:24.859268+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c91c4a52-65f8-434d-bfcb-7201b0b6bae3	EP-002	RPM gauge	RPM gauge	consumable	f	pieces	EP-002	\N	\N	{}	2025-09-20 08:11:55.480119+00	2025-09-20 08:11:55.480119+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b8bbb777-7b8b-8b9c-0123-456789012345	CON-001	Travel Kit	Tool kit with basic tools required to service the AutoBoss	consumable	f	pieces	CON-001	0	14	{/static/images/default_part_control_unit.jpg}	2025-08-03 14:53:16.435722+00	2025-09-15 10:21:03.107361+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a7aaa666-6a7a-7a8b-9c01-234567890123	CPW-004	Primary Strainer	Big conical filter, made of stainless steel	consumable	t	pieces	CPW-004	30	\N	{/static/images/default_part_filter.jpg}	2025-08-03 14:53:16.435722+00	2025-09-15 10:23:26.253087+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d7	CPW-005.1	Hose barb locking collar - straight	Hose barb locking collar - straight	consumable	t	pieces	CPW-005.1	30	\N	{/static/images/default_part_hydraulic_pump.jpg}	2025-08-03 14:53:16.435722+00	2025-09-15 10:30:02.822828+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c0774d47-6087-4cb6-b85e-4e5df231bb0e	CPW-006	Primary strainer connection to manifold	Primary strainer connection to manifold	consumable	t	pieces	CPW-006	30	\N	{}	2025-09-15 10:30:40.695425+00	2025-09-16 00:00:20.131876+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8fdf46c3-52c6-4507-b4c6-8bf05cb836b9	EP-003	RPM Sensor	RPM Sensor	consumable	f	pieces	EP-003	\N	\N	{}	2025-09-20 08:12:18.75401+00	2025-09-20 08:12:18.75401+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c5adbcaa-0074-4c2a-8ce3-bef591049a0c	EP-004	Master on/off switch	Master on/off switch	consumable	f	pieces	EP-004	\N	\N	{}	2025-09-20 08:12:40.242831+00	2025-09-20 08:12:40.242831+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1a89a5f9-39a3-47ca-b416-e855ba9d2f3c	EP-005	Sacrificial Anode (Heat Exchanger)	Sacrificial Anode (Heat Exchanger)	consumable	f	pieces	EP-005	\N	\N	{}	2025-09-20 08:12:59.803327+00	2025-09-20 08:12:59.803327+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5536e828-65a0-4979-b02a-26cf2f6e5a4d	EP-006	Turbo cover	Turbo cover	consumable	f	pieces	EP-006	\N	\N	{}	2025-09-20 08:13:22.683365+00	2025-09-20 08:13:22.683365+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
73c5349d-4d89-4ae7-a02a-522d0517704a	CPW-007	Raw Water Suction hose	Raw Water Suction hose	consumable	f	pieces	CPW-007	\N	\N	{}	2025-09-20 08:02:09.667106+00	2025-09-20 08:02:09.667106+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ea09baff-65c1-40ee-871b-a4494bdff7d0	CPW-009	Impeller (10 blade)	Impeller (10 blade)	consumable	f	pieces	CPW-009	\N	\N	{}	2025-09-20 08:02:29.958662+00	2025-09-20 08:02:29.958662+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e70	CPW-002	Filter Bag	Filter bag	consumable	t	pieces	CPW-002	30	0	{}	2025-08-03 14:53:16.435722+00	2025-09-20 08:02:48.37459+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
29771579-7b04-4998-abad-13e464ecb12e	CPW-010	Operator front pressure gauges (set of 3)	Operator front pressure gauges (set of 3)	consumable	f	pieces	CPW-010	\N	\N	{}	2025-09-20 08:05:08.287004+00	2025-09-20 08:05:08.287004+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c690fbac-0b8d-4c0c-b1a0-27fedb88fbbb	CPW-011	Inlet hose, 6m flushing w/ camlock fittings	Inlet hose, 6m flushing w/ camlock fittings	consumable	f	pieces	CPW-011	\N	\N	{}	2025-09-20 08:05:39.893559+00	2025-09-20 08:05:39.893559+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
97b097a0-a4f4-4441-b8db-010a1335c9b4	CPW-013	Bag filter orifice fittings	Bag filter orifice fittings	consumable	f	pieces	CPW-013	\N	\N	{}	2025-09-20 08:06:04.124931+00	2025-09-20 08:06:04.124931+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5dd93577-8a2c-47d9-b821-199126f9789c	CPW-014	Charge pressure hose/m	Charge pressure hose/m	consumable	f	pieces	CPW-014	\N	\N	{}	2025-09-20 08:06:26.272641+00	2025-09-20 08:06:26.272641+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b033389e-f85f-48ee-8e83-71447740b8cf	CPW-015	Charge pressure header tank anode	Charge pressure header tank anode	consumable	f	pieces	CPW-015	\N	\N	{}	2025-09-20 08:06:44.29146+00	2025-09-20 08:06:44.29146+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b553022d-d5d7-4890-816c-e4e7aa5b82f1	EP-008 V2	V2 Front crank seal	V2 Front crank seal	consumable	f	pieces	EP-008 V2	\N	\N	{}	2025-09-20 08:14:07.112929+00	2025-09-20 08:14:07.112929+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b39afd7e-77dd-490c-b174-88d9e59d41e3	EP-009	Alternator	Alternator	consumable	f	pieces	EP-009	\N	\N	{}	2025-09-20 08:14:28.006527+00	2025-09-20 08:14:28.006527+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9009ab22-8d74-432a-b40b-1c8785fc41bb	EP-010	Engine Seawater Cooling pump	Engine Seawater Cooling pump	consumable	f	pieces	EP-010	\N	\N	{}	2025-09-20 08:14:46.949051+00	2025-09-20 08:14:46.949051+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2a0d3478-7c91-4cf0-aee0-8539ecc653ab	EP-011	Isuzu oil pressure gauge sender	Isuzu oil pressure gauge sender	consumable	f	pieces	EP-011	\N	\N	{}	2025-09-20 08:15:07.419806+00	2025-09-20 08:15:07.419806+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1b069b3d-7000-4a84-9f55-c1f8d2fbe6d9	ESE-001 V2	Engine oil filters V2	Engine oil filters V2	consumable	f	pieces	ESE-001 V2	\N	\N	{}	2025-09-20 08:15:27.676337+00	2025-09-20 08:15:27.676337+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2425e475-2637-4519-8f96-68f406f9da56	ESE-001.1	Engine oil filter V3	Engine oil filter V3	consumable	f	pieces	ESE-001.1	\N	\N	{}	2025-09-20 08:15:47.861536+00	2025-09-20 08:15:47.861536+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c6e311ef-87fc-4538-8e58-50d39f21894d	ESE-002 V2	Fuel filter V2	Fuel filter V2	consumable	f	pieces	ESE-002 V2	\N	\N	{}	2025-09-20 08:16:12.652244+00	2025-09-20 08:16:12.652244+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c7e77564-90c2-4052-82b7-52b4eece06c6	ESE-003 V2	Air filters V2	Air filters V2	consumable	f	pieces	ESE-003 V2	\N	\N	{}	2025-09-20 08:16:33.307459+00	2025-09-20 08:16:33.307459+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6768c5c7-0ed9-414d-a80f-3dfca331f283	ESE-004	Engine rubber mounts	Engine rubber mounts	consumable	f	pieces	ESE-004	\N	\N	{}	2025-09-20 08:16:53.319215+00	2025-09-20 08:16:53.319215+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
41a2db1c-c900-4ebc-a346-87ab56ccf0ff	ESE-005 V2	Alternator belt V2	Alternator belt V2	consumable	f	pieces	ESE-005 V2	\N	\N	{}	2025-09-20 08:17:14.9079+00	2025-09-20 08:17:14.9079+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3e022e5e-336f-4d41-813a-34207206ccda	ESE-006 V2	V2 HP belt set	V2 HP belt set	consumable	f	pieces	ESE-006 V2	\N	\N	{}	2025-09-20 08:17:37.530163+00	2025-09-20 08:17:37.530163+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d10d1a77-aa84-4e9c-a473-75611de7448c	ESE-006.1	HP belt set V3	HP belt set V3	consumable	f	pieces	ESE-006.1	\N	\N	{}	2025-09-20 08:17:57.296535+00	2025-09-20 08:17:57.296535+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7fcf0962-7cc5-417d-b08c-121894e869ee	ESE-007 V2	V2 Charge Pump Belt	V2 Charge Pump Belt	consumable	f	pieces	ESE-007 V2	\N	\N	{}	2025-09-20 08:18:20.023936+00	2025-09-20 08:18:20.023936+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4b30b1a2-d9a0-4720-bdad-dcc6f181f2c4	ESE-007.1	Charge pump belt V3	Charge pump belt V3	consumable	f	pieces	ESE-007.1	\N	\N	{}	2025-09-20 08:18:42.790996+00	2025-09-20 08:18:42.790996+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f415d3f0-8a44-4db4-b93c-337623b50ed4	ESE-008	Drive shaft and flange	Drive shaft and flange	consumable	f	pieces	ESE-008	\N	\N	{}	2025-09-20 08:19:03.358016+00	2025-09-20 08:19:03.358016+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
eb9aa1e7-b259-44ad-a0df-652e8d482561	ESE-009	Replacement bearing	Replacement bearing	consumable	f	pieces	ESE-009	\N	\N	{}	2025-09-20 08:19:23.78695+00	2025-09-20 08:19:23.78695+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fafc8bf2-f6da-4196-b30b-5b950de630ba	ESE-010	Complete Isuzu dash panel pre-assy	Complete Isuzu dash panel pre-assy	consumable	f	pieces	ESE-010	\N	\N	{}	2025-09-20 08:19:43.104107+00	2025-09-20 08:19:43.104107+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
772e9ab5-6051-4edb-ab0d-1a5bd8f5040e	ESE-011	Alternator belt V3	Alternator belt V3	consumable	f	pieces	ESE-011	\N	\N	{}	2025-09-20 08:20:01.851578+00	2025-09-20 08:20:01.851578+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
68750114-ab87-4740-879c-5143fcd1d611	ESE-012	Engine oil filter hose V2	Engine oil filter hose V2	consumable	f	pieces	ESE-012	\N	\N	{}	2025-09-20 08:20:27.111656+00	2025-09-20 08:20:27.111656+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d1c6a3ce-4875-4528-97d5-d78927fca12c	ESE-013	Bilge pump	Bilge pump	consumable	f	pieces	ESE-013	\N	\N	{}	2025-09-20 08:20:46.263617+00	2025-09-20 08:20:46.263617+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
37323e24-ddc5-4398-bf03-4a98a725405e	ESE-014	Float switch	Float switch	consumable	f	pieces	ESE-014	\N	\N	{}	2025-09-20 08:21:06.100813+00	2025-09-20 08:21:06.100813+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
11931c5c-c9c3-4401-8041-1a7ef4eebc49	ESE-017	Engine to heat exchanger hose (long)	Engine to heat exchanger hose (long)	consumable	f	pieces	ESE-017	\N	\N	{}	2025-09-20 08:22:47.248241+00	2025-09-20 08:22:47.248241+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
699e1b97-b879-45fc-a469-a0f728b8a8b3	ESE-023	EGR cooler hose (out)	EGR cooler hose (out)	consumable	f	pieces	ESE-023	\N	\N	{}	2025-09-20 08:25:05.117516+00	2025-09-20 08:25:05.117516+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
23ea9461-2e40-48da-b246-a523490adc40	HPW-011	Pump Piston kit	Pump Piston kit	consumable	f	pieces	HPW-011	\N	\N	{}	2025-09-20 08:48:04.065003+00	2025-09-20 08:48:04.065003+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
97088f81-b083-4003-bed1-d01f40838d9a	ESE-015	Fuel filter separator V3	Fuel filter separator V3	consumable	f	pieces	ESE-015	\N	\N	{}	2025-09-20 08:21:28.271107+00	2025-09-20 08:21:28.271107+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1b3e1f1b-dbba-44b0-b557-26667e64fd1a	ESE-024	Small moulded coolant hoses	Small moulded coolant hoses	consumable	f	pieces	ESE-024	\N	\N	{}	2025-09-20 08:25:22.371397+00	2025-09-20 08:25:22.371397+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7eabe7c0-620b-4fd9-b936-325357e33edd	HPW-005	HP water pump - valve kit	HP water pump - valve kit	consumable	f	pieces	HPW-005	\N	\N	{}	2025-09-20 08:46:49.292324+00	2025-09-20 08:46:49.292324+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d5f77f9e-d9fc-42e9-a1dc-581ce1ae02a8	HPW-010	HP water pump - complete assembly	HP water pump - complete assembly	consumable	f	pieces	HPW-010	\N	\N	{}	2025-09-20 08:47:38.376585+00	2025-09-20 08:47:38.376585+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
607c5c13-ac8c-4bf4-a374-c0217743b369	HPW-013	Pump Tool Kit	Pump Tool Kit	consumable	f	pieces	HPW-013	\N	\N	{}	2025-09-20 08:48:42.629787+00	2025-09-20 08:48:42.629787+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5ae53a44-9078-461a-bfd8-4ef7369e2a70	HPW-019	Manifold stud bolt - long	Manifold stud bolt - long	consumable	f	pieces	HPW-019	\N	\N	{}	2025-09-20 08:50:47.168502+00	2025-09-20 08:50:47.168502+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
812f23fd-7372-420b-9359-fdf6f80ed456	ESE-016	Fuel filter secondary V3	Fuel filter secondary V3	consumable	f	pieces	ESE-016	\N	\N	{}	2025-09-20 08:22:23.433762+00	2025-09-20 08:22:23.433762+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
edea15c9-6748-494d-8bff-c73f8dd62460	ESE-019	Engine to heat exchanger hose (90 deg)	Engine to heat exchanger hose (90 deg)	consumable	f	pieces	ESE-019	\N	\N	{}	2025-09-20 08:23:35.289669+00	2025-09-20 08:23:35.289669+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
119f79e5-8c27-48c1-8615-d8ff8f08b855	HPW-006	Sacrificial anode	Sacrificial anode	consumable	f	pieces	HPW-006	\N	\N	{}	2025-09-20 08:47:04.773144+00	2025-09-20 08:47:04.773144+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
84ab13fc-45cc-46f2-b970-d14b1ff25753	HPW-018	Manifold stud bolt - short	Manifold stud bolt - short	consumable	f	pieces	HPW-018	\N	\N	{}	2025-09-20 08:50:19.761932+00	2025-09-20 08:50:19.761932+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
67917ec9-7277-406c-973b-0a5065bddfa6	ESE-018	Engine to heat exchanger hose (short)	Engine to heat exchanger hose (short)	consumable	f	pieces	ESE-018	\N	\N	{}	2025-09-20 08:23:10.041848+00	2025-09-20 08:23:10.041848+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2c837c50-5d28-45c8-8c03-bb3e5c722162	ESE-028	Flexi joint	Flexi joint	consumable	f	pieces	ESE-028	\N	\N	{}	2025-09-20 08:26:50.070096+00	2025-09-20 08:26:50.070096+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fa114cf5-4300-40f2-a5da-d938f5bc193b	HPW-004	HP water pump seal kit	HP water pump seal kit	consumable	f	pieces	HPW-004	\N	\N	{}	2025-09-20 08:46:28.108792+00	2025-09-20 08:46:28.108792+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d81b2cef-8ef8-41fd-ba5a-dfa919b8ca12	HPW-016	Gauge mounting clamp	Gauge mounting clamp	consumable	f	pieces	HPW-016	\N	\N	{}	2025-09-20 08:49:40.799947+00	2025-09-20 08:49:40.799947+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b890cdb0-3c3d-4ddc-bd41-728ae4041485	ESE-020	Oil cooler hose (in)	Oil cooler hose (in)	consumable	f	pieces	ESE-020	\N	\N	{}	2025-09-20 08:23:58.539836+00	2025-09-20 08:23:58.539836+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
317afbf9-bd3a-4cd1-9665-93072ae9a4b7	ESE-026	Exhaust muffler	Exhaust muffler	consumable	f	pieces	ESE-026	\N	\N	{}	2025-09-20 08:26:07.017148+00	2025-09-20 08:26:07.017148+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5fc0581f-25f9-4f95-ae61-cda8e901af7d	HPW-017	HP QRC for back of manifold	HP QRC for back of manifold	consumable	f	pieces	HPW-017	\N	\N	{}	2025-09-20 08:50:00.121703+00	2025-09-20 08:50:00.121703+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
136104a2-d4cd-4611-b3c6-6944022538dd	ESE-021	Oil cooler hose (out)	Oil cooler hose (out)	consumable	f	pieces	ESE-021	\N	\N	{}	2025-09-20 08:24:18.395516+00	2025-09-20 08:24:18.395516+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
38cc5df4-cbb2-4cf4-b866-774ea44e116b	ESE-027	Compete Exhaust	Compete Exhaust	consumable	f	pieces	ESE-027	\N	\N	{}	2025-09-20 08:26:30.748937+00	2025-09-20 08:26:30.748937+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
85907dce-f68e-4f30-b68c-bd66096b1b46	HPW-008	Pump VAM cap bolts	Pump VAM cap bolts	consumable	f	pieces	HPW-008	\N	\N	{}	2025-09-20 08:47:22.166574+00	2025-09-20 08:47:22.166574+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cbe9408e-e88d-4f1b-b400-33908422d111	HPW-012	Pump Copper Spacer	Pump Copper Spacer	consumable	f	pieces	HPW-012	\N	\N	{}	2025-09-20 08:48:21.878911+00	2025-09-20 08:48:21.878911+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
670d0278-e3b5-4357-b92a-200ac6d51806	HPW-015	Piston bolt o-rings	Piston bolt o-rings	consumable	f	pieces	HPW-015	\N	\N	{}	2025-09-20 08:49:21.229244+00	2025-09-20 08:49:21.229244+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
73ec5891-c7c4-4bf6-9080-ba76f475b6a3	ESE-022	EGR cooler hose (in)	EGR cooler hose (in)	consumable	f	pieces	ESE-022	\N	\N	{}	2025-09-20 08:24:41.930348+00	2025-09-20 08:24:41.930348+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a51eed12-714b-40b7-9299-81bd76e3c0a2	HPW-002	Modified HP water pump brass head kit	Modified HP water pump brass head kit	consumable	f	pieces	HPW-002	\N	\N	{}	2025-09-20 08:45:56.19758+00	2025-09-20 08:45:56.19758+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d10a63e6-e4a4-4ccb-8b8c-0ed333fb9819	ESE-025 V3	Primary fuel filter head V3	Primary fuel filter head V3	consumable	f	pieces	ESE-025 V3	\N	\N	{}	2025-09-20 08:25:45.371674+00	2025-09-20 08:25:45.371674+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
63815946-d7fe-4e3d-9921-88d435a1600c	HPW-003	Unloader v/v	Unloader v/v	consumable	f	pieces	HPW-003	\N	\N	{}	2025-09-20 08:46:12.384473+00	2025-09-20 08:46:12.384473+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c9725c16-34e6-4867-85e4-eeae43b0b009	HPW-014	HP Pump Plunger oil seal kit	HP Pump Plunger oil seal kit	consumable	f	pieces	HPW-014	\N	\N	{}	2025-09-20 08:49:02.772828+00	2025-09-20 08:49:02.772828+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fa375bdd-04e8-4a9c-8138-a77ade7d361e	HPW-020	HP water gauge	HP water gauge	consumable	f	pieces	HPW-020	\N	\N	{}	2025-09-20 08:51:16.857375+00	2025-09-20 08:51:16.857375+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b30b755b-9fcc-48f5-8366-159985c3c6df	HPW-021	HP Pump Crankshaft Oil Seal	HP Pump Crankshaft Oil Seal	consumable	f	pieces	HPW-021	\N	\N	{}	2025-09-20 08:51:35.070708+00	2025-09-20 08:51:35.070708+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b4b2af00-1ba3-43c9-a25b-a1979969a0f3	HPW-022	Pulley with taper lock bush	Pulley with taper lock bush	consumable	f	pieces	HPW-022	\N	\N	{}	2025-09-20 08:52:01.225266+00	2025-09-20 08:52:01.225266+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
57260f4c-c361-4774-8f25-b5b7dcf2ed5b	HYD-001	Hydraulic oil filters	Hydraulic oil filters	consumable	f	pieces	HYD-001	\N	\N	{}	2025-09-20 08:52:28.722617+00	2025-09-20 08:52:28.722617+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5647faf0-6b06-4947-9e6f-08c819d74022	HYD-002	Tandem hydraulic pump assembly	Tandem hydraulic pump assembly	consumable	f	pieces	HYD-002	\N	\N	{}	2025-09-20 08:52:48.113462+00	2025-09-20 08:52:48.113462+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7b9206b7-d6d5-4afc-a5d5-3ef1b1fc3efb	HYD-002.1	Tandem hydraulic pump assembly V3	Tandem hydraulic pump assembly V3	consumable	f	pieces	HYD-002.1	\N	\N	{}	2025-09-20 08:53:07.763992+00	2025-09-20 08:53:07.763992+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
074725c0-2ef3-4db0-8f47-4e18e227b200	HYD-003	Brass QRC adapter	Brass QRC adapter	consumable	f	pieces	HYD-003	\N	\N	{}	2025-09-20 08:53:26.105901+00	2025-09-20 08:53:26.105901+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7273d38e-f803-4a4a-a024-27f1b83e7e36	HYD-004	Tandem Hydraulic Pump Suction Manifold pipe	Tandem Hydraulic Pump Suction Manifold pipe	consumable	f	pieces	HYD-004	\N	\N	{}	2025-09-20 08:53:46.440291+00	2025-09-20 08:53:46.440291+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
379523a5-1153-4018-b1c5-8242fac1eaf1	HYD-005	Hydraulic Suction hose	Hydraulic Suction hose	consumable	f	pieces	HYD-005	\N	\N	{}	2025-09-20 08:54:04.700879+00	2025-09-20 08:54:04.700879+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9218770c-74ad-4619-a4cb-f64cb41147cc	HYD-005.1	Hydraulic suction hose V3	Hydraulic suction hose V3	consumable	f	pieces	HYD-005.1	\N	\N	{}	2025-09-20 08:54:20.882135+00	2025-09-20 08:54:20.882135+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
312d87d4-1b33-4692-ab57-03111e66d7a7	HYD-006	HP QRC adapter for back of manifold	HP QRC adapter for back of manifold	consumable	f	pieces	HYD-006	\N	\N	{}	2025-09-20 08:54:37.989899+00	2025-09-20 08:54:37.989899+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
75da9853-b123-49c7-b8a8-5987e227eb5d	HYD-007	Hydraulic fittings, rear manifold-straight small	Hydraulic fittings, rear manifold-straight small	consumable	f	pieces	HYD-007	\N	\N	{}	2025-09-20 08:54:57.474884+00	2025-09-20 08:54:57.474884+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
66b1a4be-e645-4c56-b346-bdae45d034ad	HYD-008	Hydraulic fittings for rear manifold-straight large	Hydraulic fittings for rear manifold-straight large	consumable	f	pieces	HYD-008	\N	\N	{}	2025-09-20 08:55:25.720216+00	2025-09-20 08:55:25.720216+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0e493927-744f-42d0-8e44-e3de5585031f	HYD-009	Walking wheel and winch hyd motor	Walking wheel and winch hyd motor	consumable	f	pieces	HYD-009	\N	\N	{}	2025-09-20 08:55:47.927338+00	2025-09-20 08:55:47.927338+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
877dd4b5-4723-47c6-bd24-cd007ccc56dc	HYD-010	(G1) Thruster Balance Valve replacement cartridge	(G1) Thruster Balance Valve replacement cartridge	consumable	f	pieces	HYD-010	\N	\N	{}	2025-09-20 08:56:07.653883+00	2025-09-20 08:56:07.653883+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
654ef56b-6543-44c8-90f6-f83f76813b5e	HYD-012	Hydraulic filter housing	Hydraulic filter housing	consumable	f	pieces	HYD-012	\N	\N	{}	2025-09-20 08:56:51.1541+00	2025-09-20 08:56:51.1541+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2a926557-0540-4805-8d94-b4df5d68cd2b	HYD-013	Lower winch/wheel manifold w/ valving	Lower winch/wheel manifold w/ valving	consumable	f	pieces	HYD-013	\N	\N	{}	2025-09-20 08:57:45.61898+00	2025-09-20 08:57:45.61898+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a84416fe-2562-4770-a981-b80bf04e1962	HYD-014	Lower winch/wheel manifold VALVING ONLY	Lower winch/wheel manifold VALVING ONLY	consumable	f	pieces	HYD-014	\N	\N	{}	2025-09-20 08:58:07.06002+00	2025-09-20 08:58:07.06002+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8606a6ba-c272-49a8-bcbd-de2b5bdd1955	HYD-015	Winch motor mounting bolts	Winch motor mounting bolts	consumable	f	pieces	HYD-015	\N	\N	{}	2025-09-20 08:58:31.319589+00	2025-09-20 08:58:31.319589+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
85bcdb4b-77f0-45ab-a4fb-3e8807b6b55c	HYD-016	Hydraulic pump support bearing	Hydraulic pump support bearing	consumable	f	pieces	HYD-016	\N	\N	{}	2025-09-20 08:58:56.978987+00	2025-09-20 08:58:56.978987+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2ce865ff-1b0e-4b14-81a8-00cf0c70e65a	HYD-017	Complete pump support housing	Complete pump support housing	consumable	f	pieces	HYD-017	\N	\N	{}	2025-09-20 08:59:21.74584+00	2025-09-20 08:59:21.74584+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f515e264-3639-4f18-b5e3-81d4e11aa973	HYD-018	Hydraulic pressure gauge	Hydraulic pressure gauge	consumable	f	pieces	HYD-018	\N	\N	{}	2025-09-20 08:59:46.874397+00	2025-09-20 08:59:46.874397+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
03ca9189-fa74-46ad-825b-1065c3aa9f02	OCC-001	PLC controller Class A (North America) G1/M1 only	PLC controller Class A (North America) G1/M1 only	consumable	f	pieces	OCC-001	\N	\N	{}	2025-09-20 09:39:57.019095+00	2025-09-20 09:39:57.019095+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b37d4994-28fd-43c2-b04d-a626194f4361	OCC-002	Audible alarm	Audible alarm	consumable	f	pieces	OCC-002	\N	\N	{}	2025-09-20 09:40:22.989184+00	2025-09-20 09:40:22.989184+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
282ac65d-baed-46f4-985c-c6aa485284fe	OCC-003	Dash panel on/off switch	Dash panel on/off switch	consumable	f	pieces	OCC-003	\N	\N	{}	2025-09-20 09:40:55.899372+00	2025-09-20 09:40:55.899372+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
95c596da-3970-4552-bddc-d7624072ea96	OCC-004	PLC controller (North America) Class B V2 exc M1	PLC controller (North America) Class B V2 exc M1	consumable	f	pieces	OCC-004	\N	\N	{}	2025-09-20 09:41:42.999462+00	2025-09-20 09:41:42.999462+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b73aca16-705e-4fea-88dc-e1e1b53a05e7	OCC-005	PLC controller Class C AB1/BUB	PLC controller Class C AB1/BUB	consumable	f	pieces	OCC-005	\N	\N	{}	2025-09-20 09:42:14.803656+00	2025-09-20 09:42:14.803656+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8ec34d39-d715-4c49-8876-635d4019c1d5	OCC-010	Led light indicator light replacement	Led light indicator light replacement	consumable	f	pieces	OCC-010	\N	\N	{}	2025-10-09 10:17:48.702265+00	2025-10-09 10:17:48.702265+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
60919732-96c2-44bd-90e3-a642b640a98d	OCC-011	12-24 v Power Converter	12-24 v Power Converter	consumable	f	pieces	OCC-011	\N	\N	{}	2025-10-09 10:18:10.369938+00	2025-10-09 10:18:10.369938+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bff6b8fc-1e67-4de2-9971-b8c4ebecbe3f	OCC-012	OCC-012 Throttle control module	OCC-012 Throttle control module	consumable	f	pieces	OCC-012	\N	\N	{}	2025-10-09 10:18:29.274821+00	2025-10-09 10:18:29.274821+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6d0df780-7b33-48db-b2ce-d6ed4ac4a88c	OCC-013	Solenoid coil Large	Solenoid coil Large	consumable	f	pieces	OCC-013	\N	\N	{}	2025-10-09 10:19:09.252203+00	2025-10-09 10:19:09.252203+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
61f49b97-5bd6-4fba-baa0-c4189b54f384	OCC-014	Solenoid coil Small	Solenoid coil Small	consumable	f	pieces	OCC-014	\N	\N	{}	2025-10-09 10:19:34.122728+00	2025-10-09 10:19:34.122728+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2018d454-4d26-41e0-8959-4e41945d68ad	1	1	1	consumable	f	pieces	1	\N	\N	{/static/images/d9c14be8-3a35-4a55-8ec3-fafbc2ca4fe2_13.png}	2025-09-22 04:38:11.37583+00	2025-09-24 16:48:15.157613+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b3749be0-2022-4674-a851-a1589f0ab79f	OCC-006	PLC controller, Class D V3.1B	PLC controller, Class D V3.1B	consumable	f	pieces	OCC-006	\N	\N	{}	2025-10-09 10:16:14.84763+00	2025-10-09 10:16:14.84763+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
dd5b24be-ee0c-4139-9f00-41e7a4589b23	OCC-007	Throttle switch dash	Throttle switch dash	consumable	f	pieces	OCC-007	\N	\N	{}	2025-10-09 10:16:39.79165+00	2025-10-09 10:16:39.79165+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3e34d38a-784c-40df-9a86-6c0056b39fce	OCC-008	Panel toggle switch set (2 position)	Panel toggle switch set (2 position)	consumable	f	pieces	OCC-008	\N	\N	{}	2025-10-09 10:17:05.238444+00	2025-10-09 10:17:05.238444+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7845e735-90ee-434d-afe9-7b1b58f24033	OCC-009	Ignition key switch Isuzu	Ignition key switch Isuzu	consumable	f	pieces	OCC-009	\N	\N	{}	2025-10-09 10:17:27.73598+00	2025-10-09 10:17:27.73598+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
eef95479-4cfa-460e-80bf-2417d2031325	OCC-015	Directional solenoid cartridge valve	Directional solenoid cartridge valve	consumable	f	pieces	OCC-015	\N	\N	{}	2025-10-09 10:20:38.833203+00	2025-10-09 10:20:38.833203+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cbc5857b-f4b9-41e2-a9ef-f5fa3b4048f0	OCC-016	PLC controller V4	PLC controller V4	consumable	f	pieces	OCC-016	\N	\N	{/static/images/3f8e4f54-1122-4e31-84db-57e77c2c524d_OOC-016.jpg}	2025-10-09 10:28:19.646996+00	2025-10-09 10:28:19.646996+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b1325a67-f6d8-4dab-a8d1-c236663559e6	OCC-017	Relay insert V4	Relay insert V4	consumable	f	pieces	OCC-017	\N	\N	{/static/images/a830eca0-0f15-4387-ba0c-21e11fc3120c_OOC-017.jpg}	2025-10-09 10:23:43.906256+00	2025-10-09 10:28:43.6894+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6717b695-8983-47a6-885a-f2df0fdedf4b	PP-001	Sacrificial anode (pontoon)	Sacrificial anode (pontoon)	consumable	f	pieces	PP-001	\N	\N	{}	2025-10-09 10:30:01.107637+00	2025-10-09 10:30:01.107637+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6b305bae-082b-405f-b9fb-d87173c25f16	PP-008	Pontoon lid	Pontoon lid	consumable	f	pieces	PP-008	\N	\N	{}	2025-10-09 10:32:39.00582+00	2025-10-09 10:32:39.00582+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1cc7e5ee-1ed0-4503-8da0-e8f27fe6a796	PP-002	Lifting strap - long	Lifting strap - long	consumable	f	pieces	PP-002	\N	\N	{}	2025-10-09 10:30:29.383102+00	2025-10-09 10:30:29.383102+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
89b277a7-f8d6-462d-b46f-e243c21acd13	PP-003	Lifting strap - short	Lifting strap - short	consumable	f	pieces	PP-003	\N	\N	{}	2025-10-09 10:31:09.215441+00	2025-10-09 10:31:09.215441+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
140b1db2-90b7-4bc8-b095-ab43e07cf139	RS-004	Remote TX handheld WHITE - for AutoBoss V31.B	Remote TX handheld WHITE - for AutoBoss V31.B	consumable	f	pieces	RS-004	\N	\N	{/static/images/cb322ac2-a0ef-47f7-b888-f1fdfd541322_RS-002.jpg}	2025-10-09 10:47:00.722093+00	2025-10-09 10:58:10.798533+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a2e3ab0f-04ba-4a90-974d-5bf4bd06046c	RS-002	Remote Tx handheld GREEN - for AutoBoss V31.B	Remote Tx handheld GREEN - for AutoBoss V31.B	consumable	f	pieces	RS-002	\N	\N	{/static/images/d76759f6-b57c-43e4-a5eb-4f0516a55d64_RS-002.jpg}	2025-10-09 10:44:28.912757+00	2025-10-09 10:58:32.263011+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4f6c90db-3433-417c-80c0-c6a1e6420c7f	PP-004	Hood stay kit	Hood stay kit	consumable	f	pieces	PP-004	\N	\N	{}	2025-10-09 10:31:31.239489+00	2025-10-09 10:31:31.239489+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7837ee79-0451-43c7-8e4f-f6cfb4fcada7	PP-006	Pontoon drain plug	Pontoon drain plug	consumable	f	pieces	PP-006	\N	\N	{}	2025-10-09 10:31:52.358437+00	2025-10-09 10:31:52.358437+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
54d54bbb-8b7f-4601-bb74-c28d2d1cffbd	RS-005	Remote TX handheld BLUE - for AutoBoss V31.B	Remote TX handheld BLUE - for AutoBoss V31.B	consumable	f	pieces	RS-005	\N	\N	{/static/images/dd537803-228e-45be-950b-72ca88872353_RS-002.jpg}	2025-10-09 10:47:50.882308+00	2025-10-09 10:57:44.763144+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bc10ef4e-ef68-4575-80ce-f5182ae9ea7c	PP-007	Sight Glass Kit	Sight Glass Kit	consumable	f	pieces	PP-007	\N	\N	{}	2025-10-09 10:32:14.981981+00	2025-10-09 10:32:14.981981+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b5569d72-78ae-4e81-9b02-2131a6ecccef	PRC-001	Thruster unit prop - universal	Thruster unit prop - universal	consumable	f	pieces	PRC-001	\N	\N	{}	2025-10-09 10:33:10.336157+00	2025-10-09 10:33:10.336157+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
270ef704-ebd5-44d5-bff9-ab3b6901cd36	PRC-002	Pontoon twin thruster hose assy	Pontoon twin thruster hose assy	consumable	f	pieces	PRC-002	\N	\N	{}	2025-10-09 10:34:11.807962+00	2025-10-09 10:34:11.807962+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d9ab3903-f2df-47e6-a43d-e0fb8a9729bb	PRC-003	Mounting bolts	Mounting bolts	consumable	f	pieces	PRC-003	\N	\N	{/static/images/6514d41e-1d02-4054-b284-83a50bf87912_PRC-003.jpg}	2025-10-09 10:35:27.327051+00	2025-10-09 10:35:27.327051+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c1274b14-2ec5-4f79-9d45-7b182be21fa3	PRC-004	Mounting Washers	Mounting Washers	consumable	f	pieces	PRC-004	\N	\N	{/static/images/9199bd9c-b30f-4069-bffe-63e232367f44_PRC-004.jpg}	2025-10-09 10:36:09.473559+00	2025-10-09 10:36:09.473559+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
65e51f56-f3aa-4336-a327-aaf145786c7f	WHC-011	Rotary union elbow	Rotary union elbow	consumable	f	pieces	WHC-011	\N	\N	{}	2025-10-22 14:12:55.708688+00	2025-10-22 14:12:55.708688+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
73cd252d-a9ce-4f34-b239-87152ae92830	RS-009	Remote Tx handheld BLACK - for AutoBoss V31.B	Remote Tx handheld BLACK - for AutoBoss V31.B	consumable	f	pieces	RS-009	\N	\N	{/static/images/29c5f73f-bb53-43c5-820f-b75587af684e_RS-002.jpg}	2025-10-09 10:55:55.51846+00	2025-10-09 10:57:00.022714+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e028f39d-38ff-4cdf-b4dc-d74f48f893b6	RS-001	Remote receiver,FIXED (Rx) - for AutoBoss V31.B	Remote receiver,FIXED (Rx) - for AutoBoss V31.B	consumable	f	pieces	RS-001	\N	\N	{}	2025-10-09 10:41:57.745678+00	2025-10-09 10:57:24.023419+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0cce0a8d-bfa9-4966-8b15-01e58d7bc3ce	RS-003	Remote TX handheld YELLOW - for AutoBoss V31.B	Remote TX handheld YELLOW - for AutoBoss V31.B	consumable	f	pieces	RS-003	\N	\N	{/static/images/1c3f27f8-24e4-4a01-b943-c1818e908dfa_RS-002.jpg}	2025-10-09 10:46:11.224339+00	2025-10-09 10:58:20.501862+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fbd0c00c-10a0-45f7-b529-2a3db08ebef0	RS-014	Rubber mount	Rubber mount	consumable	f	pieces	RS-014	\N	\N	{}	2025-10-09 11:08:48.483169+00	2025-10-09 11:08:48.483169+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8a3412e6-a9cd-406a-9107-c0875e789a62	RS-023	Android Device	Android Device	consumable	f	pieces	RS-023	\N	\N	{}	2025-10-09 11:09:23.593198+00	2025-10-09 11:09:23.593198+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3ae3f608-27e4-400f-aa1c-cb9607042a1b	RS-024	Remote TX handheld RED - for AutoBoss V31.B	Remote TX handheld RED	consumable	f	pieces	RS-024	\N	\N	{/static/images/74929b8d-b24f-4918-8086-2719d8125feb_RS-002.jpg}	2025-10-09 11:10:26.879834+00	2025-10-09 11:10:49.145724+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0f545e1b-2f13-4c55-8e3d-dd0cd0856553	RS-025	Remote TX handheld BROWN	Remote TX handheld BROWN	consumable	f	pieces	RS-025	\N	\N	{/static/images/5f8c3127-d658-4bc9-ae5f-3bef3ff47384_RS-002.jpg}	2025-10-09 11:13:47.24051+00	2025-10-09 11:13:47.24051+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
788452f5-5e6e-45dc-8c37-235974ad8dc7	RS-026	Remote TX handheld ORANGE	Remote TX handheld ORANGE	consumable	f	pieces	RS-026	\N	\N	{/static/images/18e9951c-1d4a-457c-9d8b-8a5177970dd4_RS-002.jpg}	2025-10-09 11:18:55.005117+00	2025-10-09 11:18:55.005117+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c8702e14-6ada-4881-8855-955b81c480ed	RS-027	Remote TX handheld PURPLE	Remote TX handheld PURPLE	consumable	f	pieces	RS-027	\N	\N	{/static/images/8aa269f6-b72d-44bf-9460-22d701936c50_RS-002.jpg}	2025-10-09 11:20:04.607777+00	2025-10-09 11:20:04.607777+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
51e22702-0843-44c6-9ddd-4a10bf14d8aa	TLS-001	Needle for grease gun	Needle for grease gun	consumable	f	pieces	TLS-001	\N	\N	{}	2025-10-09 11:28:22.965149+00	2025-10-09 11:28:22.965149+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
719755ef-949d-42ac-b2fb-6b3d51208c00	UMB-002	Umbilical short 20m	Umbilical short 20m	consumable	f	pieces	UMB-002	\N	\N	{}	2025-10-09 11:29:01.507364+00	2025-10-09 11:29:01.507364+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ae8542d5-4282-4b8a-bfb9-404800c11193	UMB-003	Umbilical - Long	Umbilical - Long	consumable	f	pieces	UMB-003	\N	\N	{}	2025-10-09 11:29:39.216518+00	2025-10-09 11:29:39.216518+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a5db6d81-f4a4-4619-a557-65652d229c3e	UMB-004.0	3/4 tailx1/2BSPT stainsteel (set w/UMB-005.0)	3/4 tailx1/2BSPT stainsteel (set w/UMB-005.0)	consumable	f	pieces	UMB-004.0	\N	\N	{}	2025-10-09 11:30:28.345752+00	2025-10-09 11:30:28.345752+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a2b0ce96-f99d-44db-bdd6-a58573e62fde	UMB-005.0	3/4 1&2 wire ferrule (set w/ UMB-004.0)	3/4 1&2 wire ferrule (set w/ UMB-004.0)	consumable	f	pieces	UMB-005.0	\N	\N	{}	2025-10-09 11:30:50.870606+00	2025-10-09 11:30:50.870606+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fbb5ad47-0e56-410e-a5e0-50027a518b4d	UMB-006	Umbilical spiral guard wrap	Umbilical spiral guard wrap	consumable	f	pieces	UMB-006	\N	\N	{}	2025-10-09 11:31:35.659554+00	2025-10-09 11:31:35.659554+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
dd3b0459-59fa-4efd-a229-f7d3de22b051	UMB-007	HP water hose crimp fittings kit	HP water hose crimp fittings kit	consumable	f	pieces	UMB-007	\N	\N	{}	2025-10-09 11:31:55.329569+00	2025-10-09 11:31:55.329569+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a12902f3-dfdc-4940-af5b-e517d679f79f	UMB-008	Test tool	Test tool	consumable	f	pieces	UMB-008	\N	\N	{/static/images/e9bee473-a088-4b1a-9aa1-c012f0b6585c_UMB-008.png}	2025-10-09 11:34:33.890303+00	2025-10-09 11:35:55.628691+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8f3b4ce1-621a-4523-8338-cbc8393f8197	UMB-009	Hyd hose crimp fitting kit 1/2 inch	Hyd hose crimp fitting kit 1/2 inch	consumable	f	pieces	UMB-009	\N	\N	{}	2025-10-09 11:37:17.564896+00	2025-10-09 11:37:17.564896+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5084ea69-4221-42e3-bdb9-eeed59e20cd9	UMB-010	Complete 20m umbilical - short, wrapped	Complete 20m umbilical - short, wrapped	consumable	f	pieces	UMB-010	\N	\N	{}	2025-10-09 11:37:45.079231+00	2025-10-09 11:37:45.079231+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4764a18e-749d-4d01-8295-aa5c2cf4f98f	UMB-011	Complete 30m umbilical - long, wrapped	Complete 30m umbilical - long, wrapped	consumable	f	pieces	UMB-011	\N	\N	{}	2025-10-09 11:38:15.207791+00	2025-10-09 11:38:15.207791+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d8ea2ca1-ad7e-41bb-b10b-e733268adf85	WHC-002	Universal hydraulic motor for prop thruster	Universal hydraulic motor for prop thruster	consumable	f	pieces	WHC-002	\N	\N	{/static/images/ebd3c8ca-929d-4281-a88e-1aec9a2eb07b_WHC-002.jpg}	2025-10-22 14:05:47.000238+00	2025-10-22 14:05:47.000238+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7d8d8466-9f7a-4563-b45b-1986f47e13c9	WHC-003	Washhead HP water hose	Washhead HP water hose	consumable	f	pieces	WHC-003	\N	\N	{}	2025-10-22 14:07:20.853621+00	2025-10-22 14:07:20.853621+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
74cc670d-986a-4258-8db9-ed920a1e7b4a	WHC-004	Wash Head Disc	Wash Head Disc	consumable	f	pieces	WHC-004	\N	\N	{}	2025-10-22 14:07:59.559441+00	2025-10-22 14:07:59.559441+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b5181487-7590-4660-bb8d-d342f849feff	WHC-006	Brass hydraulic QRC set	Brass hydraulic QRC set	consumable	f	pieces	WHC-006	\N	\N	{/static/images/afcd6c4d-5f43-41a7-ac7c-68009311bac7_WHC-006.1.jpg}	2025-10-22 14:10:03.679269+00	2025-10-22 14:10:03.679269+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
afd6e97d-0af8-4cf5-ad74-e316285a22e6	WHC-006.1	S/S hydraulic QRC set	S/S hydraulic QRC set	consumable	f	pieces	WHC-006.1	\N	\N	{/static/images/dd3aaa24-c031-4695-b0c7-3c04e2e81a1f_WHC-006.1.jpg}	2025-10-22 14:10:40.20239+00	2025-10-22 14:10:40.20239+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
eedcdb24-04a2-4ce2-98c6-3890b58c883c	WHC-007	Ceramic jets 0.9mm	Ceramic jets 0.9mm	consumable	f	pieces	WHC-007	\N	\N	{}	2025-10-22 14:11:40.040807+00	2025-10-22 14:11:40.040807+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ca0d3c00-f667-4c52-8335-1953bafacc42	WHC-008	Rotary union kit	Rotary union kit	consumable	f	pieces	WHC-008	\N	\N	{}	2025-10-22 14:12:16.985825+00	2025-10-22 14:12:16.985825+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
47fb6a54-24cc-4c9a-a3b9-306f02fd1d7e	WHC-012	Prop compression Vee seal	Prop compression Vee seal	consumable	f	pieces	WHC-012	\N	\N	{}	2025-10-22 14:13:39.581328+00	2025-10-22 14:13:39.581328+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f1aa32fa-0c5c-4c17-85d5-c96920e39d42	WHC-015	Prop mounting bolts s/s	Prop mounting bolts s/s	consumable	f	pieces	WHC-015	\N	\N	{}	2025-10-22 14:14:57.774376+00	2025-10-22 14:14:57.774376+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
df4677d3-dbac-4eed-bc87-2c1b6c8b2886	WHC-016	Prop mounting washer s/s	Prop mounting washer s/s	consumable	f	pieces	WHC-016	\N	\N	{}	2025-10-22 14:15:16.953+00	2025-10-22 14:15:16.953+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
227de5b4-4b5a-4812-8f2e-e4bb2ff4fbda	WHC-020	Prop guard cover	Prop guard cover	consumable	f	pieces	WHC-020	\N	\N	{}	2025-10-22 14:15:45.18719+00	2025-10-22 14:15:45.18719+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9f58523c-30d4-4012-8d66-1f4643cdd932	WHC-021	Grease nipple concave	Grease nipple concave	consumable	f	pieces	WHC-021	\N	\N	{}	2025-10-22 14:16:10.903981+00	2025-10-22 14:16:10.903981+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
52565a93-8e97-4f82-a78f-02eac3b9bfcf	WHC-022	Prop motor shaft key (key way)	Prop motor shaft key (key way)	consumable	f	pieces	WHC-022	\N	\N	{}	2025-10-22 14:16:35.470336+00	2025-10-22 14:16:35.470336+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5e4531f3-a807-47fd-a477-b591b13d4e36	WHC-023	Rotary Union S/S	Rotary Union S/S	consumable	f	pieces	WHC-023	\N	\N	{}	2025-10-22 14:16:58.490137+00	2025-10-22 14:16:58.490137+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e162f24a-ef8c-4a37-9d31-f9672844d19e	WHC-024	Plastic winch stopper	Plastic winch stopper	consumable	f	pieces	WHC-024	\N	\N	{}	2025-10-22 14:17:24.953479+00	2025-10-22 14:17:24.953479+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d357fad8-18eb-4db0-8595-fb6eab5467ae	WWC-001	Walking Wheel Cam Roller kit	Walking Wheel Cam Roller kit	consumable	f	pieces	WWC-001	\N	\N	{}	2025-10-22 14:17:56.748469+00	2025-10-22 14:17:56.748469+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0ea2d299-674b-4747-b1b8-bad1d1338e63	WHC-013	Disc mounting screw	Disc mounting screw	consumable	f	pieces	WHC-013	\N	\N	{/static/images/f074144b-50c6-4c11-8020-481109093849_WWC-013.jpg}	2025-10-22 14:14:09.821122+00	2025-10-22 15:34:00.781895+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
38f6c110-dbda-49da-ae6b-66a18040a57a	WWC-001.1	Walking wheel cam Roller kit- heavy duty	Walking wheel cam Roller kit- heavy duty	consumable	f	pieces	WWC-001.1	\N	\N	{}	2025-10-22 14:18:18.43914+00	2025-10-22 14:18:18.43914+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
73a81383-1266-4259-93a9-fccd06ac7f9d	WWC-002	Proximity sensor	Proximity sensor	consumable	f	pieces	WWC-002	\N	\N	{/static/images/2d6bd133-961f-4875-a05d-1998a14cdc5a_WWC-002.jpg}	2025-10-22 14:18:49.683797+00	2025-10-22 14:18:49.683797+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4f5c5d6f-29ed-4e14-9078-c9a1c4668141	WWC-002.1	Proximity Sensor new style	Proximity Sensor new style	consumable	f	pieces	WWC-002.1	\N	\N	{}	2025-10-22 14:19:26.196129+00	2025-10-22 14:19:26.196129+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f4f68bf7-0fc7-440e-92cc-f7ffe7a6bd7f	WWC-004	Walking Wheel assembly	Walking Wheel assembly	consumable	f	pieces	WWC-004	\N	\N	{/static/images/c3a2e269-62df-43b5-854e-c5db185deed2_WWC-004.jpg}	2025-10-22 14:21:09.167094+00	2025-10-22 14:21:09.167094+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
43854349-10f8-4d19-909a-2430b9fe0f71	WWC-002.2	Magnetic insert-proximity sensor new	Magnetic insert-proximity sensor new	consumable	f	pieces	WWC-002.2	\N	\N	{}	2025-10-22 14:19:51.279443+00	2025-10-22 14:19:51.279443+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6c3e241f-2c51-47ee-bf9f-483aa4a85603	WWC-003	Bungee kit (6x bungees)	Bungee kit (6x bungees)	consumable	f	pieces	WWC-003	\N	\N	{}	2025-10-22 14:20:31.673467+00	2025-10-22 14:20:31.673467+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
32d4ea30-b6b9-47f8-97a0-249b86621fb5	WWC-005	Top camplate centre spacer	Top camplate centre spacer	consumable	f	pieces	WWC-005	\N	\N	{}	2025-10-22 15:23:44.831258+00	2025-10-22 15:23:44.831258+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e1457957-9441-48d9-a161-75faff16bd5d	WHC-005	Rotary union	Rotary union	consumable	f	pieces	WHC-005	\N	\N	{/static/images/7754acf6-6473-4bf7-b8b9-0244f3b581d2_WWC-005.jpg}	2025-10-22 14:09:10.113248+00	2025-10-22 15:24:14.830569+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0b84274d-ffd6-4c3e-9074-f2682b2390bc	WWC-007	Lower nylon spacer	Lower nylon spacer	consumable	f	pieces	WWC-007	\N	\N	{/static/images/fdf0a615-cbf6-4763-9be3-480ee0658a45_WWC-007.jpg}	2025-10-22 15:25:06.75836+00	2025-10-22 15:25:06.75836+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1b2688b4-4ae3-497f-94fc-f76449cab3cd	WWC-008	Upper nylon spacer	Upper nylon spacer	consumable	f	pieces	WWC-008	\N	\N	{/static/images/1e8f8f72-c5ea-4bfa-bdbb-a96cf58f2177_WWC-008.jpg}	2025-10-22 15:25:47.664787+00	2025-10-22 15:25:47.664787+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f8f2c890-4ef9-41ce-ab46-7d8dd3c46920	WWC-009	Plastic wheel advance arm	Plastic wheel advance arm	consumable	f	pieces	WWC-009	\N	\N	{}	2025-10-22 15:26:18.223869+00	2025-10-22 15:26:18.223869+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4203555a-c6e1-49e1-9ce9-99ab757ea12e	WWC-010L	Top camplate assy L (inc bearing and seal)	Top camplate assy L (inc bearing and seal)	consumable	f	pieces	WWC-010L	\N	\N	{}	2025-10-22 15:26:46.923588+00	2025-10-22 15:26:46.923588+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
409c9118-26c3-45d1-b41d-78c4be698c41	WWC-010R	Top camplate assy R (inc bearing and seal)	Top camplate assy R (inc bearing and seal)	consumable	f	pieces	WWC-010R	\N	\N	{}	2025-10-22 15:27:06.485448+00	2025-10-22 15:27:06.485448+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5de75057-91db-481c-9bed-afbcdfefcd64	WWC-011	Wheel assembly bolt kit (x18)	Wheel assembly bolt kit (x18)	consumable	f	pieces	WWC-011	\N	\N	{}	2025-10-22 15:27:41.515324+00	2025-10-22 15:27:41.515324+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fe805357-6ce6-43fe-9757-f0eb05e043c6	WWC-012	Wheel assembly, modified fingers (small)	Wheel assembly, modified fingers (small)	consumable	f	pieces	WWC-012	\N	\N	{}	2025-10-22 15:28:01.73199+00	2025-10-22 15:28:01.73199+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9760083a-e78f-4407-9ca7-2df8fe24f521	WWC-013	Walking wheel finger - straight	Walking wheel finger - straight	consumable	f	pieces	WWC-013	\N	\N	{}	2025-10-22 15:30:21.044051+00	2025-10-22 15:30:21.044051+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c24f9949-ac15-46aa-b4db-e4b7260dfa0e	WWC-014	Walking wheel fingers - retro	Walking wheel fingers - retro	consumable	f	pieces	WWC-014	\N	\N	{}	2025-10-22 15:30:40.560622+00	2025-10-22 15:30:40.560622+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
dbe3456a-7bdd-424a-aadd-e799c888cefd	WWC-015	Wheel Assembly - heavy duty	Wheel Assembly - heavy duty	consumable	f	pieces	WWC-015	\N	\N	{}	2025-10-22 15:31:11.453148+00	2025-10-22 15:31:11.453148+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
83b9bc63-16d6-440b-8468-71f7b84b892b	WWC-016	Walking wheel support arm (Leading)	Walking wheel support arm (Leading)	consumable	f	pieces	WWC-016	\N	\N	{}	2025-10-22 15:31:32.903452+00	2025-10-22 15:31:32.903452+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
280f3850-d867-43a4-8291-1a649c9e3f42	WHC-014	Springs, disc return	Springs, disc return	consumable	f	pieces	WHC-014	\N	\N	{/static/images/ddaad6d9-e8a8-40c4-858b-f8bfe1900f91_WWC-014.jpg}	2025-10-22 14:14:32.008466+00	2025-10-22 15:32:48.19764+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
02d7bd11-e8f3-4f3e-8d87-4f38bf92c8b7	EP-007	Engine cooling pump impeller	Engine cooling pump impeller	consumable	f	pieces	EP-007	\N	\N	{"/static/images/385beeac-2caa-457c-bb96-e493b1caf2ab_Yanmar cooling pump impeller.jpg"}	2025-09-20 08:13:48.343494+00	2025-10-22 15:35:07.2148+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9b6b218d-6f66-4f12-ad1b-b61825af7265	HYD-011	Hydraulic pump drive belt V3	Hydraulic pump drive belt V3\nMANY BX 35.5	consumable	f	pieces	HYD-011	\N	\N	{/static/images/d6889dd7-f229-4b2f-9b9f-5c07f6f2399e_IMG-20251120-WA0004.jpeg,/static/images/717e39df-ada9-45a5-bc00-8f6bea0fdc5d_IMG-20251120-WA0003.jpg}	2025-09-20 08:56:27.577351+00	2025-11-20 09:25:52.107258+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: predictive_maintenance_models; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.predictive_maintenance_models (id, name, description, model_type, target_metric, features, hyperparameters, performance_metrics, version, is_active, created_at, updated_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: security_event_logs; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.security_event_logs (id, "timestamp", event_type, severity, user_id, organization_id, description, details, ip_address, user_agent, endpoint, resolved, resolved_at, resolved_by, resolution_notes, created_at, updated_at) FROM stdin;
b5112a38-58ba-42bd-94e8-0da84d155aab	2025-07-31 11:45:23.98483+00	ORGANIZATIONAL_ISOLATION_VIOLATION	HIGH	f5abc444-4a5b-5e6f-7a8b-9c0123456789	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	User f5abc444-4a5b-5e6f-7a8b-9c0123456789 attempted to access ORGANIZATION from organization a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	{"user_organization_id": "b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01", "attempted_organization_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "resource_type": "ORGANIZATION", "action": "ACCESS_VALIDATION"}	\N	\N	\N	OPEN	\N	\N	\N	2025-07-31 11:45:23.973329+00	2025-07-31 11:45:23.973329+00
0b33cc12-7151-4058-ba87-986766ec7a2e	2025-07-31 11:45:24.013732+00	TEST_SECURITY_EVENT	LOW	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	Test security event	{"test": "security_event"}	127.0.0.1	test-agent	/test	OPEN	\N	\N	\N	2025-07-31 11:45:24.012678+00	2025-07-31 11:45:24.012678+00
03e5e6c3-6dc3-4c7a-8a98-673cf07bbfdf	2025-07-31 11:45:24.079991+00	SUPPLIER_VISIBILITY_VIOLATION	MEDIUM	f5abc444-4a5b-5e6f-7a8b-9c0123456789	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	User f5abc444-4a5b-5e6f-7a8b-9c0123456789 attempted to access supplier b489b169-085d-4611-b2fb-f3ca4fe59112 outside their organization	{"attempted_supplier_id": "b489b169-085d-4611-b2fb-f3ca4fe59112", "action": "READ", "violation_type": "SUPPLIER_VISIBILITY_DENIED"}	127.0.0.1	\N	\N	OPEN	\N	\N	\N	2025-07-31 11:45:24.07305+00	2025-07-31 11:45:24.07305+00
6a9113fd-ddfa-474a-8d60-55b833b453a6	2025-07-31 11:45:24.089297+00	BOSSAQUA_ACCESS_VIOLATION	HIGH	f5abc444-4a5b-5e6f-7a8b-9c0123456789	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Non-superadmin user f5abc444-4a5b-5e6f-7a8b-9c0123456789 (role: admin) attempted BossAqua access: READ	{"user_role": "admin", "action": "READ", "violation_type": "BOSSAQUA_ACCESS_DENIED"}	\N	\N	\N	OPEN	\N	\N	\N	2025-07-31 11:45:24.084833+00	2025-07-31 11:45:24.084833+00
d0a7e9ae-fc43-488f-8e30-2a13d05a5b3b	2025-07-31 11:45:24.095009+00	BOSSAQUA_ACCESS_VIOLATION	HIGH	d13e1a2f-c773-4d6c-ba6d-243238c7a563	c2525ea0-dfec-4e6b-ae47-e70bae0e9078	Non-superadmin user d13e1a2f-c773-4d6c-ba6d-243238c7a563 (role: user) attempted BossAqua access: READ	{"user_role": "user", "action": "READ", "violation_type": "BOSSAQUA_ACCESS_DENIED"}	\N	\N	\N	OPEN	\N	\N	\N	2025-07-31 11:45:24.092514+00	2025-07-31 11:45:24.092514+00
59333ef0-3ca0-4ab9-8ec0-61d36ecca694	2025-07-31 11:45:24.10314+00	BOSSAQUA_ACCESS_VIOLATION	HIGH	f5abc444-4a5b-5e6f-7a8b-9c0123456789	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Non-superadmin user f5abc444-4a5b-5e6f-7a8b-9c0123456789 (role: admin) attempted BossAqua access: READ	{"user_role": "admin", "action": "READ", "violation_type": "BOSSAQUA_ACCESS_DENIED"}	127.0.0.1	\N	\N	OPEN	\N	\N	\N	2025-07-31 11:45:24.098293+00	2025-07-31 11:45:24.098293+00
eadb862d-e4ba-45dc-a80a-4176e5f6a34e	2025-07-31 11:45:24.119417+00	TEST_CONTEXT_SECURITY	LOW	f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	Test context security event	{"context_test": true}	\N	\N	\N	OPEN	\N	\N	\N	2025-07-31 11:45:24.117263+00	2025-07-31 11:45:24.117263+00
\.


--
-- Data for Name: security_events; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.security_events (id, user_id, event_type, ip_address, user_agent, session_id, details, "timestamp", risk_level) FROM stdin;
54029dff-aa9d-4828-a002-1fa2631726cc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-17 13:01:53.639373+00	low
9d877fe4-5505-453e-aedb-1d4988271e59	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-17 13:03:01.038884+00	low
49bdb14a-5f3e-4d99-aa5a-b3a13c02df79	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-18 10:21:41.139515+00	low
8e301bf7-4694-4448-9eca-26e8b98becac	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-18 10:40:36.299058+00	low
d085de23-7261-48e6-a43f-b33a8c5a397e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-18 11:04:38.476701+00	low
372186a2-4cf0-4d58-b41a-2398db2dcbb2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-18 12:58:48.59407+00	low
a80c8fb9-52b2-42be-b0c9-badf5aeb6346	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-18 12:59:07.694312+00	low
d96ecfc6-fb4c-4ccf-bd16-011406823bb4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-18 14:00:40.131225+00	low
0b41a91e-baf9-4b55-9fa0-aaa1b9238a55	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-19 22:48:28.41456+00	low
6d6c582a-9c81-4a75-90c1-fcf307168b89	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-19 23:29:27.664632+00	low
4b95cf6f-fc71-4605-88bb-48b103e638c2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-19 23:32:58.233055+00	low
9baa421c-87dc-415a-a2dd-ff1632bf8bae	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-19 23:42:14.927306+00	low
8181303b-35ff-49e0-ba6b-196299abcda0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-20 00:04:44.378373+00	low
11602c4d-f81e-4565-ba88-3d2f2497557f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 00:05:50.52323+00	low
52105425-f39e-4273-9741-70d334b8f2d6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 00:07:28.755322+00	low
9d6eddf3-a7fd-4af0-a8a0-79f6aed86c02	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 00:12:24.127496+00	low
25818bbd-602c-462f-9578-aa7223edec14	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 00:17:12.342379+00	low
07a8000b-60e8-4ddd-b500-ff0cdcac995f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 00:38:13.704111+00	low
e04504b3-1cfd-43eb-a837-a4eb368d4615	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 00:52:43.17166+00	low
f6b5e44b-e7d2-4ad5-9a16-5e4632e4ed83	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 01:12:02.93065+00	low
b00025dd-dc70-4f9e-9245-de8f1602e258	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 08:41:18.958282+00	low
2524993b-015c-4fbf-9d94-6e08d9003482	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 09:02:57.33362+00	low
21c6dfcd-e3a2-4ae5-a7a9-cc2ea550812b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:06:03.643406+00	low
b1c216f9-cde3-445a-8893-762d97199ea7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:06:24.666494+00	low
06425339-4c33-4fcf-ac78-250379654100	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:06:51.557919+00	low
9d431f9d-1114-4abe-b65d-20e2d2f01741	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:07:07.147173+00	low
42673c47-593c-4760-911f-d5a73c9db699	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:07:44.864321+00	low
e758ffc0-8b90-43d2-ae39-dfc114551f77	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:28:51.764805+00	low
1dbe4d99-af5d-44ef-b988-7e3f451f361f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:31:00.963418+00	low
d866cb1b-02e1-4211-b196-e269b44b6369	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-20 17:33:25.24112+00	low
92580426-160d-485b-88a1-4aab043084b0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 10:30:09.007663+00	low
b56d32e8-6cb3-4e6c-adcc-ba5d5bc61e00	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 10:30:28.973712+00	low
0d7aa4a7-fc7c-4224-b4ec-acd251487551	b0ccc999-9c0c-0d12-3456-789012345678	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:25:11.720573+00	low
0694b2d8-2138-4691-8e2e-f3a31cc98de9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:25:23.503192+00	low
c2177508-3c8e-4f0a-9635-75c522f6d89a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:38:02.205178+00	low
880fea26-78cd-44ca-a5f9-8e3118d26b1c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:38:42.546831+00	low
2c41f21f-9f88-4040-9ce3-8e19055c2215	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:39:01.134168+00	low
dfec6612-4b31-4292-9226-0bc12ff315cc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:49:19.460617+00	low
3e672d86-6aac-4199-9a19-cd9fff3d7b6e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:49:37.336903+00	low
a6efc8ea-16db-4ee7-8573-7055c9017377	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 13:57:46.938985+00	low
a5738195-a4d3-4ef2-a8be-fb96bacda75f	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:33:38.934476+00	low
4e5b24a4-d943-492f-b294-38976d74fa65	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:34:01.443439+00	low
b80be44c-3885-4376-8856-e6a9c7ae7372	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:35:02.209693+00	low
ee09e90e-e907-409d-98ec-8b273a621764	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:43:32.932807+00	low
885072cf-2f13-4a67-9da2-ad3a0088a750	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:43:49.346274+00	low
9a99c81e-f7e5-402f-be4f-1b9fbc851ef3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:48:48.79099+00	low
ef6c0bec-ebb3-4e58-b76e-b2cac3ba4af6	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 14:49:34.717838+00	low
437eced4-a16d-4a77-8389-8d657bcf7a88	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 15:02:47.291129+00	low
0585667b-eaf0-4b4a-a416-03e17bd15ee8	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 16:13:34.81377+00	low
29900c61-25f3-448a-8b7e-e7e30b904c79	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 17:03:04.414084+00	low
0d71dc0a-1f3d-46a4-aaa8-639bb2be9d4d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 17:20:31.477199+00	low
1e5e3863-4b6d-4505-bba2-8225cfbd3155	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 17:21:45.971496+00	low
f25cf42e-1f8b-4fd3-833c-3cad8410afc5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 17:22:01.163987+00	low
eb2bbf1e-614c-42dd-b102-f29b63622743	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 17:26:57.893803+00	low
70a23349-ac37-4931-a8a2-72f36af9c092	\N	login_failed	172.18.0.1	\N	\N	Login attempt for non-existent user: admin	2025-07-21 23:17:28.267447+00	low
93cac8d1-c067-43fc-ba60-5ea9311ffd85	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 23:18:36.074313+00	low
a22f8e05-bfbb-469c-988d-a84f08f3ad43	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 23:23:23.595925+00	low
30e69bcb-3fcc-4836-9f13-d65067315372	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-21 23:23:52.514119+00	low
e0970255-c6c4-4455-8b09-7facc8d36300	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 09:41:50.086105+00	low
9594f3f8-ad3e-4ee6-87fb-b4fbc0ac3b7a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 10:02:17.375979+00	low
863a24a5-df1e-4e8e-bb9b-e84398cf5f1d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 10:14:26.698884+00	low
7f60bbb2-47b0-4b1c-8df6-513a2c59b292	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 10:28:33.186091+00	low
a5e83ae9-4500-464e-a3e0-bad6dd16ed84	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 10:48:22.845014+00	low
953160b8-c6a2-4ecf-8746-3d75bb3198b2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:01:21.603452+00	low
1a228e04-f6ed-4c4d-b7eb-62110fd80843	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:01:45.197305+00	low
738b3c76-0f9f-439e-bffa-7ff26dcf8ed5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:19:46.827072+00	low
963a0a48-11bb-4b63-8bf9-1f5382a59641	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:19:49.491152+00	low
d9f83c58-0a14-45f6-a763-c28ddff02dc2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:19:50.461377+00	low
dae0efcb-655e-4784-9e50-f9a252045b3c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:19:59.022023+00	low
2aed13a1-6cf1-41d6-93dc-1f524705a19c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:20:07.616368+00	low
97b3c509-9cb8-48c9-8fbf-96b7c39e0aa2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:20:09.937066+00	low
98f822eb-84c6-40f4-9aaf-96deaea9e8e0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:22:54.502194+00	low
4c5e24a9-349a-40ea-b7ad-4d185036cfea	\N	login_failed	172.18.0.1	\N	\N	Login attempt for non-existent user: admin	2025-07-22 14:23:19.221708+00	low
bec52a0a-1c9b-43ce-8cfb-aef46c229554	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:24:33.540172+00	low
5b332aff-775e-4a5a-b80f-78b4b7161e52	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:25:41.221854+00	low
b253e84a-bcad-4686-b4c9-3373d3fc631b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:25:47.131106+00	low
fd275e7c-842c-48b4-8255-2303d20f15a2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:33:39.557699+00	low
b9feb190-d7ee-4618-a79b-aa2e6ddda82b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:34:29.510973+00	low
e0b7e61b-51ca-409f-ae79-161b5fc4fb1d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:34:46.20924+00	low
e4c2d708-8f95-41b8-9687-d5fde447b811	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:34:57.580126+00	low
d8a82526-2787-461e-afe0-f659ec5bec90	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:35:40.150271+00	low
71b4cd19-1cc7-45a4-8975-f47ca131f913	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:35:48.757715+00	low
3e540219-c949-4aa0-a7cf-95733edd564d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:38:50.611913+00	low
f4aa11ba-65f4-476a-ac4c-e820efaa7dac	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:03.016757+00	low
a2b35c24-c661-40a6-87ee-e7914960039f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:07.030895+00	low
538ff58f-094d-4a9f-a983-b5a3a0cc0703	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:08.297101+00	low
8a8ce06f-56cd-4ede-8e7b-256721125158	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:09.188512+00	low
07bd56a4-280d-4dca-b75d-7e9d0c918a12	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:21.868304+00	low
3b4d04b8-400c-42df-b706-ebff1e3db1fb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:23.639535+00	low
5eb66955-3ff4-48ff-b287-8aca1bb2f0b6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:40:31.774843+00	low
27e5504d-623d-42ce-b038-b7e218c00457	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:43:42.005609+00	low
8a3132aa-dd37-4fa2-a0f0-a34b39d64255	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:43:46.683391+00	low
14714a4f-3a02-498c-b013-764584dd63ef	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:43:48.01691+00	low
fd9c891e-2555-4c14-bd03-a726ce9194f4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 14:51:53.90244+00	low
64a2ecdd-a560-47c4-8f39-7b3b925ccf7c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:00:22.327185+00	low
1f9e9324-1aef-48bf-9a08-53b2944a4474	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:00:23.350246+00	low
e6a67bce-0138-48dd-95ab-a86c5f9ede66	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:00:24.251966+00	low
9f2cb184-9853-43e8-842e-a8c39166305a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:03:41.359574+00	low
7fbc7730-0e0b-4435-8035-26465278da60	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:06:00.121365+00	low
52bd536e-87de-4066-8b77-884d3fd2fba0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:09:31.451205+00	low
9e365497-eaa7-4f1f-89db-3e7c8d63f57b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:09:36.988787+00	low
02641934-4111-4c92-a48d-62d6dc168aee	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:09:38.176742+00	low
3e7e98b6-9ff8-43f9-905b-76fb395c0017	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:17:26.295005+00	low
0c732c79-6f46-4773-b6dc-1c16fb645b3f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:17:44.691925+00	low
7778761c-0366-46d2-8fa4-7a2e7357b2c3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:17:54.49991+00	low
f9644d7c-e8ab-47a9-86f7-b6ceca344253	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:18:22.148844+00	low
ae290095-f40d-4110-a5a5-cbe5da94956c	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:24:04.295658+00	low
d9d166d3-d044-4c2e-bc09-285474117200	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:46:36.862438+00	low
281c2ab4-ff33-487e-adb6-42c48ffac6ce	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 15:47:04.398341+00	low
8064dff0-05e7-4845-b3e0-41aa66400d13	\N	login_failed	172.18.0.1	\N	\N	Login attempt for non-existent user: admin@oraseas.com	2025-07-22 16:03:05.329703+00	low
ab0dd7b4-52af-43dd-8de1-21c07007e0dc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 17:54:52.304836+00	low
ef3fe60e-cecf-47e6-9f15-dbf2c3f6cccd	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 17:56:14.846589+00	low
2e315c37-44b0-4868-9a2d-204d7410236c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 20:35:08.874666+00	low
274b4483-e8ab-4b89-b386-6a2d32952793	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 21:46:25.214013+00	low
6fb3ca06-0bd7-411d-9618-cb7b02103333	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-22 22:40:36.335298+00	low
7b7d7927-e903-4e23-ad92-386ec093a5aa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-23 09:23:26.026633+00	low
5a7106f5-bfe5-453b-80f8-2a101a3da0dd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-23 14:29:13.607419+00	low
264868c7-bcf1-4703-9acb-5b80c2fac33b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-23 14:43:16.558493+00	low
b7aa81f3-0f12-499f-9dfb-8894dc6ee036	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-23 14:51:42.125101+00	low
c80a3e17-59e8-452b-b676-6e2fa966ddbf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-24 07:53:34.808706+00	low
38cd12e6-42f6-41f8-9c1f-486600fd74a0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-24 23:18:51.116611+00	low
26428b18-1f41-4001-9a67-433bc640e1a2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:31:22.555581+00	low
05603db8-8f86-4f5f-a463-bfe96287e410	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:31:22.867283+00	low
e249e69b-615f-4bbc-91b1-cfce88d69d6a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:32:34.950246+00	low
4274400c-82e8-4e4b-9f38-e8857cccdfd3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:32:35.399137+00	low
f9a1cb41-176c-45ac-ae75-bb537adeaded	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:32:35.667672+00	low
5881c3ef-77a9-45ad-9f2b-94dd694b0d20	f6abc555-5b6c-6f7a-8b9c-0d123456789a	account_locked	127.0.0.1	\N	\N	Account locked after 5 failed attempts	2025-07-24 23:32:35.948262+00	medium
9a7918d3-36f1-4081-be94-d10d42e0a673	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:32:36.222374+00	low
af7eacaf-9f7c-4abc-aa1e-0c241ee51b86	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:32:36.310864+00	low
8f2c9fe9-e3c2-4946-8a9b-232821cdd222	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-24 23:32:36.589721+00	low
e8d41bdd-e80d-48da-9056-d96b77d1a6d9	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:32:36.869538+00	low
73f7eea1-cf70-4b6f-bcee-fe0aa076fb8c	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:32:58.020023+00	low
2b88ec5f-932d-4dc8-9423-6d7c3c60420a	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:33:47.87807+00	low
8ca933e9-40f4-4560-971c-2407ab901c47	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:34:22.980719+00	low
9799d870-5459-4c78-a2c9-20ddfbe68cd1	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-24 23:43:48.141384+00	low
5db66bdd-b959-409f-987f-5383cf4f9db3	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-24 23:44:15.333541+00	low
17169f76-dc83-4f62-adcd-f8074fe31f24	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-24 23:44:29.024345+00	low
0cdfa964-1226-418b-889e-126efe0cae10	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:46:47.757444+00	low
e17e7cdc-9a16-4389-bab8-0243aefe03fa	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:47:54.629171+00	low
05a22740-8ed2-4c4b-bb35-b875bbf75256	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	127.0.0.1	\N	\N	Successful login	2025-07-24 23:48:37.178671+00	low
1356d8bc-20fe-4233-bcdc-7fec72d949a0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-24 23:52:15.168521+00	low
c1968b9a-1af4-42a7-99b8-276b686447bf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 08:13:27.108825+00	low
f93ce6f0-71f9-4ccd-9aa1-4eefb00caeaf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-25 13:55:59.528767+00	low
393f9009-5aad-42ac-9631-2d3398fb4643	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 13:56:10.614859+00	low
fd93b05f-477d-4138-877e-e8a3f7ee0db9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 13:56:27.888954+00	low
11849a47-bc0a-43ab-b202-6d618557ccf5	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 15:54:59.224931+00	low
26c4f590-e2df-45f2-bb47-16c93dd87065	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 15:55:20.062768+00	low
8e7a8366-625c-4b78-8c06-595cb9861615	\N	login_failed	172.18.0.1	\N	\N	Login attempt for non-existent user: superadminuser	2025-07-25 15:57:38.872673+00	low
008fd4ba-53f1-47d2-ac05-1b1bc285be50	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 15:58:19.668651+00	low
5d82281c-9630-4f9f-95a0-a5ebecdb87c5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 15:58:36.808395+00	low
01ed78b3-c349-4942-b91e-fa79c889a836	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 16:02:44.225379+00	low
53857498-e647-4159-81f2-fc987b3299e7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 16:35:35.269443+00	low
fd061565-ba14-4ecb-bd67-61ff8c36417d	\N	login_failed	172.18.0.1	\N	\N	Login attempt for non-existent user: admin@oraseas.com	2025-07-25 17:42:21.486622+00	low
966c21e6-e80f-4807-815d-003cb18c15bf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:43:25.812689+00	low
485d7bca-4b48-4f60-a91a-d7d1e39dae79	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:44:16.94286+00	low
928799f6-0339-48d0-b047-ff8f6ba0ab48	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:45:58.011022+00	low
c502ce9f-c5de-445c-9c43-92f1a9207995	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:47:01.759183+00	low
50c06eeb-75bd-4cc6-80d7-0e8116c92a08	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:48:19.558446+00	low
182e772d-3906-4d72-82c3-072016cb191a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:50:16.259131+00	low
f611d6b0-1a83-494a-839b-183c76774d2f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:53:33.749129+00	low
76653947-d2d3-4066-94df-562b839c3dd1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-25 17:58:30.56755+00	low
c468d67b-c469-42a9-b396-141798b103ed	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 08:11:41.185091+00	low
ee109ac1-8ce2-4227-80cb-385adc389fd6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-28 08:16:38.348178+00	low
49cb8a40-89f0-4c91-94c2-8c86016e2992	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 08:17:15.830253+00	low
409a2799-8ad4-4378-b824-5f98a4c3a7a8	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-28 08:18:00.881205+00	low
45b8e7fa-f9df-4da2-abcc-13662f3a49a4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-28 08:18:27.164578+00	low
39b145c9-aa7a-408e-8c6b-962f422864a3	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 08:18:47.329214+00	low
e02991ce-595b-4e47-be27-897a91e93630	c1ddd000-0d1d-1e23-4567-890123456789	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-28 08:19:24.595394+00	low
a4d5c3fd-08f8-4bbd-8f39-5b54b4b81e70	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 08:20:27.726456+00	low
23dd0229-9e45-43e8-ba04-f72a6e50c71e	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 08:57:14.758599+00	low
491e6923-21c8-401b-8858-d172604da783	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 09:20:25.607573+00	low
6f72c6ec-8477-4462-940d-62b90a385d8a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 13:15:39.31038+00	low
2863c1bd-4571-4ef3-abc2-a39b499caf1d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-28 13:26:00.760622+00	low
d9b89feb-caf1-48e2-94a6-c50fd79a1290	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-28 13:26:28.620017+00	low
344a780e-dc0e-4dc0-b846-24d4356d0584	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-28 13:27:03.066073+00	low
bc459ca8-33ce-48cf-a3a6-165f5eea0e2d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-28 13:34:55.912858+00	low
3e935db4-b129-4130-82aa-825b85da6919	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-28 13:35:25.644051+00	low
3216a4e4-8cc1-45a1-9f75-f620eaf20885	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:15:49.320348+00	low
5b17ccc7-f0b5-4f86-aca9-33c6d0620b8c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:20:44.997702+00	low
252cc595-1003-4c0f-b514-b42c77a78043	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:22:39.092121+00	low
4267bea2-539d-45f0-a75d-a310fac4a1e0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:22:56.51547+00	low
1103944e-a8a0-4b68-b1ff-3281c2b22feb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:28:19.375544+00	low
e7b6ef66-7c54-42a3-90d3-79d65c1b76c3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:51:31.881018+00	low
fc5bd2c8-cfb8-4dec-9d16-a82801d0ce7f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:51:55.285449+00	low
3e26408b-f01e-4fcf-8b5e-b8be545e69f4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:53:10.832781+00	low
56d05729-b163-40cf-a8d4-97b23b0e4309	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 14:56:09.465716+00	low
263636f6-6284-4baf-b03f-4b223b85f4e8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 15:07:29.254512+00	low
53b7b783-5816-4866-b257-cdcc5742c330	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 15:25:34.880974+00	low
b33364a2-bc74-44ed-9c0f-c189d7419925	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 15:26:10.913927+00	low
656cfdb2-ac3a-4ecb-a974-72751f47b808	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-28 16:14:24.069988+00	low
94c8bed0-44dd-407d-b1ba-380379059143	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 17:20:24.270378+00	low
a94a8ef7-7c8d-480f-b59e-1705bc799ce7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:14:36.49536+00	low
f0c7d06b-c41d-4137-9445-0c5fc5657b8e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:18:05.400154+00	low
60cc0740-a0ea-4767-a6c2-b02d6626fcf1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:18:14.854144+00	low
61c1a14d-332d-4e26-8328-a0a75b607cd3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:21:43.343906+00	low
e019ad13-5692-44e0-a395-28c960b82677	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:24:57.31722+00	low
3fce3c43-7907-4cf7-b8ef-19c569096edb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:25:22.788665+00	low
3803b29c-1329-4e16-949d-31fd476c0dd4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:25:33.595167+00	low
c5bfa316-f67d-4458-90fa-2f54245570ed	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:26:50.750902+00	low
8d9e13a8-e680-4824-94b1-8b02cde7b35c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:27:00.663584+00	low
8c75492f-22cd-4559-969e-25b73c883f6d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:27:13.790693+00	low
3ecef59f-3de7-4559-98a6-f5602c4f4a39	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:27:29.949827+00	low
6aec90fa-1d09-4b9d-ae86-bc33cf2aca86	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:27:42.643354+00	low
b32cfe82-44a4-44d4-aec1-15101c3755c1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:28:27.25585+00	low
9173875f-8710-486c-91e9-5530c6cba42f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:29:27.900023+00	low
2e20fd71-4a26-42d4-aa45-587ed76dbca7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:29:49.985591+00	low
62b3c3c3-c98e-489b-94bb-df6a69da6419	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:30:20.42589+00	low
b2ebb6cb-a580-4954-8e27-9910472c6796	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:31:01.53541+00	low
e3b503dc-7161-49db-a248-62fca2a4f1c4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:31:29.034903+00	low
0322a4e6-7055-485a-a760-af73aa967907	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:33:47.658237+00	low
bc332708-ad6a-43d2-9933-751a731f785f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:34:15.391257+00	low
2e12927e-4506-414f-8800-589fda857b2f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:34:40.497647+00	low
0e9a2e7b-576c-4ceb-87ae-e14835cb99f1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:35:04.260362+00	low
18d7dd4b-7167-4ef8-bf4d-7c456a33636c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:35:26.662772+00	low
0afa58ff-8553-43bd-ad0a-a3f47a4a3c33	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:35:48.469795+00	low
3acf5c47-d95c-4d3d-b337-dd0c515c7cb0	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-29 22:36:00.937619+00	low
11f025ef-1cee-4b86-b4ee-a9ddf2cd77d6	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:36:47.176083+00	low
5006b00f-27ed-4ed7-b603-2757b9a91a90	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:37:10.113864+00	low
c9cb877d-b918-4b5c-b2d4-8ca3ac6e8be2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-29 22:42:46.913923+00	low
af655d6c-a877-43dd-964d-5f25ae1b47e8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 09:14:49.688187+00	low
3fb31a45-2158-4545-ba21-ea182b19d328	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 10:08:28.501393+00	low
8eec6afc-7052-477f-bf0e-c02f76bc75ec	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 10:12:24.51598+00	low
ce6eff12-8ae5-4520-928b-57711b97404e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	172.18.0.1	\N	\N	Invalid password	2025-07-30 14:48:31.677445+00	low
09c4b1df-fed3-4054-9ac2-8c02d0609cb8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 14:49:34.515162+00	low
7649202d-d37c-44dd-a0db-5b9c83619423	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 15:00:14.824579+00	low
3356f08c-e789-4e87-a832-3c20075e8e50	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 15:01:30.145097+00	low
9613ca56-c7cb-46fd-81c1-60dc1e7cb76d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 15:50:00.612818+00	low
9f4308c8-2379-4958-8f9a-4b0443fc4267	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 15:50:40.717187+00	low
727d5797-6adc-4f67-873e-667b6f53f966	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 15:56:33.483784+00	low
90abb6fa-580d-4a9c-a2e9-549ead41d0fc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:42:01.276222+00	low
6c08be08-c012-4351-8fe0-cc8b51920acc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:48:07.605341+00	low
3ef5088b-a888-489d-9bb5-b619f63a5f44	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:49:03.849617+00	low
3490f2ec-8c86-4f59-bd45-e3a9d206446f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:49:19.312485+00	low
0656b2a9-8b64-4f98-a06e-b325cef9db61	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:50:16.844074+00	low
c424a143-befb-42d7-857b-7d6594182291	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:50:52.250597+00	low
a8741cbb-2e24-473c-80b7-2a088678c936	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-30 16:50:52.485012+00	low
250efbf1-1efc-40cc-8da3-141f51299456	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:55:42.77435+00	low
1aea2ecb-ff29-4195-83cf-6697ee1f1bfb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:55:43.123082+00	low
48700ab3-e105-42bb-b36c-044581f51b1b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:55:43.486876+00	low
c5a2e069-6f2e-4db6-9e4e-816937ae2518	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 16:55:43.866036+00	low
5faefabf-0171-4a96-9b36-27e5b8117531	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:03:16.95278+00	low
aaad0c07-cdee-4026-826f-7d38ccac2bb8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:03:32.396377+00	low
3e221bdb-eacf-4b49-86ee-ebd2ec69567b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:03:57.770281+00	low
ed4670af-a318-4be4-9e34-1a581a5c669f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:05:00.899947+00	low
5bd3ef09-13f1-4048-827b-badaeaa82f0f	d13e1a2f-c773-4d6c-ba6d-243238c7a563	login_failed	127.0.0.1	\N	\N	Invalid password	2025-07-30 17:05:22.117437+00	low
faf068d1-4d2e-430c-8d85-5c3ca98e94da	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:05:22.463196+00	low
47e137bc-7861-4c57-a98b-b085d5cce7f3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:06:34.958603+00	low
308a1431-10ab-4455-83f0-1bc400d27307	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:07:08.02315+00	low
7ad5614b-71e3-4dd8-901d-e8de3ad532db	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:11:29.096016+00	low
3d9fe63e-81ab-41ac-a237-b10f66c49fde	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:11:36.614307+00	low
727486f8-de4a-40b4-9e77-fe911a9b43ce	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:22:59.960004+00	low
48c87274-5ee2-45ca-8038-434d8df2880b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:23:22.839918+00	low
ea084c94-8b53-4602-92d8-2601fe5f385e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:27:49.787431+00	low
14ee125c-16d5-45bb-a529-59c2314eb29f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:27:57.804792+00	low
f2b6078c-ba13-4746-a62c-14ec09b92443	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:29:02.967111+00	low
ea9ddf69-0900-45ba-b6fb-42ce6514ee86	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:29:10.668539+00	low
1d1e0791-6d0b-4b76-8f3a-b0b3df591abd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:30:30.679429+00	low
21dff1b3-6845-4ab7-9819-a54a387e3a10	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:31:24.346766+00	low
bacdd1c8-62aa-455f-94a3-4e7ebb673244	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 17:33:57.523385+00	low
4784ed8c-f0cf-43df-a27e-32830e4dd256	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:40:55.298236+00	low
67e2e95a-9ca8-4131-820a-fdcf6761a1c3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:41:41.831016+00	low
26c08969-e767-4830-9a42-2f66ca5edde7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:41:59.835292+00	low
c2fe73e5-eca3-438e-893a-4e3c403cac02	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:42:11.054741+00	low
6ec6ab9f-4942-481f-85bf-30ed80487af1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:42:22.402443+00	low
bdfbe6ff-430f-4a5a-bef6-e32620ab7f48	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:43:06.281177+00	low
24d741f6-71bc-49c7-805d-73e628f8f640	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:43:51.414368+00	low
72b978d7-72c1-4750-803a-be44ef101b37	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:45:18.942126+00	low
ce92a800-d20f-4e98-a7d4-91d5efcf4339	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:45:51.957981+00	low
7476de2a-4fd6-4fc8-869c-73114bb779b2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:46:25.078431+00	low
2aefca5a-b4a4-42cc-a420-c9108bac4995	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-30 17:47:15.311689+00	low
7972ba1d-912a-430b-a7c5-93ebeb60ee4c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:01:16.328008+00	low
a1992229-67c7-4e5d-be16-be165dc3eeda	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:01:16.940756+00	low
0671827c-318a-4a30-a96e-323d61802324	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:01:17.490873+00	low
f5daf6b8-e952-4628-8768-f67654acceb9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:02:27.053165+00	low
9f8327a3-b53f-4324-a0a1-3960bf82cea6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:02:27.731537+00	low
ebf77d54-111c-472a-bc76-cb7b578a0f50	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:02:28.313767+00	low
1f280bcd-5628-465e-9907-d0f08632e08a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:03:10.404884+00	low
c71f3580-ad21-42b3-87b3-8b5c5fa8ab46	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:03:10.932003+00	low
8aca523e-e878-4c7b-bf46-176ff24b76ff	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:03:11.338553+00	low
9d439f12-a9ec-4863-b1d6-0d40d414c8b1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:04:47.252255+00	low
e1e38f6f-98dc-4748-94c5-3aa6c76c3be9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:04:47.865463+00	low
84b65b8a-9eee-4691-8b7a-ffad6dff1993	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:04:48.515377+00	low
beb7fb05-2d54-4ab6-951e-0e8eab9600ae	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:05:09.712686+00	low
873326f0-6268-44ee-aea1-3b2a74e9b90b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:07:15.434092+00	low
20a1e8d7-851b-4847-96cf-0869c5fc9ddf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:07:15.80154+00	low
78f9087b-fec8-4e68-b0e2-f49ed6dd527f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:07:16.254684+00	low
fa6eea3d-790d-4aa3-a3f2-acc9d621dc4c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:13:04.099126+00	low
e029dacd-72ef-43d5-95f4-02625f989968	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:14:54.766881+00	low
97d5f841-54da-4d22-bacf-8e2353899b15	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:21:25.814527+00	low
9d39a166-6484-4a51-89f8-a0c8dfc12f25	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 18:23:19.076219+00	low
27e803e9-8741-4c66-978f-7cc63daffd92	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 21:21:40.278476+00	low
5e55cb73-d397-49f1-8cd0-3db99dda0836	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 21:22:15.652102+00	low
a4bcd11e-8d17-49b2-ba6e-d3904b917b09	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 21:45:06.715459+00	low
c6017a65-f558-4bcd-9165-087edd65959c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 21:53:36.351344+00	low
e3a04d11-8aa8-4536-aa26-f6834395938a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 21:56:33.87009+00	low
6995cb38-45d2-4e97-8e82-e437c132eb4c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 21:57:56.215234+00	low
1eecc6b2-9c47-4b55-8ead-fa4c9cbb92ef	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 22:10:59.588646+00	low
f5c1601f-dfd1-4174-9f7f-692b8ec32303	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 22:17:27.513+00	low
2149878d-0025-4189-95fb-98e759be6aeb	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 22:21:21.42212+00	low
ebb5f1ce-96c2-4cdf-92c4-15a30353074b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 22:46:22.983122+00	low
1f133152-41fd-4156-ba06-56461731f440	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 22:47:22.736003+00	low
29e6fe98-234d-4d25-bef3-b8ea4cc6a68e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 22:53:50.744433+00	low
5be25d95-6cbc-4650-8bbb-6d6d132fab04	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 23:12:17.304859+00	low
5f8cc679-e361-441d-9935-9d58c58ae221	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 23:43:14.471008+00	low
f0dee735-a432-4fda-b0fe-f999a0308798	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-30 23:46:02.777022+00	low
439fd114-77fc-4f80-aeec-069c04ec8dfb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 08:23:58.823991+00	low
3cf8a582-280a-456d-b172-6d74f713e666	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 08:26:26.608739+00	low
df766fa4-94df-428f-9787-92a4021c151e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 08:27:36.454055+00	low
2d9129c8-6ad7-4b23-a429-8a7b62d6a02f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 08:28:15.617259+00	low
4830acf4-a869-4157-90cd-072247573565	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 08:28:35.848556+00	low
5b10e6ce-e803-4a20-b37e-ea4279b7e6e9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 09:57:58.404681+00	low
277c3894-c4f7-4229-a619-783cd7d7e224	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 10:07:15.511823+00	low
71f177de-eda4-48e8-8ddc-013381ac1e11	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 10:32:17.888496+00	low
5ef52ba3-d2f1-493f-86b1-9803795374ec	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 10:35:39.611282+00	low
a0574111-a2d8-4769-8677-a187b3def416	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 10:36:05.209066+00	low
ed769e69-52da-4339-b62f-51c3682270c4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 10:37:12.905894+00	low
471d8bb2-3a9a-4dd9-b355-58510add8a1a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 10:38:34.28753+00	low
e6037d47-89ac-4634-a947-9581fdf79ea4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 10:45:22.91214+00	low
f9ca5b9f-c22e-43fb-9a55-7894e9f327fa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 11:21:53.734621+00	low
b1cb16b7-6666-4e77-92f5-5c6a2c503599	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 11:24:15.451289+00	low
d8ab903a-ea9d-405a-9fa0-e3c015e19994	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:08.270433+00	low
8682b734-a697-4968-9087-6652d4b69dba	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:08.556405+00	low
d0c1e5ed-a9d8-49e1-8506-1ff2e9936ceb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:08.781766+00	low
26379791-2ffe-4b3c-9ca9-81da0d94791d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:09.057509+00	low
7c82aa06-7be5-44c4-a1e7-02bfd2ab02ae	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:09.3277+00	low
2f357c15-28f7-436e-8304-66856e7b6e7e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:09.568037+00	low
472d35ca-82a2-4ad9-9b35-92a3e67f3c16	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:46:09.78934+00	low
91df925b-38e2-4410-8228-ddd92409c244	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 11:50:40.068982+00	low
99702d73-8fad-4744-9349-cb8543cfd0bd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 11:51:22.336737+00	low
40b83239-bc03-42c9-94b5-80d41a9af1d5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 11:51:31.869372+00	low
7bea3ffb-3f3e-4a7c-ae39-a19b04503a13	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 11:52:32.334262+00	low
682d7bf8-24a7-4055-9e19-fc4cd09d88fc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:38.925089+00	low
c017817b-9511-4f4a-af05-9e711112edd0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:39.154993+00	low
e9a47ed5-2a9a-48d3-910b-bd23cdf84eb8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:39.384093+00	low
3864e767-00d9-4595-9219-bd207813b776	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:39.663218+00	low
a329cc6f-11d5-4e9d-afc8-583360fdb78a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:39.906901+00	low
4a9815af-4267-40c7-94b6-02a4387f9ca7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:40.144789+00	low
8bb02dec-c32b-40b6-826f-b78d85a5990e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 11:52:40.38027+00	low
92263283-0a23-4fd9-9f59-249bdaddd870	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 13:23:29.989044+00	low
9496fdb6-2fe6-4d84-b30b-bc5b8f298dcc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 13:24:24.095599+00	low
0f082183-95f6-4ac6-8260-4e3de6740178	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 13:25:59.457097+00	low
626587f7-f4b5-49c4-a5cc-53789e64a97a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 13:30:21.457853+00	low
5da81a4a-7248-4584-a587-52dbdbc0c45d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 13:31:28.88716+00	low
5215a7b0-0d7a-4353-b0c9-582db29fd36b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 13:32:23.337523+00	low
e27e5f67-59e0-46ff-a9a4-bd0aa5585924	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 13:32:46.193699+00	low
bd255969-2c1b-40d2-a8fa-38a17f85311f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 13:33:40.873908+00	low
76e01f99-a4f4-4eb4-8cde-40964861a4b8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 15:04:40.873397+00	low
6260031c-9505-4265-b708-66ecbb252871	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 15:05:51.902655+00	low
6b3fcd63-8d60-4274-8dc8-5da030d1f2a8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 15:06:25.271888+00	low
dd85af4f-6c74-49f1-a06b-cf3e6336f4b3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 15:08:42.670935+00	low
c8daa466-60d0-429c-8101-c46d0046cfcc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 15:13:51.272558+00	low
5e537a5d-3014-4223-8d41-d387d929b765	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 15:16:59.404928+00	low
c76dc15a-bd37-4455-94a7-bafbfbe849fa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 15:27:13.562809+00	low
b736a6fe-1b9a-45a0-95d8-61433670e152	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 15:40:38.472195+00	low
48041a99-f6b0-4f6e-b608-dca0c9d1e60f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 15:47:01.561827+00	low
db6ba756-a917-4901-9f25-cd383f363027	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:00:22.439743+00	low
e366350d-3c18-4677-9340-ef618d17e8b4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:00:47.546548+00	low
527d96ac-aac0-42eb-aa6a-219b8643f4a2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:01:54.416925+00	low
eb2e7e6d-7a16-42b4-9970-634635781944	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:03:13.676688+00	low
d092cf32-2d80-4252-8e92-ba538a25f441	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:05:34.087183+00	low
e4ee788c-66b6-459f-909b-7d3bdae28344	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:14:24.588756+00	low
29a4e259-5e27-43bc-8e9d-caf9d49ed0f4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:18:12.287807+00	low
042fbaf1-717c-40ea-9892-13502f7dcb1e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:19:49.187531+00	low
981b1cb1-6ac2-46bb-9ad3-a8ac5197ad0b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:21:26.503316+00	low
bd7203ac-e6c6-4bc9-bba3-d223116225bf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:34:06.710295+00	low
ae187acd-6157-42c5-b734-9f684b590014	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 16:40:23.634216+00	low
616f0062-efcc-4140-b7e7-816de5a980ef	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	127.0.0.1	\N	\N	Successful login	2025-07-31 16:46:24.442189+00	low
acd38be7-8046-4d44-a3ac-43d1a6e75bbb	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 17:03:21.881413+00	low
29dd9f16-ba50-4340-be99-464ebf35fe55	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-07-31 17:03:56.078118+00	low
9276b007-586f-43cb-99a5-33496541e43a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-03 21:58:37.049709+00	low
1e3ab075-72e9-4b06-ac32-2b22580835f0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-03 22:12:17.059628+00	low
4f93b6cc-cdd7-4f25-a3f2-812b445caf46	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-03 22:12:25.073581+00	low
a2c70453-202c-4c4e-a5be-2619e040aaf6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-03 22:45:01.223655+00	low
e4e784f8-75c7-43a0-9bb2-164d198442c6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 09:49:19.489657+00	low
186cf398-041a-46d7-985b-5bec002739e4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:24:20.401865+00	low
95488a96-a1a8-436c-8dd5-66a05dae59d2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:26:19.44472+00	low
03d9416b-f544-4929-9a67-003220549e64	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:27:37.108011+00	low
da282519-4fe7-4f3e-a94a-dd3cbfce8aa4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:28:12.078476+00	low
9e376500-853c-4061-9cf4-47e7ed37e420	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:28:22.011737+00	low
94ff8110-89ec-4529-814a-1f60e9472145	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:30:46.672749+00	low
47bdc64f-b24f-4582-9732-4a8f84681b83	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:35:24.797741+00	low
1352048e-cdcd-4e68-afcc-7500475c354b	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:36:01.495259+00	low
df28562d-f689-45d0-b239-b158db949ee1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:50:33.710398+00	low
130afcfd-569d-4432-8382-cc3baac10c54	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:50:49.505055+00	low
3a7354f2-e9be-423a-b06f-55b696227d3a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:51:08.823341+00	low
e037c496-304a-40ba-b63e-d15178558648	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:58:44.033139+00	low
0adf6ecc-b016-42c6-ba7a-131d8a7d5705	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 22:58:53.199073+00	low
8f8926bf-60f2-41d9-bb28-98802a595e8d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:05:11.379245+00	low
5234a0cd-6bea-4845-bf9b-85cb593b2ac7	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:05:39.856697+00	low
f576deaf-cc7d-44d2-acdc-15cf634a3c56	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:07:02.472104+00	low
4bae84f0-6005-4d15-a7e1-f2bf3c1d241a	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:07:23.439046+00	low
50bec898-ebe1-4720-9f07-00824d01b578	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:11:07.560847+00	low
165a73bb-c02c-4571-a617-254215431ee1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:13:45.905912+00	low
06e82514-21c9-49d4-8d37-3ceaa9704b58	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:15:33.438815+00	low
155e9d8b-ae6b-4c65-af4b-101e1242b467	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:17:07.268303+00	low
0ffd30e8-439e-43a1-b504-4fcbad035a17	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:17:33.510165+00	low
b3881385-157e-4308-a021-4bd46fb58457	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:17:51.505921+00	low
f34dc7f8-4765-40b3-be8b-296f513f01b9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:18:38.125332+00	low
f1be60f6-d5ef-4f88-9eb8-ad22e4dabba8	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:19:21.466537+00	low
9eac63b1-6781-49cc-a2e3-70afe47251fd	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:20:08.239387+00	low
e3c628c9-8f8c-4914-886d-bcfcaf50f725	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:20:28.794008+00	low
17777455-1b9b-4974-9fdd-9e5dcafc6aed	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-05 23:32:23.086032+00	low
d120b83c-98fc-4051-9746-5a1400603f4d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 12:47:51.911803+00	low
dded9860-8b7b-4fc1-b499-6e40de214b01	f5abc444-4a5b-5e6f-7a8b-9c0123456789	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 12:48:06.380537+00	low
b9fa542c-57bf-4d31-8dc4-69e96814028f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 12:49:42.580136+00	low
0aef6f77-25f7-4af4-a7ae-bad19e912719	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 13:04:09.816772+00	low
5fb0c48b-4e19-4c9f-bae7-f37647213e9b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 13:07:55.468815+00	low
b89efaa1-a701-4ae2-918d-179db363c1b4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 13:17:22.004881+00	low
f4fa3ac8-ae4a-4099-88db-6d0ad82f4c3b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-06 13:23:53.801682+00	low
7b52fe74-b21a-4180-8c32-694fc810f92a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-07 13:05:49.467195+00	low
ea33a335-54c3-4da0-8fa0-c93e846250c2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-19 11:37:21.954013+00	low
0d61421a-4568-4dca-bf50-89ca320f1132	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-23 14:57:32.707887+00	low
883b176b-1d77-459e-80ed-64eb4ce6c58b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-24 11:46:44.413126+00	low
4606010a-5799-45bc-bbb5-6d171297be5d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-08-29 16:23:00.383451+00	low
f38f1ff3-404d-4aca-90f9-201a1d8292ca	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	172.18.0.1	\N	\N	Successful login	2025-09-06 15:13:22.49084+00	low
83a638b3-07f5-4a1e-ade2-0465050a8223	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-10 22:00:54.593635+00	low
fe14e95d-7263-4ed7-9d44-bc5e25af1368	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-10 23:32:49.217267+00	low
54d75b8e-7a34-4554-89dc-d96f4d7f0349	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-10 23:33:33.837317+00	low
1b1b21d9-cee3-4b0b-90ab-aea43ea228fc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-11 13:06:57.917641+00	low
4100bf00-8ca2-41e2-9511-46e2d22af0f1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	password_changed	\N	\N	\N	Password changed, 0 other sessions terminated	2025-09-11 13:09:21.909125+00	low
f257faa0-0766-42a3-8cc2-2768e10209ae	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-11 13:10:21.342444+00	low
8286853a-af47-497c-a004-279d7f36553b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-11 14:15:26.793599+00	low
8db589f1-3af2-405f-b4b6-aaa019dcaef1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-11 14:16:44.200587+00	low
d0a36e4d-10e8-4743-8bf6-43d85db26dd8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-11 17:15:47.196826+00	low
eb7fd628-ce7c-47c4-96e2-334f8d1fa68f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-11 17:19:46.862996+00	low
4c0c5b5d-7b35-48fc-8e7b-a7528336e7da	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	94.66.244.130	\N	\N	Successful login	2025-09-11 17:26:48.599292+00	low
8360f45a-9194-4b3f-bf24-20eaa8e3d7fd	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	94.66.244.130	\N	\N	Successful login	2025-09-11 17:44:09.349958+00	low
835dcc84-1276-41dc-9d05-f78f13ac9c0e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	87.58.94.209	\N	\N	Invalid password	2025-09-12 10:05:32.066425+00	low
04199634-d08b-4ca8-af39-27ac9fc889fe	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-12 10:06:00.948344+00	low
99c45e9a-cb8b-43f5-ad18-01cbc909b43d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-12 17:08:20.169459+00	low
b1712d18-26ee-4ecd-96ea-830542dfcb93	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	94.66.244.130	\N	\N	Successful login	2025-09-12 18:32:11.503127+00	low
794ce8ff-0493-43a6-8abe-b449a8df57f7	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	31.152.66.217	\N	\N	Successful login	2025-09-15 09:11:00.66486+00	low
ee4d8bf8-c671-4df1-815d-2c8d49763ade	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	31.152.66.217	\N	\N	Successful login	2025-09-15 10:14:52.078559+00	low
731a15be-33f0-4208-b840-fe003bd2b379	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-15 13:36:05.292038+00	low
0770bf9a-c265-4d41-bac4-8a95472047ad	4db3f5bf-0946-43c0-979b-7ac671e0fbb9	login_success	87.58.94.209	\N	\N	Successful login	2025-09-15 13:38:11.610705+00	low
cef8b74f-a90e-4d67-818c-0202b3580b31	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-15 13:38:38.281247+00	low
47e0b882-27eb-430a-b405-a2f179475ef2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.209	\N	\N	Successful login	2025-09-15 15:47:24.244446+00	low
d5364c93-d4e6-4557-9471-043ea0122e90	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-15 22:06:36.851273+00	low
e8b5451c-4ce2-47b7-8f8b-b3e401772674	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-15 23:58:36.199197+00	low
1604d08d-d602-47f8-8487-d80d42152e7c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	176.79.222.12	\N	\N	Invalid password	2025-09-16 00:02:22.587506+00	low
1a55bf13-0593-4c59-8638-8b2b91ec814c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-16 00:03:21.355448+00	low
96e21404-ae66-4376-a903-a4f3c111c170	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_failed	176.79.222.12	\N	\N	Invalid password	2025-09-16 00:03:42.371997+00	low
8db96a9d-fa2f-4e6e-a7a9-7599288e21ee	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-16 00:03:55.527925+00	low
ec5a49ad-5596-402e-84b2-0f25f0e00fca	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	31.152.66.217	\N	\N	Successful login	2025-09-17 11:24:25.285236+00	low
c9801333-9eec-4e21-a761-de2534338323	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	31.152.66.217	\N	\N	Successful login	2025-09-19 12:10:14.146738+00	low
d8dc28af-d7f4-44dc-bb27-00ec162ad059	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	94.66.240.156	\N	\N	Successful login	2025-09-20 08:00:41.794896+00	low
af559a54-e0e2-42b2-a5f4-b8e5c03e105c	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	185.16.164.65	\N	\N	Successful login	2025-09-22 04:37:32.074209+00	low
8df25f0d-7bf4-40f5-a47f-db37a1d82471	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-22 21:10:12.781497+00	low
b189c7d2-c13c-4ce6-97c0-51867f343784	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-23 10:48:30.930689+00	low
d14dfeaa-2110-49fb-b3da-2e3b68e9b384	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.213	\N	\N	Successful login	2025-09-23 15:11:54.877909+00	low
5277edda-e9cf-469f-ad84-e3eae8a747db	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.213	\N	\N	Successful login	2025-09-23 15:17:47.483594+00	low
f26005e3-5ded-4680-ab38-30ee3f544f3a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.213	\N	\N	Successful login	2025-09-23 15:18:01.411459+00	low
1dcef3ad-90ca-4ba7-ae44-77ed0733e783	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.213	\N	\N	Successful login	2025-09-24 15:05:53.935138+00	low
ba5d4e06-279e-4d96-8c5c-5b5c2d527cd0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.213	\N	\N	Successful login	2025-09-24 15:10:39.085028+00	low
e8be5c0c-bd55-4282-93df-d9ebb81a6909	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.213	\N	\N	Successful login	2025-09-24 15:11:01.729488+00	low
286369ef-9f6a-493d-a73e-c39e4bb14cd7	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	94.66.245.246	\N	\N	Successful login	2025-09-28 20:56:55.978683+00	low
48423626-fd42-43e3-8a81-ba643e84e219	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.233.94	\N	\N	Successful login	2025-09-29 09:57:29.994827+00	low
a6d63ffa-9c96-4b13-ab1d-0a290795120e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-09-29 11:35:30.741771+00	low
ef82e0ae-fd14-4854-b210-3ff06517f893	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.219	\N	\N	Successful login	2025-09-29 17:13:15.498572+00	low
5d3b8eca-044b-4a17-b311-3a75d0ecdfbb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.219	\N	\N	Successful login	2025-09-29 17:18:17.395404+00	low
52a144a2-613e-48ad-a03c-187bc62aa3f0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.219	\N	\N	Successful login	2025-09-29 17:21:50.006726+00	low
c6961939-1308-4365-b403-40c22f39a89b	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	94.66.245.246	\N	\N	Successful login	2025-09-30 20:30:48.463012+00	low
159a7f80-fc03-4d15-9019-ed3ec15b4c04	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	79.131.185.227	\N	\N	Successful login	2025-10-01 10:36:52.739619+00	low
6e162b85-6b18-4a58-8891-dac5de1169bd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-10-02 14:17:29.059243+00	low
92915e16-7599-484b-88c7-e84134317ab5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	87.58.94.219	\N	\N	Successful login	2025-10-02 16:31:33.453487+00	low
1a77b011-f331-4a5d-8089-e425a9a57a1e	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.53.227	\N	\N	Successful login	2025-10-09 09:48:01.008689+00	low
7eca2fd0-9e9f-49a8-8bc1-4b932c3f6e71	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	109.178.53.227	\N	\N	Successful login	2025-10-09 09:49:54.327633+00	low
36c94e00-f812-4075-bcde-67af85044e58	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.53.227	\N	\N	Successful login	2025-10-09 10:06:55.326991+00	low
8dd01d90-a728-4a84-ba68-43919ae8ca0a	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.25.139	\N	\N	Successful login	2025-10-20 11:14:38.041437+00	low
ac396492-2596-4987-84c9-943c9974b62e	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	109.178.25.139	\N	\N	Successful login	2025-10-20 11:15:12.140292+00	low
53d474c2-797d-4726-bee7-c4bfb484dd34	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.25.139	\N	\N	Successful login	2025-10-20 11:17:38.399438+00	low
3e2dba79-0964-445d-a95b-aee7d5462ab3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-10-21 00:00:46.718825+00	low
50912ea3-4532-405b-82a7-50ad3d47b546	c1ddd000-0d1d-1e23-4567-890123456789	login_success	176.79.222.12	\N	\N	Successful login	2025-10-21 00:02:00.518971+00	low
0700e4fb-33ed-4115-b40c-97cad60284bb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-10-21 00:03:49.354698+00	low
8beda416-9596-45e3-99a5-6ac1ffa18f05	\N	login_failed	109.178.25.139	\N	\N	Login attempt for non-existent user: Zissis	2025-10-21 10:04:26.614142+00	low
c56c7939-a3c7-4134-9fb6-88a622651cb3	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	109.178.25.139	\N	\N	Successful login	2025-10-21 10:04:34.68802+00	low
1b4b8e56-3338-4955-a845-a05f6ce053d8	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	109.178.25.139	\N	\N	Successful login	2025-10-21 10:10:19.408025+00	low
a0c2b4f1-7f46-4f74-abd0-b29927cf1d2e	c1ddd000-0d1d-1e23-4567-890123456789	login_success	46.50.3.68	\N	\N	Successful login	2025-10-21 16:43:02.57539+00	low
2ee7b2c3-0106-4b47-a540-005842ed01f2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	46.50.3.68	\N	\N	Successful login	2025-10-21 16:44:54.690431+00	low
91fa8d78-5953-462a-97c2-34fb1d99b7d9	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	2.87.187.224	\N	\N	Successful login	2025-10-21 16:54:12.736499+00	low
3ebc91c6-72d5-4cc4-af8e-1a583d3caaa2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	46.50.3.68	\N	\N	Successful login	2025-10-21 17:19:52.39661+00	low
9424c611-2691-40a0-94a1-9e0dd1032ad1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-10-21 23:18:33.540969+00	low
07f36b3a-a3ec-4958-bf4e-88132789eb5e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	login_success	176.79.222.12	\N	\N	Successful login	2025-10-21 23:28:48.561699+00	low
8f441400-1481-4a26-abbd-b05cd56568bf	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.25.139	\N	\N	Successful login	2025-10-22 07:28:12.208184+00	low
bdd9c6fe-a62d-4b2a-bcc6-27c5b29c1587	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	2.87.187.224	\N	\N	Successful login	2025-10-22 15:29:43.106899+00	low
e1e08502-44e5-4cf3-b673-d32f4ac04f4e	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	2.87.187.224	\N	\N	Successful login	2025-10-22 15:48:48.275431+00	low
492d88ac-a425-4075-9a3e-dcf75849da99	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	2.87.187.224	\N	\N	Successful login	2025-10-22 15:51:28.927535+00	low
51aa5ebc-93b6-42e6-9d80-088628f70159	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	94.66.251.74	\N	\N	Successful login	2025-10-24 11:28:25.470423+00	low
56f3dbfb-79eb-473d-bd2e-c8ba989480dc	c068d54f-9f9c-4735-a4e1-ef3ecd0c2510	login_success	94.66.251.74	\N	\N	Successful login	2025-10-24 11:41:04.542988+00	low
eec42382-0a10-4207-a373-03cd5354c85a	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	2.87.154.6	\N	\N	Successful login	2025-11-02 14:53:42.149257+00	low
93addcca-7a6e-448f-94c5-38aacb366ee2	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	2.87.154.6	\N	\N	Successful login	2025-11-02 14:54:14.113364+00	low
c0c376ff-a247-40a1-9110-23068f8a0a03	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	2.87.154.6	\N	\N	Successful login	2025-11-05 19:57:20.057441+00	low
8a594123-16d6-4d48-ae83-ad6f0ec85e07	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	2.87.154.6	\N	\N	Successful login	2025-11-06 07:48:57.730176+00	low
dbf99649-aed0-4a96-8b3b-74babf16a3f4	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	79.131.186.241	\N	\N	Successful login	2025-11-08 17:55:22.055901+00	low
36ef3e62-e842-4d95-9c8b-3c3bbe00debd	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.153.193	\N	\N	Successful login	2025-11-10 06:57:07.877119+00	low
e2b41f6c-3e38-48a3-bbcf-83d02b2c365e	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.153.193	\N	\N	Successful login	2025-11-10 13:48:04.559527+00	low
9251efe5-2e60-4a4f-8f99-1be9531e191c	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.153.193	\N	\N	Successful login	2025-11-12 11:57:31.65173+00	low
2bbc53cf-92cf-4707-a2e1-cb20ee054c56	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	109.178.153.193	\N	\N	Successful login	2025-11-12 12:02:39.8353+00	low
90f2a7da-a902-4d06-82b1-1d50ca812330	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.153.193	\N	\N	Successful login	2025-11-12 12:08:24.519209+00	low
d7f29562-b5df-4878-ba87-ad5bee30fb8d	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	109.178.153.193	\N	\N	Successful login	2025-11-12 12:22:57.342101+00	low
dd7f53c2-1973-42c9-9a19-238c9769b0d6	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	31.152.50.242	\N	\N	Successful login	2025-11-13 10:30:48.448483+00	low
a0a81b15-d70e-44be-b80a-bf787886e847	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	31.152.50.242	\N	\N	Successful login	2025-11-17 11:17:00.176704+00	low
084181cc-b9be-404e-b600-836bded11eaf	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	31.152.50.242	\N	\N	Successful login	2025-11-18 14:57:11.946501+00	low
d697643f-f4e3-42f8-8079-c6d53c722430	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	login_success	31.152.50.242	\N	\N	Successful login	2025-11-18 14:59:00.56131+00	low
a95e9ed5-d053-4311-9c91-25b41be2a1bf	49245fcc-06f5-43a6-9fa6-8f59648a0527	login_success	31.152.50.242	\N	\N	Successful login	2025-11-19 12:48:00.506275+00	low
a1993e65-ec55-4abf-ab23-7de962bcb4ff	ec000c4c-dd24-4f95-b86d-b0835204843c	login_success	31.152.50.242	\N	\N	Successful login	2025-11-20 09:18:25.140804+00	low
\.


--
-- Data for Name: stock_adjustments; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.stock_adjustments (id, inventory_id, user_id, adjustment_date, quantity_adjusted, reason_code, notes, created_at, updated_at) FROM stdin;
7ef40618-6278-4886-ab80-0b7670989c65	e883361b-12fd-45dc-afa6-faeefbb929af	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-29 17:23:27.826835+00	100.000	Stocktake adjustment		2025-09-29 17:23:27.826835+00	2025-09-29 17:23:27.826835+00
09747fd5-e846-4bc9-987a-3d8cec7a3089	e883361b-12fd-45dc-afa6-faeefbb929af	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-29 17:26:25.449289+00	50.000	Stocktake adjustment		2025-09-29 17:26:25.449289+00	2025-09-29 17:26:25.449289+00
580c496f-844a-4784-b564-89c2cd7b9743	e883361b-12fd-45dc-afa6-faeefbb929af	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-29 17:30:04.679029+00	0.000	Expired items		2025-09-29 17:30:04.679029+00	2025-09-29 17:30:04.679029+00
\.


--
-- Data for Name: stocktake_items; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.stocktake_items (id, stocktake_id, part_id, expected_quantity, actual_quantity, counted_at, counted_by_user_id, notes, created_at, updated_at) FROM stdin;
e842454a-570b-4277-bc5b-3ef729111bb2	de3e9d0c-eca5-4ee0-ba28-5adc1615d406	a7aaa666-6a7a-7a8b-9c01-234567890123	150.000	\N	\N	\N	\N	2025-10-21 23:34:37.052938+00	2025-10-21 23:34:37.052938+00
eb0afaad-87f1-4701-9449-78c74c7d48c3	de3e9d0c-eca5-4ee0-ba28-5adc1615d406	b8bbb777-7b8b-8b9c-0123-456789012345	25.000	\N	\N	\N	\N	2025-10-21 23:34:37.052938+00	2025-10-21 23:34:37.052938+00
607e0c5e-5e8c-4c52-abf8-b8dcde417cd6	de3e9d0c-eca5-4ee0-ba28-5adc1615d406	a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d7	15.000	\N	\N	\N	\N	2025-10-21 23:34:37.052938+00	2025-10-21 23:34:37.052938+00
9c444fbb-3906-4c2e-a1f8-64c78e119745	de3e9d0c-eca5-4ee0-ba28-5adc1615d406	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	200.000	\N	\N	\N	\N	2025-10-21 23:34:37.052938+00	2025-10-21 23:34:37.052938+00
32d0dd7e-04b2-430f-abef-7a009e9d059a	0e4dd9d9-e983-44ba-8826-9a0d0e1ad8f8	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	4.000	1.000	2025-11-12 12:07:09.19343+00	49245fcc-06f5-43a6-9fa6-8f59648a0527		2025-11-12 12:06:41.481491+00	2025-11-12 12:07:09.180211+00
d3a524be-66d7-4148-b642-ec59bb395ef8	0e4dd9d9-e983-44ba-8826-9a0d0e1ad8f8	e1457957-9441-48d9-a161-75faff16bd5d	4.000	5.000	2025-11-12 12:07:14.732585+00	49245fcc-06f5-43a6-9fa6-8f59648a0527		2025-11-12 12:06:41.481491+00	2025-11-12 12:07:14.726053+00
\.


--
-- Data for Name: stocktakes; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.stocktakes (id, warehouse_id, scheduled_date, status, notes, scheduled_by_user_id, completed_date, completed_by_user_id, created_at, updated_at) FROM stdin;
de3e9d0c-eca5-4ee0-ba28-5adc1615d406	11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-10-23 07:00:00+00	planned		f6abc555-5b6c-6f7a-8b9c-0d123456789a	\N	\N	2025-10-21 23:34:37.027449+00	2025-10-21 23:34:37.027449+00
0e4dd9d9-e983-44ba-8826-9a0d0e1ad8f8	1e019a80-2852-4269-b3d3-2c5a46ded47f	2025-11-13 05:00:00+00	in_progress		49245fcc-06f5-43a6-9fa6-8f59648a0527	\N	\N	2025-11-12 12:06:41.46181+00	2025-11-12 12:07:09.180211+00
\.


--
-- Data for Name: supplier_order_items; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.supplier_order_items (id, supplier_order_id, part_id, quantity, unit_price, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: supplier_orders; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.supplier_orders (id, ordering_organization_id, supplier_name, order_date, expected_delivery_date, actual_delivery_date, status, notes, created_at, updated_at) FROM stdin;
db640c51-53e5-475b-8696-fd1e923381d6	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	AutoParts Ltd	2025-08-06 00:00:00+00	2025-08-22 00:00:00+00	\N	Pending		2025-08-06 14:20:51.206223+00	2025-08-06 14:20:51.206223+00
\.


--
-- Data for Name: system_configurations; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.system_configurations (id, category, key, value, data_type, description, is_system_managed, is_user_configurable, requires_restart, validation_rules, default_value, created_by_user_id, updated_by_user_id, created_at, updated_at) FROM stdin;
2bcb93cb-29f1-4db7-8fb1-037df1ba5481	ORGANIZATION	org.default_country	GR	ENUM	Default country for new organizations	f	t	f	{"allowed_values": ["GR", "KSA", "ES", "CY", "OM"]}	GR	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
5149b532-4e80-4b00-bf68-1714ea0f3798	ORGANIZATION	org.auto_create_warehouse	true	BOOLEAN	Automatically create default warehouse for new organizations	f	t	f	null	true	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
d7719c6e-cf7b-472e-88a7-adc181a1458e	ORGANIZATION	org.max_suppliers_per_organization	50	INTEGER	Maximum number of suppliers per organization	f	t	f	{"min": 1, "max": 200}	50	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
dac6b214-30d0-463b-90ed-41fe0b8a0ebd	PARTS	parts.max_photos_per_part	4	INTEGER	Maximum number of photos per part	f	t	f	{"min": 1, "max": 10}	4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
a7a3ad20-cd95-4438-b5b1-5932473d7e12	PARTS	parts.photo_max_size_mb	5	INTEGER	Maximum photo size in MB	f	t	f	{"min": 1, "max": 20}	5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
b2b5da09-4d42-4b98-8ffd-c21ffa6904e2	PARTS	parts.supported_photo_formats	["jpg", "jpeg", "png", "webp"]	JSON	Supported photo formats for parts	f	t	f	null	["jpg", "jpeg", "png", "webp"]	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
0b93a918-c297-46ef-988a-795970634af3	USER_MANAGEMENT	user.password_min_length	8	INTEGER	Minimum password length	f	t	f	{"min": 6, "max": 128}	8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
41e02717-f7e0-445e-974b-762586a51e99	USER_MANAGEMENT	user.session_timeout_minutes	480	INTEGER	Session timeout in minutes	f	t	f	{"min": 30, "max": 1440}	480	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
f9dff7d3-b524-41ca-b8e2-aaa8b13ed10b	USER_MANAGEMENT	user.max_failed_login_attempts	5	INTEGER	Maximum failed login attempts before lockout	f	t	f	{"min": 3, "max": 10}	5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
a7f9364d-1127-4658-b013-50fad8718af8	LOCALIZATION	locale.supported_languages	["en", "el", "ar", "es"]	JSON	Supported languages	f	t	f	null	["en", "el", "ar", "es"]	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
e03be385-b9f4-4696-88fa-fc4ed6d96187	LOCALIZATION	locale.supported_countries	["GR", "KSA", "ES", "CY", "OM"]	JSON	Supported countries	f	t	f	null	["GR", "KSA", "ES", "CY", "OM"]	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
e4328f0c-251e-4005-8d29-c9bfaf20b6dc	LOCALIZATION	locale.default_language	en	ENUM	Default language for new users	f	t	f	{"allowed_values": ["en", "el", "ar", "es"]}	en	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:38:34.534003+00	2025-07-31 10:38:34.534003+00
7fa75079-fd24-47e8-bdf0-3a4bd269437d	ORGANIZATION	test.config	test_update_value	STRING	Test configuration	f	t	f	\N	\N	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-07-31 10:30:17.074828+00	2025-07-31 15:13:51.567115+00
\.


--
-- Data for Name: transaction_approvals; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.transaction_approvals (id, transaction_id, approver_id, status, notes, created_at) FROM stdin;
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.transactions (id, transaction_type, part_id, from_warehouse_id, to_warehouse_id, machine_id, quantity, unit_of_measure, performed_by_user_id, transaction_date, notes, reference_number, created_at) FROM stdin;
9b090e84-655b-4c58-b1a1-a3298654462d	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	22eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	402317bf-7d65-432f-9099-6ed4a852b95c	\N	5.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-15 14:54:03.837802+00	Transfer from Spare Parts Warehouse to Test WH	\N	2025-09-15 14:54:03.837802+00
15e4bb6b-557b-48ee-b12a-3ff1e49e9b01	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	1.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-15 15:23:48.853048+00	Transfer from Test WH to Test WH II	\N	2025-09-15 15:23:48.853048+00
5940e747-96cc-4094-9606-f91c20d48ee1	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	1.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-15 15:25:14.36398+00	Transfer from Test WH to Test WH II	\N	2025-09-15 15:25:14.36398+00
b8c796d8-bfb9-416d-9535-2b821b5ebd1f	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	1.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-15 15:25:45.325788+00	Transfer from Test WH to Test WH II	\N	2025-09-15 15:25:45.325788+00
ceb716c6-c681-4aba-9ad9-4fb904d8bd69	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	1.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-15 15:26:13.160535+00	Transfer from Test WH to Test WH II	\N	2025-09-15 15:26:13.160535+00
88dcfd27-d184-48bc-a888-21f3a7840c20	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	1.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-15 15:27:09.717129+00	Transfer from Test WH to Test WH II	\N	2025-09-15 15:27:09.717129+00
bd40ac82-686b-409c-8891-e8b1da8d6366	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	50.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-29 17:24:02.614272+00	Transfer from Test WH to Test WH II	\N	2025-09-29 17:24:02.614272+00
be652d47-fe20-43a6-aa63-b761758befde	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	5.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-29 17:27:11.598071+00	Transfer from Test WH to Test WH II	\N	2025-09-29 17:27:11.598071+00
50ff80b5-c974-4e3e-a301-50e72165a2d2	transfer	a7aaa666-6a7a-7a8b-9c01-234567890123	402317bf-7d65-432f-9099-6ed4a852b95c	70851ed9-1146-4abb-8463-699907dfefe9	\N	20.000	pieces	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2025-09-29 17:28:39.65465+00	Transfer from Test WH to Test WH II	\N	2025-09-29 17:28:39.65465+00
47eea23f-59a0-4c78-b0b5-4b8000f191ec	creation	b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f	\N	1e019a80-2852-4269-b3d3-2c5a46ded47f	\N	2.000	pieces	49245fcc-06f5-43a6-9fa6-8f59648a0527	2025-10-21 10:09:11.322262+00	Customer order fulfillment - Order ID: 53ae4a63-b7e4-4a49-8f59-0a768edc6d37	\N	2025-10-21 10:09:11.296726+00
b1e1a35c-4f81-49f6-a858-fd155ceb4d01	creation	e1457957-9441-48d9-a161-75faff16bd5d	\N	1e019a80-2852-4269-b3d3-2c5a46ded47f	\N	2.000	pieces	49245fcc-06f5-43a6-9fa6-8f59648a0527	2025-10-22 15:50:10.977476+00	Customer order fulfillment - Order ID: 26f2d136-c8b9-48cd-84f5-0cd5e94ce9b8	\N	2025-10-22 15:50:10.961949+00
\.


--
-- Data for Name: user_management_audit_logs; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.user_management_audit_logs (id, user_id, action, performed_by_user_id, "timestamp", details) FROM stdin;
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.user_sessions (id, user_id, session_token, ip_address, user_agent, created_at, last_activity, expires_at, is_active, terminated_reason) FROM stdin;
2fd6c94f-f4de-47ba-86c3-2bd4c67e4611	f6abc555-5b6c-6f7a-8b9c-0d123456789a	R8vl6nbHsuwaXiFUrZtHxOdZoKe-LmyxJxj_4miWzhc	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-17 13:01:53.952091+00	2025-07-17 13:01:53.952091+00	2025-07-17 21:01:53.948697+00	t	\N
259db65e-5c0c-4ef0-a9eb-53ecc016c564	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ZiZ0DGbiLjnpA6fAIJxygi_YmQ7YaSIqPytTEzmf-UY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-17 13:03:01.328809+00	2025-07-17 13:03:01.328809+00	2025-07-17 21:03:01.328082+00	t	\N
1bd6dc07-82db-4386-8b00-4c2a03de76ee	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4msSSCFYXQjhD-S8dbONUPs8dCnQ0v6CiVA3p2OvBZ0	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-18 10:21:41.468155+00	2025-07-18 10:21:41.468155+00	2025-07-18 18:21:41.466013+00	t	\N
828f14e5-1861-47d8-9289-e13404443cf4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2KkqHZckH2lMcgE9YIpYKdzL9XwuUzOZx0PWXt9T4Zw	172.18.0.1	curl/8.6.0	2025-07-18 10:40:36.591174+00	2025-07-18 10:40:36.591174+00	2025-07-18 18:40:36.589238+00	t	\N
742b28f7-ffe4-4aa2-b5e1-d48673d9cb26	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ArHlHPljAdyUqltPz5UeIavZaqRXqmbsHhjs4JDy_aE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-18 11:04:38.767653+00	2025-07-18 11:04:38.767653+00	2025-07-18 19:04:38.765631+00	t	\N
d15f4e27-2080-42f4-b3be-dbc8a04490ff	f6abc555-5b6c-6f7a-8b9c-0d123456789a	nHf7boXZPWHPgZAmpJRyjDNkmDzCm5vY1cfFNWFn7Ws	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-18 12:58:48.89694+00	2025-07-18 12:58:48.89694+00	2025-07-18 20:58:48.894948+00	t	\N
1033bb1f-5367-4bfd-b9de-4ff958ad8cf8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PKhP9hhlYXq8LIvb-aTNMGTz8iUns4iHH92xf5fUEgA	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-18 12:59:07.944932+00	2025-07-18 12:59:07.944932+00	2025-07-18 20:59:07.944352+00	t	\N
063716a3-15fa-4560-ac86-0cbf0bb43d1b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	n3Lh96sV3RyQe87hctIzcIvVQ74nsR4jQc2PH-BIbJI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-18 14:00:40.423105+00	2025-07-18 14:00:40.423105+00	2025-07-18 22:00:40.421245+00	t	\N
ad6fa9d0-72b4-4caf-b571-5ba5e7e4de82	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sW1KvHVjPCamQX1tOCA0j17SXl2-aznNzhShISCiPY8	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-19 22:48:28.741756+00	2025-07-19 22:48:28.741756+00	2025-07-20 06:48:28.739209+00	t	\N
46651c7c-c104-40c3-af35-b3fcfa57ba2b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	mg9LFDOuuuBXqIHdkk2_no8fIUK0Zu6LJY-qwcBfQE0	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-19 23:29:27.946346+00	2025-07-19 23:29:27.946346+00	2025-07-20 07:29:27.943659+00	t	\N
0ee0d44c-e2ed-4304-a24b-250188c3bfb4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	BH6kum1yEoPetZpcPQsmlyoSNey71j6q25sZxUeftQg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-19 23:32:58.501236+00	2025-07-19 23:32:58.501236+00	2025-07-20 07:32:58.500556+00	t	\N
e4c85d49-deed-417b-b04a-826ca78fcff4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	9W7YX2MU9nDPVPVnnudVYRmBn337-cQhExoHpr5N5hs	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-19 23:42:15.243979+00	2025-07-19 23:42:15.243979+00	2025-07-20 07:42:15.241191+00	t	\N
95384539-550d-400c-80b0-133ad20f53bb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pcogFymbvjEZG8iwXe3nhlQ384ULEVgtjmFRxeqiz8w	172.18.0.1	curl/8.6.0	2025-07-20 00:05:50.790864+00	2025-07-20 00:05:50.790864+00	2025-07-20 08:05:50.788982+00	t	\N
4c741a1d-9938-4b6f-bea9-f71f1e2a94dc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kI6BNiYsGatnZEyJKYCWfL1lQGbmwqLg2lgS6KHcPrs	172.18.0.1	curl/8.6.0	2025-07-20 00:07:29.060369+00	2025-07-20 00:07:29.060369+00	2025-07-20 08:07:29.058245+00	t	\N
0bee9330-0662-4e34-bc91-6c40c5599002	f6abc555-5b6c-6f7a-8b9c-0d123456789a	snxWa_DX1erv5JDm3_iVjxsDPIQ_GsRvpdBncXbAH6w	172.18.0.1	curl/8.6.0	2025-07-20 00:12:24.430089+00	2025-07-20 00:12:24.430089+00	2025-07-20 08:12:24.428099+00	t	\N
7e665e27-5f22-4967-81f4-15d4186cdee5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	T-oWxaaw-87fX7EHdSOtpQczqYAO7UMHhMjuyLJUn-I	172.18.0.1	curl/8.6.0	2025-07-20 00:17:12.647197+00	2025-07-20 00:17:12.647197+00	2025-07-20 08:17:12.644022+00	t	\N
c387f66b-a772-41f4-a4b5-9e0ab25324fd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	v2phEHxJ9gA1h3xhpqhuuRvorX1GwnuMukEW_zdhRMg	172.18.0.1	curl/8.6.0	2025-07-20 00:38:13.969667+00	2025-07-20 00:38:13.969667+00	2025-07-20 08:38:13.968779+00	t	\N
a22c71f9-4d91-4c33-8df0-c7bb522dc38d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	S2mQ-64tM70U0dC9vbhXnGQphrYceFUoNy4ekjcid38	172.18.0.1	curl/8.6.0	2025-07-20 00:52:43.446637+00	2025-07-20 00:52:43.446637+00	2025-07-20 08:52:43.445635+00	t	\N
23500704-4784-4c53-8b77-1acd313ca632	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5ge8uk0G-XmrG3Q_0wfLlY_WGcZ8l62MmswrF8OeLM4	172.18.0.1	curl/8.6.0	2025-07-20 01:12:03.24281+00	2025-07-20 01:12:03.24281+00	2025-07-20 09:12:03.240632+00	t	\N
25b48b90-fcc3-4e07-b88c-d1724c8ac837	f6abc555-5b6c-6f7a-8b9c-0d123456789a	hLeotNVOt9Viy4o9apk_ruV84WJ7OPoykZWhf_63qZY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-20 08:41:19.27321+00	2025-07-20 08:41:19.27321+00	2025-07-20 16:41:19.271119+00	t	\N
e0ed5903-4f09-4b8b-96a5-699e2aff8532	f6abc555-5b6c-6f7a-8b9c-0d123456789a	s4O0hL2rzFXV36QN1-SEmKwVp4wM3QzHJcqfXDxTj1o	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-20 09:02:57.605589+00	2025-07-20 09:02:57.605589+00	2025-07-20 17:02:57.604871+00	t	\N
a99b2fd2-2741-43ab-a16f-d0b3a617600c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	VzbUjOUYIR3RnzplbjhuIs1QvXdEO7ppDshzuA6izwY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-20 17:06:04.017603+00	2025-07-20 17:06:04.017603+00	2025-07-21 01:06:04.012966+00	t	\N
720f0499-874c-4ee7-a260-3149911c21a1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	mOO3_SEzDdXcEyX8shjlqlptPSbnbOu3jgCZlyBA320	172.18.0.1	curl/8.6.0	2025-07-20 17:06:24.967435+00	2025-07-20 17:06:24.967435+00	2025-07-21 01:06:24.966472+00	t	\N
c3b7258b-e75c-4d85-931b-2e2ed21a7c4a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PPYUxz4jhQeYnKhxvuwLZ_V_U1740obkFo11e4lBOto	172.18.0.1	curl/8.6.0	2025-07-20 17:06:51.835977+00	2025-07-20 17:06:51.835977+00	2025-07-21 01:06:51.833906+00	t	\N
8dd524f0-ef7d-4074-9673-d2156f4d5d7f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	irleiUuRDtReWY9Gc_PB36WPHg9-NTjHOUraZmRF__E	172.18.0.1	curl/8.6.0	2025-07-20 17:07:07.45676+00	2025-07-20 17:07:07.45676+00	2025-07-21 01:07:07.455937+00	t	\N
7e8a51ed-c906-4728-a4a2-719143d1d113	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1RhkM0vWZ14FwDqhohp9iAPjwwMe3yiuKG7X69BG6JA	172.18.0.1	curl/8.6.0	2025-07-20 17:07:45.138545+00	2025-07-20 17:07:45.138545+00	2025-07-21 01:07:45.137686+00	t	\N
276e2cf8-3e55-4cf8-8734-d5cebfef4260	f6abc555-5b6c-6f7a-8b9c-0d123456789a	JyOixptxCKinM4b932Sl-4L0_zOR1kJ2HK-2YeRZUxk	172.18.0.1	curl/8.6.0	2025-07-20 17:28:52.069791+00	2025-07-20 17:28:52.069791+00	2025-07-21 01:28:52.067727+00	t	\N
bdba03d4-4528-4cae-8a1a-d39e60fb4ea2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	jYbAzYUzYZjd9iF4JnkQTjs2rWeuJDwz2vcQQGvc_B4	172.18.0.1	curl/8.6.0	2025-07-20 17:31:01.274461+00	2025-07-20 17:31:01.274461+00	2025-07-21 01:31:01.272283+00	t	\N
e16b7a4d-7056-4f22-8600-c5a3adc3dbe0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	qRvjbcqa9oZsjNg31qUX4T9SNE2LdJefXaLYQla0meY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-20 17:33:25.123358+00	2025-07-20 17:33:25.123358+00	2025-07-21 01:33:25.120877+00	t	\N
0fae2a4e-3905-4b20-bd38-b2cb0270c9ca	f6abc555-5b6c-6f7a-8b9c-0d123456789a	X7grh0gUWspxjz8gBXkm3EGVF0YPXiL856Ik0g1sfVI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 10:30:09.327099+00	2025-07-21 10:30:09.327099+00	2025-07-21 18:30:09.323562+00	t	\N
94ff7850-ffad-454c-b193-cba6017f1cda	f6abc555-5b6c-6f7a-8b9c-0d123456789a	rNOZ63In7lbKpF6qNtRN4Cs0rVf9RoW-jXNTH3zW1Oo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 10:30:29.349081+00	2025-07-21 10:30:29.349081+00	2025-07-21 18:30:29.348303+00	t	\N
86154929-114e-414e-a3dc-dd31fad2364e	b0ccc999-9c0c-0d12-3456-789012345678	5B_wIWxnYFGPBI9KWeH0Y1JGmAm-rcNtRV3KwiDTPQ4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:25:12.011858+00	2025-07-21 13:25:12.011858+00	2025-07-21 21:25:12.009985+00	t	\N
a69d2b4d-da2b-4e37-82b4-477aca6059c5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pybqkbnhyNLVsmWjLMYhAT2OSqSmKEWJCJmMI7gEwMY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:25:23.773044+00	2025-07-21 13:25:23.773044+00	2025-07-21 21:25:23.77224+00	t	\N
159a363b-1565-4abe-9ffc-d56c5f295e70	f6abc555-5b6c-6f7a-8b9c-0d123456789a	yws5bSKDmFX_fxudFXY87iLGPUH68WXTZrFD6VJTkKk	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:38:02.502958+00	2025-07-21 13:38:02.502958+00	2025-07-21 21:38:02.499476+00	t	\N
b38174d2-bc28-403a-a70e-927702618498	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EIrU132cyu3sRg0-WsMEq370z1rWd9KTbR-BVlA66FQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:38:42.810076+00	2025-07-21 13:38:42.810076+00	2025-07-21 21:38:42.809488+00	t	\N
77d30e3e-fa48-40f1-a635-20e081f07719	f6abc555-5b6c-6f7a-8b9c-0d123456789a	oq3m7eLNg8tidt9Nx45oIilDES-PEUurJMstQXSRHnc	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:39:01.414893+00	2025-07-21 13:39:01.414893+00	2025-07-21 21:39:01.413931+00	t	\N
8a8298ba-c119-4ad6-8665-622b300eae17	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Ck5rBdmZJOOLAMV9TxyBUjy0Kjs82ljX1ueqSSAdY34	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:49:19.767416+00	2025-07-21 13:49:19.767416+00	2025-07-21 21:49:19.764839+00	t	\N
0f2e31a0-5c11-4d68-bdd2-f32b4b5b55b5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	bICl2w9qxXKlXEF4KAcUjoJk3kR3DkDROu79CBeVAsU	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:49:37.614577+00	2025-07-21 13:49:37.614577+00	2025-07-21 21:49:37.613752+00	t	\N
dd3d1075-8359-494d-a868-36d5123adcc1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	UwPNmv8eZapnQsW8KvBzESm7d-KOxDuIgSEsQzqnUuw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 13:57:47.25138+00	2025-07-21 13:57:47.25138+00	2025-07-21 21:57:47.24905+00	t	\N
76f61fc3-247c-4c1e-b7ef-c40e1a3f2d12	f5abc444-4a5b-5e6f-7a8b-9c0123456789	4fi9CVwRdJ0caw5PUkRsSqmd2FAUGoyk4-TnQnBM5Xo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:33:39.239746+00	2025-07-21 14:33:39.239746+00	2025-07-21 22:33:39.237755+00	t	\N
6866f7bf-36fa-49e6-a4b0-46908a643fbc	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	qcNPtne6vFlChINZoRx5Ty6JlEsjHxj4oH6qkESSrbQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:34:01.7097+00	2025-07-21 14:34:01.7097+00	2025-07-21 22:34:01.708964+00	t	\N
c628a9fd-8367-4d56-82c6-bd2a07f0bfb4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	UgIZj_blu-gDxxzV1KXu5dcfGdcPdqsCPz5gDIF7p24	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:35:02.492022+00	2025-07-21 14:35:02.492022+00	2025-07-21 22:35:02.491029+00	t	\N
f196442a-59e0-4d01-82e5-1c20054335b7	f5abc444-4a5b-5e6f-7a8b-9c0123456789	bome_hIcocEnJVTaUEXOv-xvEG73SdOu1arIDaaDaYY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:43:33.210267+00	2025-07-21 14:43:33.210267+00	2025-07-21 22:43:33.209441+00	t	\N
a06ef9ae-64a3-43f4-a713-d2a76e2f03af	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	-x20v-hUj1Yn1Lc8LHOceJyaK6TOujrPj0KVOh4xsCk	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:43:49.606681+00	2025-07-21 14:43:49.606681+00	2025-07-21 22:43:49.605951+00	t	\N
c41c67f2-c481-451b-9abb-4d0dff13db4b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	HJyNUDH1b335PHS0LA3zb6gX47npnlrJy8wwTTKOVhI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:48:49.061144+00	2025-07-21 14:48:49.061144+00	2025-07-21 22:48:49.060308+00	t	\N
a5c29ee7-66d8-42c3-9d7d-a1c1ee8a9911	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	_BF8BPw0n8SykGAaNpQOXMpuM9tg5pt1Df4w-tHSh3w	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 14:49:34.989811+00	2025-07-21 14:49:34.989811+00	2025-07-21 22:49:34.988847+00	t	\N
e96ad686-e74f-463c-bff9-a691beef8fc1	f5abc444-4a5b-5e6f-7a8b-9c0123456789	8Dh5LtZ96ioVU7ShwD_HOhHq1gydriQqqxJNdUAT1hY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 15:02:47.620989+00	2025-07-21 15:02:47.620989+00	2025-07-21 23:02:47.618666+00	t	\N
3a689b14-e8e4-45fe-8222-2bf199791940	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	KdmcT5lCjskckSUv0PXO7398sjCNNV28SyEBupjm5BA	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 16:13:35.145449+00	2025-07-21 16:13:35.145449+00	2025-07-22 00:13:35.143425+00	t	\N
99e68861-addb-4e0e-aa95-4f095f83d510	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5XzdVb_XMBsNZAMOx0RDuCIqlQI2dlMktZNupxC1OAg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 17:03:04.720599+00	2025-07-21 17:03:04.720599+00	2025-07-22 01:03:04.718337+00	t	\N
f6632b6c-7261-47d1-9e41-e276e7ccd302	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5mpB-pZvmt1f5aXo1zgLiuPFZ2B93G1DIg0LtBc2nZw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 17:20:31.755776+00	2025-07-21 17:20:31.755776+00	2025-07-22 01:20:31.754798+00	t	\N
4c8264e3-fa05-4043-8963-7ce3cb162078	f6abc555-5b6c-6f7a-8b9c-0d123456789a	9UWCu-pAVI6rLl8ZuIpa7Ep_IhBklxs-ZVCdHvgoDFI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 17:21:46.237645+00	2025-07-21 17:21:46.237645+00	2025-07-22 01:21:46.236742+00	t	\N
ee9bebb4-d5b1-499f-92e8-b50a33db2b67	f6abc555-5b6c-6f7a-8b9c-0d123456789a	vcis0o99LlGymlnaAK8FRvRDIg2a6eBtQSY-Qom2XBI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 17:22:01.435084+00	2025-07-21 17:22:01.435084+00	2025-07-22 01:22:01.434396+00	t	\N
90aed9a8-fcce-4bff-9b43-f7b50e597d3f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	tGFpOgxONjysLR09qB33AnzBjapJzZkt1ogwV85tJCE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-21 17:26:58.191595+00	2025-07-21 17:26:58.191595+00	2025-07-22 01:26:58.18961+00	t	\N
6b535ccb-56d1-4e4e-aed3-b76b5f51a353	f6abc555-5b6c-6f7a-8b9c-0d123456789a	LxOLc1E7Vd3MgoLx1nC6fN-l3b0DuiJSXx_OFml7h18	172.18.0.1	curl/8.6.0	2025-07-21 23:18:36.372776+00	2025-07-21 23:18:36.372776+00	2025-07-22 07:18:36.370148+00	t	\N
610f64e5-4389-4dd2-808e-98b4c1a4bf84	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Ddc6rVqUdJ9kTQLPS1sEpCTsc-yF0r07uZMtI3WNhpE	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-21 23:23:23.8688+00	2025-07-21 23:23:23.8688+00	2025-07-22 07:23:23.868059+00	t	\N
cfa9fd04-6799-4091-98be-5ab9b0839308	f6abc555-5b6c-6f7a-8b9c-0d123456789a	r_YNRRSv04UHdI1AyaFOklHvvI6uJWFHPNWyvK6djuM	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-21 23:23:52.782722+00	2025-07-21 23:23:52.782722+00	2025-07-22 07:23:52.781973+00	t	\N
817d0a77-587c-4823-b342-0378f15d617d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	acY71zf1hADe8BK59nkqspPENx7q1gKvRBa2ZjICrtY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 09:41:50.812941+00	2025-07-22 09:41:50.812941+00	2025-07-22 17:41:50.786756+00	t	\N
efdf4ad8-6c87-4f49-899f-0f511ea848c8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	lzAOxgq0FWd55vMgXQT6xjehJKIcpp1OyztE7A4QDww	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 10:02:17.874906+00	2025-07-22 10:02:17.874906+00	2025-07-22 18:02:17.870006+00	t	\N
fb7fbd49-1141-42fc-a0b7-68806d700044	f6abc555-5b6c-6f7a-8b9c-0d123456789a	tUpY-BAbLmGs3ATnoW-Vrngz7cEMK0-CFGhwR-QjxME	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 10:14:27.471192+00	2025-07-22 10:14:27.471192+00	2025-07-22 18:14:27.46654+00	t	\N
e5d4c75a-bd35-4237-8aa5-cb05fb21f8ae	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8uo8RlJiKxzz4c1kT8BrmMyD77DkuhUgsl_1BXPVDFY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 10:28:33.930896+00	2025-07-22 10:28:33.930896+00	2025-07-22 18:28:33.92519+00	t	\N
75bdbaaa-b65a-4e62-8607-a2b111dcf062	f6abc555-5b6c-6f7a-8b9c-0d123456789a	LuBTZ48a-VGLJQCqpPSJZOgtvfZTIRamcQicGyF63iA	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 10:48:23.420678+00	2025-07-22 10:48:23.420678+00	2025-07-22 18:48:23.417161+00	t	\N
c26f3dd0-8a81-43e0-a093-9d42e9722bd7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-JxYG4yQ7deu7sKK3WBuZOqOJ-xueHnh9o3ic5KZkD0	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:01:21.958751+00	2025-07-22 14:01:21.958751+00	2025-07-22 22:01:21.955456+00	t	\N
9f7d83ed-bdf6-4a6c-bbec-62840c4f9402	f6abc555-5b6c-6f7a-8b9c-0d123456789a	lEbGgZb1MAxT7POCCDc_63UsliAY4RrXulwEn-nftBo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:01:45.462562+00	2025-07-22 14:01:45.462562+00	2025-07-22 22:01:45.461843+00	t	\N
80f33e37-b035-48c4-a40c-82f2f9a78976	f6abc555-5b6c-6f7a-8b9c-0d123456789a	zqQBYjF-hkdLD6H_-3-5vXit0M3t6nxvN69KyxNEgvA	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:19:47.10975+00	2025-07-22 14:19:47.10975+00	2025-07-22 22:19:47.107374+00	t	\N
51f45133-8499-419a-b921-b253bb1f3408	f6abc555-5b6c-6f7a-8b9c-0d123456789a	f7wl6Lb7qO6ogLHPM9JgS_vSij8dckEEzArfOyQMMSg	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:19:49.742172+00	2025-07-22 14:19:49.742172+00	2025-07-22 22:19:49.741425+00	t	\N
dc361d33-2ca8-4206-b9c2-50e48fcce6fd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	so6WAmk2rxKh2-xOHoQx8sEFJVM16aJjQq4WFCOE8uA	172.18.0.1	curl/8.6.0	2025-07-25 15:58:19.951688+00	2025-07-25 15:58:19.951688+00	2025-07-25 23:58:19.950773+00	t	\N
3d4cd482-5023-4f07-9fe3-9fe253b899f6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pjPdr4WZTDVa99OpBG1ZJycmUCXJCmZuTe9_0nhHAWw	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:19:50.768153+00	2025-07-22 14:19:50.768153+00	2025-07-22 22:19:50.767353+00	t	\N
1ac2d2f6-9ccc-46da-b264-81fafd793f81	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EZEKSjHy1XXRFxT8LybhZvP_q7zWeYv5reWm_n6kD4s	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:19:59.299135+00	2025-07-22 14:19:59.299135+00	2025-07-22 22:19:59.298327+00	t	\N
775b13ce-ee40-4627-9527-3b23e0bac8f7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eF9-GVxUvDa3FyCukVg4FIxktBvT2ZLChOhvpfqol-w	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:20:07.870712+00	2025-07-22 14:20:07.870712+00	2025-07-22 22:20:07.869853+00	t	\N
be22b4bd-fa7a-4253-b6ff-e421c799ae5c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8tSlT-nKuGDI-kdJz6kJ1s2AsGL7hun2ko_UtZ_SDLs	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:20:10.18507+00	2025-07-22 14:20:10.18507+00	2025-07-22 22:20:10.184017+00	t	\N
cb0a0b23-cb90-4346-902e-b480573eb8d6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	R4ZpMJ7jxfPHiHS-H1dddj9dSsWxl4DYho04_1kQo78	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:22:54.789724+00	2025-07-22 14:22:54.789724+00	2025-07-22 22:22:54.787752+00	t	\N
f592e863-d3df-48eb-895b-994954ebb555	f6abc555-5b6c-6f7a-8b9c-0d123456789a	A0BZZiTYNoNsi2s6ioTQBpiz-e4KFgehZulPlqWfW5U	172.18.0.1	curl/8.6.0	2025-07-22 14:24:33.798379+00	2025-07-22 14:24:33.798379+00	2025-07-22 22:24:33.797761+00	t	\N
58155997-0941-4b40-ac92-5b247a96a95e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	aCrDAeEU9r44khp5cFb0kulRuuByiQYLXE6_pwERO7o	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:25:41.473014+00	2025-07-22 14:25:41.473014+00	2025-07-22 22:25:41.47234+00	t	\N
8ee38796-a94a-4f57-aba6-ae192a34cfa9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	bEmjnB1a9ucNFasdJwE-CRIF5q7OdVe0lYob3sNZZ7c	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:25:47.423629+00	2025-07-22 14:25:47.423629+00	2025-07-22 22:25:47.42277+00	t	\N
1b31befe-3dab-4b27-a9f4-632fe56b0053	f6abc555-5b6c-6f7a-8b9c-0d123456789a	uUSTph9_JjP-qjoFxV3TTZctEKV7vJq23P_LUp4YvkU	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:33:39.830397+00	2025-07-22 14:33:39.830397+00	2025-07-22 22:33:39.829481+00	t	\N
74d17ef7-0897-4c34-98ef-4047a3782936	f6abc555-5b6c-6f7a-8b9c-0d123456789a	j5kLi7kefxCC152gkyEilk8PVNoo3H6oOVJ9kXo9Gi0	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:34:29.802112+00	2025-07-22 14:34:29.802112+00	2025-07-22 22:34:29.800543+00	t	\N
cb56b8a0-9b8b-4395-8e8c-9988d7ab38b9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ZkOYGr_q9FtxXuuCUIx_0umrsJDEoma1jv8-ESSq_hk	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:34:46.454093+00	2025-07-22 14:34:46.454093+00	2025-07-22 22:34:46.45344+00	t	\N
6ca1f5d3-fe17-49ed-a266-781cbeb6cd2d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	SCRXunF3QIYg_Jd9EBJDxmh70hWNoeTpdoZaoDGe0lo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:34:57.861239+00	2025-07-22 14:34:57.861239+00	2025-07-22 22:34:57.860472+00	t	\N
d4e77f06-1008-4ec9-80f5-508c1f6bebd1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	6AG7LEbGgL_eI-Te77IbOKu9AUKtmg20iKi3IAHaOJE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:35:40.411499+00	2025-07-22 14:35:40.411499+00	2025-07-22 22:35:40.410314+00	t	\N
39620814-57b9-4d48-8a9f-c498fbd781e7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	LA6455YZ7fkOy3G0kKp5JSbBmhpcPsMvlunPbDN8kCg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:35:49.01736+00	2025-07-22 14:35:49.01736+00	2025-07-22 22:35:49.016531+00	t	\N
35568c31-e2cc-4a04-91c9-bb6df83dcdc6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_9LhiTYZndTek9O7I0b8Yd9mlIM2znckQHZPxY2e6oM	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 14:38:50.905923+00	2025-07-22 14:38:50.905923+00	2025-07-22 22:38:50.904106+00	t	\N
3f3779e2-24b3-40d8-9f17-1b96fc7e3c1b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	HRLi6JiITtQGIZRZknMmKLQhUDsKTUh9zIaCw57_HYc	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:40:03.284223+00	2025-07-22 14:40:03.284223+00	2025-07-22 22:40:03.283476+00	t	\N
578ec022-0c5c-4834-98dc-af94b478477b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5ddy9zxXTPpe-KJcOmnaJ7wE1cZmb8X3-Dfa0NtixjU	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:40:07.276198+00	2025-07-22 14:40:07.276198+00	2025-07-22 22:40:07.275454+00	t	\N
6adcd351-dc92-42f0-9455-8d7133012061	f6abc555-5b6c-6f7a-8b9c-0d123456789a	13W_QUvvMiPg2-eSPVHXMCXxUZhUZH-Fej8AQRnQWLY	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:40:08.553125+00	2025-07-22 14:40:08.553125+00	2025-07-22 22:40:08.552494+00	t	\N
aa5bb9fa-c9cd-4cfa-a0f4-7876cbebfae6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	cLPuBrxKFDkPZy_9cXFAPZoIUBj66VojSsy8D8tBPIg	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:40:09.445372+00	2025-07-22 14:40:09.445372+00	2025-07-22 22:40:09.44477+00	t	\N
4705e1bf-3ebc-4a83-8fc6-a04bc5a9faeb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	q9CiVhNBA2vZXerTZP56oS70CCaT3J1zRv0tTy9j-iU	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:40:22.13495+00	2025-07-22 14:40:22.13495+00	2025-07-22 22:40:22.133947+00	t	\N
07789237-96f3-479e-a33b-3aafb2f5e74b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kCgNooGcToa8OwwWibsnuZtdI7NkuGDzJl7M3IUiO-k	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:40:23.901008+00	2025-07-22 14:40:23.901008+00	2025-07-22 22:40:23.900229+00	t	\N
89b28110-a250-4712-94f5-030a8c64bdb7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	qXmKee_UWPXqvsZ0BasqWD7C2lSWBXd9gKBYyD0eYCc	172.18.0.1	curl/8.6.0	2025-07-22 14:40:32.030279+00	2025-07-22 14:40:32.030279+00	2025-07-22 22:40:32.02933+00	t	\N
2e38f6da-caea-401c-bcfa-c36a4ade7431	f6abc555-5b6c-6f7a-8b9c-0d123456789a	nD5MBJee_MPTBfeRPe34CvK1HdQ8mnxF8RwURkfsHx0	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:43:42.296093+00	2025-07-22 14:43:42.296093+00	2025-07-22 22:43:42.293966+00	t	\N
f254ca29-3473-49d3-9bfd-b53134ecd71e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_U0fSK5MKI0zmZ-Wjprsc3IT-u-TlTvVAEV3LCkGC80	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:43:46.938547+00	2025-07-22 14:43:46.938547+00	2025-07-22 22:43:46.93775+00	t	\N
59723286-cdc0-4cfb-95eb-6a1fa6a17479	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4Oefl4dP_YEQfBzReb3Z6hQsBuUYnz97MFbxhvCS6PU	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 14:43:48.274117+00	2025-07-22 14:43:48.274117+00	2025-07-22 22:43:48.273437+00	t	\N
136b6cd9-7312-4236-8af4-b8643579bd50	f6abc555-5b6c-6f7a-8b9c-0d123456789a	cV_lpU9H0LCldwdz_tAI8pzCi1rNL0c-7FGkBiZnsC0	172.18.0.1	curl/8.6.0	2025-07-22 14:51:54.191042+00	2025-07-22 14:51:54.191042+00	2025-07-22 22:51:54.189199+00	t	\N
c32d5533-14f0-4f57-ad7f-5791ed0cdcfb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	xmUeRlyI2nR16wr8Vav79Em88p0A1bSjiryIRYDL7jQ	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:00:22.60793+00	2025-07-22 15:00:22.60793+00	2025-07-22 23:00:22.605519+00	t	\N
514a6026-a3f1-41ad-a519-39dd42ef9b43	f6abc555-5b6c-6f7a-8b9c-0d123456789a	TXcka2DgJr21ahpEq3yY8O4vipd9G0bEfGL4StHTfgg	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:00:23.604003+00	2025-07-22 15:00:23.604003+00	2025-07-22 23:00:23.603352+00	t	\N
e647ec9f-76b5-43bb-a000-b717b547a346	f6abc555-5b6c-6f7a-8b9c-0d123456789a	UEBWRzvBuv_dttITa4zjnYkrGSQp59HYVckg_IOjSvY	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:00:24.509782+00	2025-07-22 15:00:24.509782+00	2025-07-22 23:00:24.509126+00	t	\N
e22e260d-86bb-4b04-a40d-63155c1425b2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	zq06wkcFy6GEZp3-_NNCViOdFBxapL5tBFcQ_u4_o1I	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:03:41.61777+00	2025-07-22 15:03:41.61777+00	2025-07-22 23:03:41.617047+00	t	\N
a1d704e2-f3d0-448c-8ef4-739138f589d5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	AFB57qfNKQGqCgRbNpfu5kQOm_nAfojlP9gmh9hFiYk	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:06:00.385321+00	2025-07-22 15:06:00.385321+00	2025-07-22 23:06:00.384365+00	t	\N
b4befd0f-9cca-4dcd-8636-392d0f2b818f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	A8LTG-KKvHREuLVT1qVNccdtaKcPMX1pBMXtd4ZL-O0	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:09:31.738767+00	2025-07-22 15:09:31.738767+00	2025-07-22 23:09:31.737839+00	t	\N
136aec34-2004-4f7b-b597-7258cd6097ab	f6abc555-5b6c-6f7a-8b9c-0d123456789a	vKqRJEaAA1yw7EMV-Yw6uu-nQeevlnebupbjvwaUDTA	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:09:38.463831+00	2025-07-22 15:09:38.463831+00	2025-07-22 23:09:38.4626+00	t	\N
11df37cf-bbce-4d47-9e13-cdb08e4d0053	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kSDYy5Cc5dL4SWD8JGJ0BvIeEtrZIOm8K1MMR9OSqzM	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:09:37.270066+00	2025-07-22 15:09:37.270066+00	2025-07-22 23:09:37.269045+00	t	\N
fbb4fabd-24fd-40c0-8fc7-26ff5637dd36	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Mx9QMmYxvPQ4E0Ysg6CAL-BoI1vwFyEOI63lkZ6kvvM	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:17:26.578193+00	2025-07-22 15:17:26.578193+00	2025-07-22 23:17:26.57597+00	t	\N
2a54cd77-db7b-44f8-b196-ddbd362ded7d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	TQ0urRYVKA7iNRRa-WPEErbBEmnwH3je1JHSevbSX9c	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:17:44.946931+00	2025-07-22 15:17:44.946931+00	2025-07-22 23:17:44.945979+00	t	\N
c21107a7-1cea-4123-9aad-3f0ebfc82125	f6abc555-5b6c-6f7a-8b9c-0d123456789a	D9aTpfF_Na9RATRkqBG-Xwflys8QafP35hC01zanecU	172.18.0.1	curl/8.6.0	2025-07-22 15:17:54.754194+00	2025-07-22 15:17:54.754194+00	2025-07-22 23:17:54.753455+00	t	\N
84c7f548-eb88-46e1-85cf-ab5190ed2fc5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	acAORQmcogjYdDC2NrzxfTNj3k8vmSWcOLPwCwUqqv4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 15:18:22.424834+00	2025-07-22 15:18:22.424834+00	2025-07-22 23:18:22.424093+00	t	\N
9c5dbe97-c311-475c-9789-e758fed11407	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	t-RNFjbbER8dXflE0AeW4vyOiDjgghb2BnuyTGVWYMY	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:24:04.544751+00	2025-07-22 15:24:04.544751+00	2025-07-22 23:24:04.54408+00	t	\N
149e6ff1-3a5b-4c04-b424-4016b435eb01	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pAHDxMHHnAGwl99wseGk900K2SKFnPNTaeZt2cmCSW4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 15:46:37.152968+00	2025-07-22 15:46:37.152968+00	2025-07-22 23:46:37.15099+00	t	\N
67951df9-f17b-495d-9cd4-a800659cb3b0	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	oRWMPNrKlNpytBbhRE6T5LhkdbqjHBS2xYAxyyM6Ekg	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 15:47:04.650507+00	2025-07-22 15:47:04.650507+00	2025-07-22 23:47:04.649894+00	t	\N
242386b0-ef1a-4d6b-b0c0-d6c99964759e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	wc4Sei5Fjrb3yH2x8_49dmxUiL1KEEptxg9VP8z3GQM	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 17:54:52.630601+00	2025-07-22 17:54:52.630601+00	2025-07-23 01:54:52.628341+00	t	\N
7fd53f3a-5b70-4a38-aa27-aec6b23c5f75	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	X1-7W4euJTMEHGcqAdStOKFicDcrQr33eiWb1hz40CY	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-22 17:56:15.154454+00	2025-07-22 17:56:15.154454+00	2025-07-23 01:56:15.152173+00	t	\N
e5000a60-c373-4cf3-9bbb-59972864e09b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Sd6AhGCwo1bgnH3cLdpK48BrwlMFznNWD5203wnn7PQ	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 20:35:09.5863+00	2025-07-22 20:35:09.5863+00	2025-07-23 04:35:09.583575+00	t	\N
6d4ea220-f011-463e-ba5b-ece9ee5c023c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eSqvOaNg4BEhBc8bff_K5aqZSpRK-qOp1XSKJNJllpQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-22 21:46:25.519718+00	2025-07-22 21:46:25.519718+00	2025-07-23 05:46:25.516628+00	t	\N
7ae3628f-445f-4705-90a4-c602ab899a78	f6abc555-5b6c-6f7a-8b9c-0d123456789a	TftRk6U2Xz88lN1D6__m8iK_ekZh79FRrZNO4YrCzRM	172.18.0.1	curl/8.6.0	2025-07-22 22:40:36.661953+00	2025-07-22 22:40:36.661953+00	2025-07-23 06:40:36.657839+00	t	\N
25571610-0387-4576-afd7-b7493a75c92b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4BD6GSYBbQcUw3w_afY3GncUSIaZs7jOXcZsm1x6e8k	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-23 09:23:26.658225+00	2025-07-23 09:23:26.658225+00	2025-07-23 17:23:26.654772+00	t	\N
eb716e5d-4a59-4c83-90e2-78868b7168c4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ln4EgnMGNIbXmYxwP5OXc36jJ04900eh7dUCn6t7CUY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-23 14:29:13.874827+00	2025-07-23 14:29:13.874827+00	2025-07-23 22:29:13.873808+00	t	\N
d2fae105-7209-42ac-8ea2-d67a8daa5709	f6abc555-5b6c-6f7a-8b9c-0d123456789a	mGQx3Jkm5-0vyNdnxNTcabihLZdOWNndS2Mc6-o7rZ4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-23 14:43:16.858176+00	2025-07-23 14:43:16.858176+00	2025-07-23 22:43:16.857061+00	t	\N
268dedba-ac2f-49c1-aba3-828d56bbe2cc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	JaWOgZQtQLJX9DVloFBaVJ1hBSYpa3g5nsIODQKJYlQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-23 14:51:42.444459+00	2025-07-23 14:51:42.444459+00	2025-07-23 22:51:42.443756+00	t	\N
ba7f620b-795d-49d1-9f1f-46bb2c08493d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-S_FXNgcspgyuUiB3BuyMGYTv8dYO0kzL1OEJC96nJg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-24 07:53:35.14256+00	2025-07-24 07:53:35.14256+00	2025-07-24 15:53:35.139609+00	t	\N
01b1e30d-04aa-400a-b6cd-1ae7db4dffb6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	v4APE4ReB4Sll09lGg6SFI1Mx8IifwsZwHbk1C7vpzQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-24 23:18:51.430555+00	2025-07-24 23:18:51.430555+00	2025-07-25 07:18:51.427953+00	t	\N
9ab3dcbe-aae1-4b4e-840d-bcd905294b3a	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	LAsWoCOZHqsIU4x4FtIjj7vBbOyL9FWXgFww__DWF-o	127.0.0.1	python-requests/2.32.4	2025-07-24 23:32:37.15319+00	2025-07-24 23:32:37.15319+00	2025-07-25 07:32:37.152209+00	t	\N
7eac7d83-e561-4755-973c-d6781639f848	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	OjVgoiqvFxgsN9hez2G-I7MLjPYSVEZjhsSSxWlFWSA	127.0.0.1	python-requests/2.32.4	2025-07-24 23:32:58.315671+00	2025-07-24 23:32:58.315671+00	2025-07-25 07:32:58.313452+00	t	\N
776ca947-54cb-4e12-94aa-1f1f30e32648	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	K_TeFYFBgfpy7S2Xg7aO1jpuWkJnOUlaB8C_F5ka_Cs	127.0.0.1	python-requests/2.32.4	2025-07-24 23:33:48.180702+00	2025-07-24 23:33:48.180702+00	2025-07-25 07:33:48.178515+00	t	\N
fe06d835-dfd4-462b-941a-4568df3a1d8c	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	Qc_TtY9mNnqEOdMJkKKB4-t7iv0NbG1ZzhRB-lr7PMc	127.0.0.1	python-requests/2.32.4	2025-07-24 23:34:23.283898+00	2025-07-24 23:34:23.283898+00	2025-07-25 07:34:23.282092+00	t	\N
d857f6ef-b3df-4812-bfda-91b9baffa17f	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	95CQPtp7OYekdLS7n6Vs4EXWpJ-hwMWBkyM_XOlvz5E	172.18.0.1	curl/8.6.0	2025-07-24 23:43:48.412681+00	2025-07-24 23:43:48.412681+00	2025-07-25 07:43:48.411871+00	t	\N
d9c2df87-c62e-4c4a-a270-aebc19cd62eb	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	vgpkR8AIq384-6RMRa4ZI8wqQy5YmynHZ0-6msknLG0	172.18.0.1	curl/8.6.0	2025-07-24 23:44:15.608403+00	2025-07-24 23:44:15.608403+00	2025-07-25 07:44:15.607793+00	t	\N
90116b4d-2410-4844-8c7c-e2b1d9a4566a	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	zRfPNbVCDja9SoUAE2qxWYCJvQ0wz7tdvlkC7H4qnoc	172.18.0.1	curl/8.6.0	2025-07-24 23:44:29.318647+00	2025-07-24 23:44:29.318647+00	2025-07-25 07:44:29.317991+00	t	\N
4d405462-29ab-4231-81a3-e7bad8f5177b	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	b4RleCkdV7F1v4uavFnRsllxO31WJTeLnlcovIkz_rQ	127.0.0.1	python-requests/2.32.4	2025-07-24 23:46:48.063101+00	2025-07-24 23:46:48.063101+00	2025-07-25 07:46:48.060202+00	t	\N
8c351951-dad6-4980-ab1b-8ec19881fac9	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	CmgSiWgYsJie5_X8uHeWjk8ds5EoB9UsI6raTMlcRj4	127.0.0.1	python-requests/2.32.4	2025-07-24 23:47:54.925025+00	2025-07-24 23:47:54.925025+00	2025-07-25 07:47:54.924147+00	t	\N
22c7ee00-7c09-4fc1-8d15-da43bd284713	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	xpn_3Tc6h5_Y3qzzjkri6Gf3dPV6OtoJL0JIpA2t6Q8	127.0.0.1	python-requests/2.32.4	2025-07-24 23:48:37.488084+00	2025-07-24 23:48:37.488084+00	2025-07-25 07:48:37.48439+00	t	\N
08b36424-3a50-4a81-af63-01400508c934	f6abc555-5b6c-6f7a-8b9c-0d123456789a	hANEyaUB1LfLP1ss0_2i460ShYcF3HbM6MIgqcqK9GE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-24 23:52:15.180706+00	2025-07-24 23:52:15.180706+00	2025-07-25 07:52:15.180014+00	t	\N
29b33185-8acb-4134-aa51-c1a9af4e9d19	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Tt7mfU8NMjQQzkzbp0b9YOI78Dr62GhfwG5dazdE8ig	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-25 08:13:27.611473+00	2025-07-25 08:13:27.611473+00	2025-07-25 16:13:27.608361+00	t	\N
6847d40f-5880-4eae-b409-1d1c30a132f4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-ZIatC_rL-Ss2dcxtPAsvR9FhkQsSn8sZ9zMdHYXVQU	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-25 13:56:10.891946+00	2025-07-25 13:56:10.891946+00	2025-07-25 21:56:10.889497+00	t	\N
cd9015e0-4beb-47c0-8200-ad00a64b1518	f6abc555-5b6c-6f7a-8b9c-0d123456789a	3J7QvGGmzdvmT5fhfi-hKwV9gcqnrXKvKNF9YDnhSZI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-25 13:56:28.168378+00	2025-07-25 13:56:28.168378+00	2025-07-25 21:56:28.167598+00	t	\N
0493c737-8b13-4379-80a8-fd51b799effb	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	lG46lFX6nnYyXwAXtv7jgxAiUzcb7HR9KGGksXeoDIM	172.18.0.1	curl/8.6.0	2025-07-25 15:54:59.561496+00	2025-07-25 15:54:59.561496+00	2025-07-25 23:54:59.559708+00	t	\N
39f1eb00-efcb-47e0-9453-21bd95101a88	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	_olFSNHaZT21lhj1gAnYra2PuHwi6YTTPx-cQ9_Su5k	172.18.0.1	curl/8.6.0	2025-07-25 15:55:20.348011+00	2025-07-25 15:55:20.348011+00	2025-07-25 23:55:20.347407+00	t	\N
2b4c9a68-a22a-43fa-aa5b-552513ddb42f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4TWIjK6krDNygXLfmnMQGKooYRao300ikaQish2ikBQ	172.18.0.1	curl/8.6.0	2025-07-25 15:58:37.073751+00	2025-07-25 15:58:37.073751+00	2025-07-25 23:58:37.073269+00	t	\N
525edeba-6aef-4df5-8f30-62dcded24fe4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5tYEb-HnyY8wXfy1LjCaUeJlhMeTA3iEa67tb9RXDdc	172.18.0.1	curl/8.6.0	2025-07-25 16:02:44.509328+00	2025-07-25 16:02:44.509328+00	2025-07-26 00:02:44.508573+00	t	\N
ef569807-1270-4ca1-acd0-68b15a94cdf6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	C0BaRXdkbmJmQ_-VKpNpF7jcJbbnrDjoQ3CZNJSkeBM	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-25 16:35:35.558881+00	2025-07-25 16:35:35.558881+00	2025-07-26 00:35:35.555157+00	t	\N
2cbc7986-7f2c-4e52-a7bb-69c6bf26a571	f6abc555-5b6c-6f7a-8b9c-0d123456789a	VvLJhGr8fsm_FOSqKhnIqbSY5ywAfvzoVWXCYHH8fAA	172.18.0.1	python-requests/2.32.4	2025-07-25 17:43:26.124132+00	2025-07-25 17:43:26.124132+00	2025-07-26 01:43:26.121779+00	t	\N
26e241e5-8239-4562-88de-dd735ed08f13	f6abc555-5b6c-6f7a-8b9c-0d123456789a	DYRdoVa4qxmC2s3nH1ocpDB3ueZJ8-ISM-5eJIu7MBM	172.18.0.1	python-requests/2.32.4	2025-07-25 17:44:17.241829+00	2025-07-25 17:44:17.241829+00	2025-07-26 01:44:17.239172+00	t	\N
18ebc6bf-c4bb-4b0f-9e0e-7f3efc14b0f1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	jiKD8xkwPXqmr8DE3M4Xn7Gw2I_TbC1SIKYG7ERVIpE	172.18.0.1	python-requests/2.32.4	2025-07-25 17:45:58.314626+00	2025-07-25 17:45:58.314626+00	2025-07-26 01:45:58.312756+00	t	\N
004b563b-24bf-4e90-82ee-096a754217a9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	0w3kMLPSV9c0vFz0i6RDXcVdSc1yx6kUEjdrnpgAffM	172.18.0.1	python-requests/2.32.4	2025-07-25 17:47:02.059512+00	2025-07-25 17:47:02.059512+00	2025-07-26 01:47:02.056433+00	t	\N
57d32a3f-81d6-47c6-b7b2-b1f9fc2e7d6c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_iKko5mIgzYcSmA0jXUmozK2Ap8TOb1Qfp7LZRhJ85A	172.18.0.1	python-requests/2.32.4	2025-07-25 17:48:19.850119+00	2025-07-25 17:48:19.850119+00	2025-07-26 01:48:19.84846+00	t	\N
781b9f03-4901-4350-8092-fd5de97886d4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	dQYTwDyX4rWPno9AoalCpz8xeQbgkQrA8zPc25Fm7Xc	172.18.0.1	python-requests/2.32.4	2025-07-25 17:50:16.565035+00	2025-07-25 17:50:16.565035+00	2025-07-26 01:50:16.563202+00	t	\N
60a3bf33-36ec-406c-ba38-9c2679f16f45	f6abc555-5b6c-6f7a-8b9c-0d123456789a	vW6Q1TJ4mc_kQMQg3BsnBhWKDxqJEEQ2oHzc5R8uEw0	172.18.0.1	python-requests/2.32.4	2025-07-25 17:53:34.034786+00	2025-07-25 17:53:34.034786+00	2025-07-26 01:53:34.033759+00	t	\N
676b7a51-0592-4143-80c3-24fe7fe2ada9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	rxabgJt8_a0sCybdJCpdeOqcLX7dpULJhpIZtZw8x8M	172.18.0.1	python-requests/2.32.4	2025-07-25 17:58:30.870566+00	2025-07-25 17:58:30.870566+00	2025-07-26 01:58:30.868795+00	t	\N
a4e8efbf-8c0c-4e65-bc86-9490b053d29f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	R-O8f84I0l3ue-riaJ4GaBRTUbX-4B8SHfhxdwFPpLo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-28 08:11:43.003512+00	2025-07-28 08:11:43.003512+00	2025-07-28 16:11:42.955286+00	t	\N
268563a2-72f2-4c6c-af71-024f65e9b23b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	iJS1qqONUchZlJA5grctrqFS_duNUkSUarhrM9aeeJk	172.18.0.1	curl/8.6.0	2025-07-28 08:17:17.128067+00	2025-07-28 08:17:17.128067+00	2025-07-28 16:17:17.077126+00	t	\N
6dda1ced-33c5-402c-a3a5-02a1a57d5481	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	SFI_llry5JskZXNcn4dbGZHce-qb2pN2jJoZMoZdzrI	172.18.0.1	curl/8.6.0	2025-07-28 08:18:48.118994+00	2025-07-28 08:18:48.118994+00	2025-07-28 16:18:48.117408+00	t	\N
0bfd6a00-cf8b-4dae-928a-459c00ee2b95	f5abc444-4a5b-5e6f-7a8b-9c0123456789	2wWsMyeX7U02M7v_J7EaWuophn2ZU6tD_zTZ1ou4SmA	172.18.0.1	curl/8.6.0	2025-07-28 08:20:28.318075+00	2025-07-28 08:20:28.318075+00	2025-07-28 16:20:28.313439+00	t	\N
844bc9cb-693d-437d-b41d-9588f3f240c1	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	MZwuBeXkAQsUpGtJthKpewcffh9III1q16xOL3UaCWc	172.18.0.1	curl/8.6.0	2025-07-28 08:57:15.32035+00	2025-07-28 08:57:15.32035+00	2025-07-28 16:57:15.315251+00	t	\N
dcb55744-0c7b-41df-b6eb-a48392ff8207	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	xnTHmji3MwEXOqDZ-mXiNGGYlOkPC_ajC2Zh6746Tzk	172.18.0.1	curl/8.6.0	2025-07-28 09:20:26.009565+00	2025-07-28 09:20:26.009565+00	2025-07-28 17:20:26.007462+00	t	\N
8b1ee0c2-9c95-49e0-bdfa-4b41eaa0f223	f6abc555-5b6c-6f7a-8b9c-0d123456789a	tQVgIQYwhN3n3FK64C4ZiV9UsnFpGI9qFAqtnNG5RuA	172.18.0.1	curl/8.6.0	2025-07-28 13:15:39.620754+00	2025-07-28 13:15:39.620754+00	2025-07-28 21:15:39.618835+00	t	\N
808c0fa1-5254-4fd7-9cfe-98a850c715c0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	H00b3H-QXK4AIUdYe4ky4JJaiSvIrTIeUzrrjHQcYBA	127.0.0.1	python-requests/2.32.4	2025-07-28 13:26:01.055971+00	2025-07-28 13:26:01.055971+00	2025-07-28 21:26:01.054049+00	t	\N
af9510f4-6b92-4c69-83c1-4567737e2bd6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	n7oDDxFLtoWr-c2WMCFzxco5x2ovhLDKMPP135Yc5f8	127.0.0.1	python-requests/2.32.4	2025-07-28 13:26:28.919944+00	2025-07-28 13:26:28.919944+00	2025-07-28 21:26:28.918188+00	t	\N
5591924d-a4ec-40f8-84e6-6ab1a8058c95	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ExNFmNesJpV6e7zZXFFRVphMU3mNI0Fca6oG9D6eQoI	127.0.0.1	python-requests/2.32.4	2025-07-28 13:27:03.359951+00	2025-07-28 13:27:03.359951+00	2025-07-28 21:27:03.357946+00	t	\N
e26f37ce-cdb6-4057-a832-b0a6ddb17b23	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sA08Z01xyC7-l7CXB6ApCrLCHCUKECU-J2FQRvOzjMU	127.0.0.1	python-requests/2.32.4	2025-07-28 13:34:56.217275+00	2025-07-28 13:34:56.217275+00	2025-07-28 21:34:56.215332+00	t	\N
97e51f12-b418-495f-9ec0-b3c40a6fc8c2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	YrWZMVvGlKCYwUMirw3LkbwwE0_if8urdioiqHl_t7Q	127.0.0.1	python-requests/2.32.4	2025-07-28 13:35:25.911748+00	2025-07-28 13:35:25.911748+00	2025-07-28 21:35:25.910781+00	t	\N
8dd32ce2-321e-4984-b38e-d67df2738138	f6abc555-5b6c-6f7a-8b9c-0d123456789a	R8imLvPfhPTOHZV0Av_VQnkmPxLfhBCRmKchqcJH2bE	172.18.0.1	curl/8.6.0	2025-07-28 14:15:49.641057+00	2025-07-28 14:15:49.641057+00	2025-07-28 22:15:49.638402+00	t	\N
5c4e6f53-12f3-49e0-b268-9d668a9579fe	f6abc555-5b6c-6f7a-8b9c-0d123456789a	HAAJ_m87MP7ben5fZcknJi3ihJ0MyfW6aPqg-G7uTC0	172.18.0.1	curl/8.6.0	2025-07-28 14:20:45.276785+00	2025-07-28 14:20:45.276785+00	2025-07-28 22:20:45.275952+00	t	\N
6b52e849-cf49-41db-89de-60cce66ebefc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	wWuhQMQR7hCQVUIMLDRTFwY-wzeMBW2QAa8LlIR1lvs	172.18.0.1	python-requests/2.32.4	2025-07-28 14:22:39.384263+00	2025-07-28 14:22:39.384263+00	2025-07-28 22:22:39.383552+00	t	\N
058e60a6-4591-4fda-a89a-653c169a505e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1EmGTb5SFr-ZJqJPhs0FA2sqff-Nf7iNwJCTWUxVFK8	172.18.0.1	python-requests/2.32.4	2025-07-28 14:22:56.789241+00	2025-07-28 14:22:56.789241+00	2025-07-28 22:22:56.788542+00	t	\N
a4c9f70f-4178-40c0-b85f-5ba893afc314	f6abc555-5b6c-6f7a-8b9c-0d123456789a	CKi9pRysCaF-Inuds7j-jlWolV0wp0wp7EU070kNe98	172.18.0.1	curl/8.6.0	2025-07-28 14:28:19.639412+00	2025-07-28 14:28:19.639412+00	2025-07-28 22:28:19.638693+00	t	\N
c7137230-c72d-46c9-b1cb-8410b6b229be	f6abc555-5b6c-6f7a-8b9c-0d123456789a	JZMOj1JEEvk7fZOLrj-v_XHv8MUNliIyxgRpnPVVwP0	172.18.0.1	curl/8.6.0	2025-07-28 14:51:32.175201+00	2025-07-28 14:51:32.175201+00	2025-07-28 22:51:32.173098+00	t	\N
2fb1e92c-c294-42db-819f-abf0ba6bf5ca	f6abc555-5b6c-6f7a-8b9c-0d123456789a	p5y3rFY08_kvSdMy0UpAs4Qhcjvoxn2EMF0P5NF_xdg	172.18.0.1	python-requests/2.32.4	2025-07-28 14:51:55.58813+00	2025-07-28 14:51:55.58813+00	2025-07-28 22:51:55.585951+00	t	\N
a7850f23-ad67-4dee-aab8-368e978e1b74	f6abc555-5b6c-6f7a-8b9c-0d123456789a	SgL_N4MEtnwrx0ve-9m3CfbkaW22VMsRsOjOOzsSfD0	172.18.0.1	python-requests/2.32.4	2025-07-28 14:53:11.122181+00	2025-07-28 14:53:11.122181+00	2025-07-28 22:53:11.120165+00	t	\N
f3b3d09b-f04e-45ea-a223-2eeb63caf487	f6abc555-5b6c-6f7a-8b9c-0d123456789a	cDoCmCCggEjjw0idgQ2VawCiR36ft2BgQ4nTv2FKYjk	172.18.0.1	python-requests/2.32.4	2025-07-28 14:56:09.764802+00	2025-07-28 14:56:09.764802+00	2025-07-28 22:56:09.762737+00	t	\N
08a8134c-07c6-4f91-8e93-af9d538b9d58	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1AMq_TxZP_bsNhqkq9LeeFPmspCd1ijp8ZE3iBqb-tc	172.18.0.1	python-requests/2.32.4	2025-07-28 15:07:29.559385+00	2025-07-28 15:07:29.559385+00	2025-07-28 23:07:29.557254+00	t	\N
85535f3c-5fac-4e8b-b0a7-12f5776adbf7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	MZXQ_dO3d8EvfFkzn_XJqURvA5KeSvLOhOdJ_QV5SIw	172.18.0.1	curl/8.6.0	2025-07-28 15:25:35.163649+00	2025-07-28 15:25:35.163649+00	2025-07-28 23:25:35.16269+00	t	\N
ad174e27-7bb4-43c8-a731-8163e7edbbe4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PJgaRnzIMJrBP_OPY6nieDcxkOsFxuewjWP0p3TE7dM	172.18.0.1	curl/8.6.0	2025-07-28 15:26:11.202903+00	2025-07-28 15:26:11.202903+00	2025-07-28 23:26:11.20213+00	t	\N
15ebb889-496b-4feb-900c-3cb1602adf33	f6abc555-5b6c-6f7a-8b9c-0d123456789a	HdCoDM27aSeEfOk-HacqAnPmhgdqJW_tQ9MeFwaAjJ4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-28 16:14:24.424945+00	2025-07-28 16:14:24.424945+00	2025-07-29 00:14:24.422858+00	t	\N
9942cf63-debd-4e7f-a90f-5c9f614f0434	f6abc555-5b6c-6f7a-8b9c-0d123456789a	srEm5zCtSmUIvcaxvTR2A0Lrl-pGmNtK0HQ31YkffJE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-29 17:20:24.583611+00	2025-07-29 17:20:24.583611+00	2025-07-30 01:20:24.581358+00	t	\N
7a42d347-8623-4572-93de-6a5a6d2fc1de	f6abc555-5b6c-6f7a-8b9c-0d123456789a	heJPus47fB0x-EQXL8M8qRN9MglYoJ56aJ5b1aKQBAs	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-29 22:14:37.338759+00	2025-07-29 22:14:37.338759+00	2025-07-30 06:14:37.334257+00	t	\N
eb89fadc-6055-454f-9aa0-b3db0cf6d749	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eTSHhKXeAW9wV_qhwGx3h5GCZfBHVSadz-uR_vNQnqM	172.18.0.1	curl/8.6.0	2025-07-29 22:18:05.748176+00	2025-07-29 22:18:05.748176+00	2025-07-30 06:18:05.746965+00	t	\N
c5aa21ee-3b95-47b3-a4ef-cbaf04fd951b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	hIYPYz_Sl2YZjOYpD-i5H1vMktA26POfQyI8zxZbVLI	172.18.0.1	curl/8.6.0	2025-07-29 22:18:15.202695+00	2025-07-29 22:18:15.202695+00	2025-07-30 06:18:15.201726+00	t	\N
9af3d824-4ef2-4b23-beac-2ebcf7b80d66	f6abc555-5b6c-6f7a-8b9c-0d123456789a	xrykW9RGVFCTQFtsR8jl8AF4IGUqxVDyA1YG3oFb9lc	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-29 22:21:43.603289+00	2025-07-29 22:21:43.603289+00	2025-07-30 06:21:43.602524+00	t	\N
be19eb63-7178-4020-ad09-9f2326a76c0f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	E3nJlf2o7sDnEpZO-InekS3m4rQCo3S7aJC-BljfynA	172.18.0.1	curl/8.6.0	2025-07-29 22:24:57.730146+00	2025-07-29 22:24:57.730146+00	2025-07-30 06:24:57.728979+00	t	\N
6ffcfdfc-19f5-42f5-942c-82b5fa7d16aa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PjlTjMY2dI886W7SjHZD2JqI5Nig7ZDL8ne2XeohRYI	172.18.0.1	curl/8.6.0	2025-07-29 22:25:23.355395+00	2025-07-29 22:25:23.355395+00	2025-07-30 06:25:23.353866+00	t	\N
8dcff95c-bd01-4da9-b596-c4c8b3877ec4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	xoIKYbIg3ykSuwC9lMoNY_IiDMgubCfaCIhF_xIjPHM	172.18.0.1	curl/8.6.0	2025-07-29 22:25:33.972542+00	2025-07-29 22:25:33.972542+00	2025-07-30 06:25:33.971312+00	t	\N
dc872b1c-887a-452a-94f6-620179531d8d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	XPWycaaKT0Ja2gonmCpwN3QHylDMKAqEIMumOestAtg	172.18.0.1	curl/8.6.0	2025-07-29 22:26:51.091219+00	2025-07-29 22:26:51.091219+00	2025-07-30 06:26:51.090358+00	t	\N
28e33a55-8d4f-4a7f-ab6a-3855b6939fb2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8p-KcTn3wln_qRzxV7378n9nlOowd9i9iGoyA_rn-Yg	172.18.0.1	curl/8.6.0	2025-07-29 22:27:42.954604+00	2025-07-29 22:27:42.954604+00	2025-07-30 06:27:42.953519+00	t	\N
d47bb00c-01ad-4f83-9bc3-829f52ba1d36	f6abc555-5b6c-6f7a-8b9c-0d123456789a	CJCPV_Ab1eUQ5E_7iQy9Wbmk1ifEbnBPVO9smR02KdE	172.18.0.1	curl/8.6.0	2025-07-29 22:29:28.277319+00	2025-07-29 22:29:28.277319+00	2025-07-30 06:29:28.276333+00	t	\N
2b3eb97f-d43f-4ad4-bc71-8883d528a8b3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PFhNyuy8wiGNVLhjJq5v4X2l2n20HzLMflmrNdLII8E	172.18.0.1	curl/8.6.0	2025-07-29 22:29:50.316745+00	2025-07-29 22:29:50.316745+00	2025-07-30 06:29:50.315875+00	t	\N
4e84a183-78b0-4d88-b942-40a6177a4f03	f6abc555-5b6c-6f7a-8b9c-0d123456789a	zgpKIcGrnuN0GXqdyT3l1inxZ8aUgODbSJ_HqEwA6sg	172.18.0.1	curl/8.6.0	2025-07-29 22:30:20.828335+00	2025-07-29 22:30:20.828335+00	2025-07-30 06:30:20.827305+00	t	\N
4807c8c3-ac3a-4d62-9d4b-db09e168f7dd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	fQdPQstqX2fw9lw0dah_p7DdcblTFoZBZkDnZAqpA24	172.18.0.1	curl/8.6.0	2025-07-29 22:31:01.753927+00	2025-07-29 22:31:01.753927+00	2025-07-30 06:31:01.753325+00	t	\N
6ec425ae-5c88-40fb-aed1-9e3591ddfcf9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-I5ElinKlKbMhFQHJCnA1koKRTedpn0ObskQca8iFt0	172.18.0.1	curl/8.6.0	2025-07-29 22:34:40.85092+00	2025-07-29 22:34:40.85092+00	2025-07-30 06:34:40.850008+00	t	\N
dce4b8e7-a3d3-4cfd-a2ef-58bbc9b6a02d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	fHmk2aQ9n14GMVVuwCXMYzNIvhSDRB6rBGUH9DYZIew	172.18.0.1	curl/8.6.0	2025-07-29 22:35:04.540105+00	2025-07-29 22:35:04.540105+00	2025-07-30 06:35:04.539222+00	t	\N
512a0588-73c7-49b2-aefe-6ecbb7d0b74f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	qf7la2WpvoPLf83a1pW8xhBDFFFF_6eFrZ40jKhPpzo	172.18.0.1	curl/8.6.0	2025-07-29 22:27:00.988349+00	2025-07-29 22:27:00.988349+00	2025-07-30 06:27:00.985341+00	t	\N
78bcd8d4-4f73-4f7b-9f11-265e4a86acdd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	RQykh3zIZOfjx71Xfv62mg4F8yCxDB352q6OsbEAn_o	172.18.0.1	curl/8.6.0	2025-07-29 22:27:14.164659+00	2025-07-29 22:27:14.164659+00	2025-07-30 06:27:14.163827+00	t	\N
61f91c9e-37b6-49a4-b339-2fbb0e60d5a9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GBCHO0yc_V5wyzYor3NHOvzuPqooBC_LegS8j4Ed3BY	172.18.0.1	curl/8.6.0	2025-07-29 22:27:30.30535+00	2025-07-29 22:27:30.30535+00	2025-07-30 06:27:30.30454+00	t	\N
40fa9e71-f983-419b-805e-124d197a584f	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	l-NtRRjP51vgfF-pMXxPyGBesisr-p4_pfL52Zrbhx8	172.18.0.1	curl/8.6.0	2025-07-29 22:36:47.48878+00	2025-07-29 22:36:47.48878+00	2025-07-30 06:36:47.487962+00	t	\N
51bf4f9b-3dc1-4f39-976b-3ab8daf4083d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	j1iNYyI40TF6rB2MJ4jfzL-v2I0dQS7RHAg91BDebvY	172.18.0.1	curl/8.6.0	2025-07-29 22:28:27.636572+00	2025-07-29 22:28:27.636572+00	2025-07-30 06:28:27.635079+00	t	\N
807b57d5-39da-4420-a62e-bf74febe9073	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Z7EJEz5wsS6Qg6bwb045Q0ihjhGzKohDJTJ35rTx-ig	172.18.0.1	curl/8.6.0	2025-07-29 22:31:29.438565+00	2025-07-29 22:31:29.438565+00	2025-07-30 06:31:29.437517+00	t	\N
f054f2ae-9b1f-41c9-954c-fa4edbdc1591	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sMd81DIO1dTiiBVctPbpQxF1lXHAUd4hzLMQmfUPuFw	172.18.0.1	curl/8.6.0	2025-07-29 22:33:47.900608+00	2025-07-29 22:33:47.900608+00	2025-07-30 06:33:47.899856+00	t	\N
7a8cc557-5186-4f39-9496-fd114a71dc99	f6abc555-5b6c-6f7a-8b9c-0d123456789a	HiSM3JuSVyAXT6vwihVzPYzCpKgEkXY7QeL4zB0AmYE	172.18.0.1	curl/8.6.0	2025-07-29 22:34:15.789421+00	2025-07-29 22:34:15.789421+00	2025-07-30 06:34:15.788548+00	t	\N
c188579e-6d1a-4597-a327-b5357e3812a1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	B8BULtIDNjFShm6jJyL6VagRRX9_qzuoBX0X98SuGoM	172.18.0.1	curl/8.6.0	2025-07-29 22:35:27.040938+00	2025-07-29 22:35:27.040938+00	2025-07-30 06:35:27.040032+00	t	\N
fee4df73-dfb7-42c5-b2ca-df2419a92cfa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ZeixwjI8t4_IaOV4jzJH3U1zTzjTXL8hdIHQ7r9fRok	172.18.0.1	curl/8.6.0	2025-07-29 22:35:48.823142+00	2025-07-29 22:35:48.823142+00	2025-07-30 06:35:48.82237+00	t	\N
a323682e-ea96-4948-9e79-25289bf085b8	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	JvlGFKOwDm4SwCnJ8OcLvAcsW-jowWAgPi3_mYDGT1E	172.18.0.1	curl/8.6.0	2025-07-29 22:37:10.322814+00	2025-07-29 22:37:10.322814+00	2025-07-30 06:37:10.322303+00	t	\N
67d3ab51-1424-414c-ae89-b48008af216c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	14BmKIhHh-aNdNjZ4bW4jTYLb2UMXkL1TnJOp3lGOlw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-29 22:42:47.352868+00	2025-07-29 22:42:47.352868+00	2025-07-30 06:42:47.351567+00	t	\N
e493b7b1-8ec4-48c5-9550-0ef40266aab8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4KBIq-2-a5TfjDFL1qWvSKofSdi7ysT5zUwfAgT56ek	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 09:14:50.085556+00	2025-07-30 09:14:50.085556+00	2025-07-30 17:14:50.081749+00	t	\N
02219d14-e992-4781-adaf-53d1348e687c	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	P4OEzxNBr7UQURnG1ypWkkogapigvLE3BtUrf-X__qg	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-30 10:08:28.805088+00	2025-07-30 10:08:28.805088+00	2025-07-30 18:08:28.803314+00	t	\N
763640b7-68d2-484a-869b-386cca66f643	f6abc555-5b6c-6f7a-8b9c-0d123456789a	e2z8IFN6mA_owQVUtct-M3Ok7LeSsyByy0tprx298Pc	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-30 10:12:24.787398+00	2025-07-30 10:12:24.787398+00	2025-07-30 18:12:24.786521+00	t	\N
571059ba-db9a-4030-9ccd-4dfc2250f2b0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	qSR310joSSVuQPedRDB8lABEbjIVFnpZs4d1iMc77Gc	172.18.0.1	curl/8.6.0	2025-07-30 14:49:34.724752+00	2025-07-30 14:49:34.724752+00	2025-07-30 22:49:34.722588+00	t	\N
d25d5ac9-96ec-457e-b2b8-4fbf9bccbd80	f6abc555-5b6c-6f7a-8b9c-0d123456789a	p554JDiG-fmm5R3wn0VfMMzNAOepUF0BBD-uOv2jagI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 15:00:15.038896+00	2025-07-30 15:00:15.038896+00	2025-07-30 23:00:15.038271+00	t	\N
07f67daf-2e7e-4a61-8bc7-d4de9a8988fd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	c0mQZ3iZTFTH1i9u5xK60-mrEIkxqcTbYrcR540myNQ	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-30 15:01:30.350195+00	2025-07-30 15:01:30.350195+00	2025-07-30 23:01:30.349674+00	t	\N
0c024839-4380-4ec8-be05-be3319be2fcd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	7KWdZ7fsAcZUTspEMfPAKFrQsMsOQt-TkLw1kh2QM1E	127.0.0.1	python-requests/2.32.4	2025-07-30 15:50:00.910101+00	2025-07-30 15:50:00.910101+00	2025-07-30 23:50:00.907935+00	t	\N
52e7ac5b-5d6a-403a-944f-bae023790456	f6abc555-5b6c-6f7a-8b9c-0d123456789a	cLbipT-5Qd_CBnyZtSW6yStQaFy6-Y4VndufVVu3FJQ	127.0.0.1	python-requests/2.32.4	2025-07-30 15:50:41.006675+00	2025-07-30 15:50:41.006675+00	2025-07-30 23:50:41.004854+00	t	\N
3bda4025-84d5-473f-be5f-0ae3051fe0f1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2MCRf6JmhpVs6WbS-CKpaljW2IZhZS9Pt94OCUdowCY	172.18.0.1	python-requests/2.32.4	2025-07-30 15:56:33.714493+00	2025-07-30 15:56:33.714493+00	2025-07-30 23:56:33.713154+00	t	\N
8ec3a74a-21a1-41d2-a698-3a9c36bbf904	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ifghWjxEhjPXnDY0uuTmDR7q8rWxVSz1X6xEEw36kvY	127.0.0.1	python-requests/2.32.4	2025-07-30 16:42:01.607428+00	2025-07-30 16:42:01.607428+00	2025-07-31 00:42:01.604803+00	t	\N
47432c56-c571-4d61-a15b-0a46c5f656d8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Rb0PK7-MnYbW06lT6rXFZcz2hCr4JPAwkqkzn1QTcTM	127.0.0.1	python-requests/2.32.4	2025-07-30 16:48:07.833146+00	2025-07-30 16:48:07.833146+00	2025-07-31 00:48:07.831686+00	t	\N
7acb07c6-8346-487c-9bb2-2e4419995e4f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kwQbfffkn5Ih1I7cB6yA6Cy5cRTZXhnpWso8ACri7uA	127.0.0.1	python-requests/2.32.4	2025-07-30 16:49:04.0872+00	2025-07-30 16:49:04.0872+00	2025-07-31 00:49:04.08534+00	t	\N
441f7ea3-7b13-43ac-9709-ac176c89b3bd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	TaK155H_gdeUjRgykiu4osnvOWclp9rubqPBwubgzD0	127.0.0.1	python-requests/2.32.4	2025-07-30 16:49:19.522889+00	2025-07-30 16:49:19.522889+00	2025-07-31 00:49:19.522298+00	t	\N
baa0868e-8e04-4568-b5ac-cd6823b37757	f6abc555-5b6c-6f7a-8b9c-0d123456789a	OMSiPoSOM3KhFdsOgaWFDxqdYyCKS9XRyf9r5n6NFL8	127.0.0.1	python-requests/2.32.4	2025-07-30 16:50:17.050039+00	2025-07-30 16:50:17.050039+00	2025-07-31 00:50:17.049506+00	t	\N
609526b8-34c2-4f3d-a15f-5dedf6263a6b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Madj2WldBJQrHnIE-5a9MEoi2wyjzMsjsKz082aZb58	127.0.0.1	python-requests/2.32.4	2025-07-30 16:50:52.454982+00	2025-07-30 16:50:52.454982+00	2025-07-31 00:50:52.454367+00	t	\N
fb8c194a-5464-4fa2-8605-cb1082ed0788	f6abc555-5b6c-6f7a-8b9c-0d123456789a	7BRXYbBYP8-CDqmaUv1FZCsmvoJBxXmcXmi4Mwg_tuI	127.0.0.1	python-requests/2.32.4	2025-07-30 16:55:43.007088+00	2025-07-30 16:55:43.007088+00	2025-07-31 00:55:43.005567+00	t	\N
ab5b72ec-f16c-4f8d-8963-0107c212b370	f6abc555-5b6c-6f7a-8b9c-0d123456789a	MCQ4T5P3estSSpHbebf1MjxamS0emRmPfqeXFS-qr7M	127.0.0.1	python-requests/2.32.4	2025-07-30 16:55:43.332382+00	2025-07-30 16:55:43.332382+00	2025-07-31 00:55:43.331761+00	t	\N
fcb23e59-bd23-4829-b175-1c02c163844d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	KvGgucmvUy3oAf8WtZX0se33JO6UFiYeqfJG0AgmCQM	127.0.0.1	python-requests/2.32.4	2025-07-30 16:55:43.790376+00	2025-07-30 16:55:43.790376+00	2025-07-31 00:55:43.789473+00	t	\N
6b84e5e6-1fa1-43a6-b869-ec1ad60eaafe	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EBXWQe104NdDHEYVCH1MYa8_wf5sfizF2Q-YOP5t6BE	127.0.0.1	python-requests/2.32.4	2025-07-30 16:55:44.069682+00	2025-07-30 16:55:44.069682+00	2025-07-31 00:55:44.069159+00	t	\N
9924ded5-f2d4-454a-8e63-70041a1be71e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	neeKtzZl9PtVVbkZCMuBKO53pp_h7ODUd8Biynaa1Lo	127.0.0.1	python-requests/2.32.4	2025-07-30 17:03:17.239768+00	2025-07-30 17:03:17.239768+00	2025-07-31 01:03:17.239094+00	t	\N
389aa22d-d1db-49c4-bf36-f8abe859172a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Eq6PhbBMoZd1tw4hnPqC5fD6_B8n3pnLx4GkLBbHR2s	127.0.0.1	python-requests/2.32.4	2025-07-30 17:03:32.778885+00	2025-07-30 17:03:32.778885+00	2025-07-31 01:03:32.777989+00	t	\N
a60af406-3e9a-47bd-8ac0-7dd50d4824c9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_Bwv8Fwsb8OJiPSn-kPu13aZAVJdcQVTiExa8n-K8y0	127.0.0.1	python-requests/2.32.4	2025-07-30 17:03:58.114801+00	2025-07-30 17:03:58.114801+00	2025-07-31 01:03:58.113343+00	t	\N
2738f1f7-7be0-4416-a534-6dd77dbba23e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	zIjOE4GxMKRjzk7Ynxl7-IM020f7Lk9tpNY3WlqNqbA	127.0.0.1	python-requests/2.32.4	2025-07-30 17:05:01.19524+00	2025-07-30 17:05:01.19524+00	2025-07-31 01:05:01.194384+00	t	\N
93c6b553-1fdf-4a27-8cd1-c8ae320a5cb6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1mt6sHIpqcylFvN2MvLFF6DdODvgMguHhaqJzp_946c	127.0.0.1	python-requests/2.32.4	2025-07-30 17:05:22.777932+00	2025-07-30 17:05:22.777932+00	2025-07-31 01:05:22.777198+00	t	\N
f122f051-a9a8-4e30-8cff-82acb69203b7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eJvtYQEN49AMiW8CsxD-i2DysJNKoIhg9HyQjDZ4aFU	127.0.0.1	python-requests/2.32.4	2025-07-30 17:06:35.31752+00	2025-07-30 17:06:35.31752+00	2025-07-31 01:06:35.315373+00	t	\N
8e3bae95-ef97-4f3d-bcde-517243e0e563	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5MtaPPrYtKGXJVpTsIgsUl-6HiLvlybuTCH-gPA3-5Y	127.0.0.1	python-requests/2.32.4	2025-07-30 17:07:08.524634+00	2025-07-30 17:07:08.524634+00	2025-07-31 01:07:08.520767+00	t	\N
16c078f8-a0d6-4050-ac87-ce2b1a70479e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	nBRO_4WITx7L6K1JAuNU4IPQhJJHKAZlROL2snZzK20	127.0.0.1	python-requests/2.32.4	2025-07-30 17:11:29.473987+00	2025-07-30 17:11:29.473987+00	2025-07-31 01:11:29.466667+00	t	\N
45e4cbfd-b279-489a-ba87-0b121bbcc7b8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	i8bbsAMvjd9sDamjNgFmeWVnv3-hADJykqT6vkhbzmI	127.0.0.1	python-requests/2.32.4	2025-07-30 17:11:37.015822+00	2025-07-30 17:11:37.015822+00	2025-07-31 01:11:37.014518+00	t	\N
f14bc517-84b8-4dfb-a23c-972e06d56394	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Mpcb2Kl7G9XvLDUr5dsSjYRIlpQhKfKpKIJkxmYgK3o	172.18.0.1	curl/8.6.0	2025-07-30 17:23:00.275273+00	2025-07-30 17:23:00.275273+00	2025-07-31 01:23:00.272851+00	t	\N
be061fe6-fba1-4042-9869-b4af08462e81	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Ty1y0yD_-401PWczlZ-MRz0izwlin49bqtBR6vszfyA	172.18.0.1	curl/8.6.0	2025-07-30 17:23:23.112727+00	2025-07-30 17:23:23.112727+00	2025-07-31 01:23:23.11185+00	t	\N
7bc3a0e3-27c8-4481-a070-905be182f86c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	orI1uFen8JPTX1bHrcwVf6zoygKxswQBTK0GLeYDeMM	172.18.0.1	curl/8.6.0	2025-07-30 17:27:50.035102+00	2025-07-30 17:27:50.035102+00	2025-07-31 01:27:50.03339+00	t	\N
1f5e799e-30bd-4190-9819-d46a9e365659	f6abc555-5b6c-6f7a-8b9c-0d123456789a	9G8EVjufb8mj_ofP0V1_Bn3MB6SMWFvBhyGXzY8rJc4	172.18.0.1	curl/8.6.0	2025-07-30 17:27:58.109549+00	2025-07-30 17:27:58.109549+00	2025-07-31 01:27:58.10888+00	t	\N
72ff932d-d1c2-496a-8b32-989f2f8c5300	f6abc555-5b6c-6f7a-8b9c-0d123456789a	KCSokE4i6k-KvL5G2muRF_AnQ7rDvjOLy6L8c3e6IN4	172.18.0.1	curl/8.6.0	2025-07-30 17:29:03.37042+00	2025-07-30 17:29:03.37042+00	2025-07-31 01:29:03.36755+00	t	\N
efd47be2-681d-4d85-9592-fa3d98b86651	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EWpWUfBCqKI3t-PI9h4CA7ORk2jk2BF4tiObDVfvD0Q	172.18.0.1	curl/8.6.0	2025-07-30 17:29:11.050517+00	2025-07-30 17:29:11.050517+00	2025-07-31 01:29:11.049446+00	t	\N
15013910-7756-42e4-be30-a784069ed5cd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	g1nioVjgHNpidxXq42A7mgV39adqPUaCrESrA09UPyM	172.18.0.1	curl/8.6.0	2025-07-30 17:30:31.202313+00	2025-07-30 17:30:31.202313+00	2025-07-31 01:30:31.198516+00	t	\N
191e4f7d-386b-41d1-936d-109b194b3c3e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pkUqWFVREin3KnITLbXQzwuOIQjiOUgqQSvK0JQfQhI	172.18.0.1	curl/8.6.0	2025-07-30 17:31:24.823571+00	2025-07-30 17:31:24.823571+00	2025-07-31 01:31:24.819051+00	t	\N
5d8795b5-2417-41e8-9a75-74fcbd02364f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eogfjsiGaQtLmyg-6LzchMGjrOt7ppPnLpL4Ah736dk	172.18.0.1	curl/8.6.0	2025-07-30 17:33:57.812968+00	2025-07-30 17:33:57.812968+00	2025-07-31 01:33:57.812289+00	t	\N
3cfa312a-a094-4df4-9e34-54d7ccd99080	f6abc555-5b6c-6f7a-8b9c-0d123456789a	meQ1q1KCUjrAEc6HgFXH53V-fU1YDZBkiBWoy6E6dfQ	127.0.0.1	python-requests/2.32.4	2025-07-30 17:40:55.59694+00	2025-07-30 17:40:55.59694+00	2025-07-31 01:40:55.596145+00	t	\N
5ea7578c-898c-4395-8a25-da7b7e3d4a37	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_1X6rSBd-UEJo_9tZxLnzd6tFJ-5V6uDV5hVvWmFFhQ	127.0.0.1	python-requests/2.32.4	2025-07-30 17:41:42.160229+00	2025-07-30 17:41:42.160229+00	2025-07-31 01:41:42.157966+00	t	\N
7dada31e-203a-4260-aeaa-c940f68ed885	f6abc555-5b6c-6f7a-8b9c-0d123456789a	UixwfN4wgSmuiwSKTn7GqVKzUooJwbIMRZ07QjCryBs	127.0.0.1	python-requests/2.32.4	2025-07-30 17:42:00.152402+00	2025-07-30 17:42:00.152402+00	2025-07-31 01:42:00.151255+00	t	\N
af358fd3-809b-4ce1-a8ea-c85a0482b425	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Df--DjM46aiH1AK0gOUnP0nTJ2jTUsN26Tz8kWIJIyQ	127.0.0.1	python-requests/2.32.4	2025-07-30 17:42:11.431332+00	2025-07-30 17:42:11.431332+00	2025-07-31 01:42:11.43006+00	t	\N
dde7f6ff-2e8f-4f57-aa42-e6e083d1bac9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4IqNtPNIKxyTJpYLi6gNu-UPwvMfJ6vJI2M9QHZMMoQ	127.0.0.1	python-requests/2.32.4	2025-07-30 17:42:22.708157+00	2025-07-30 17:42:22.708157+00	2025-07-31 01:42:22.707173+00	t	\N
300753c2-1a21-45a9-bd95-43f2ba84020d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	akli_rhedJy1CWdbPJba0CaW6Ca1b-HH8lrqmttyBws	127.0.0.1	python-requests/2.32.4	2025-07-30 17:43:06.606714+00	2025-07-30 17:43:06.606714+00	2025-07-31 01:43:06.605723+00	t	\N
e6cb2d9c-ab12-499a-9668-dc3b102ca348	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pME_EjQ7P-t6KTYTxI6pWowq1BRTgHxnSVEoOWMaZjE	127.0.0.1	python-requests/2.32.4	2025-07-30 17:43:51.785355+00	2025-07-30 17:43:51.785355+00	2025-07-31 01:43:51.782336+00	t	\N
f4234239-5f3d-4d14-9719-158c38b5d8e6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_AZjWZNcVLKVwcHIk63uKu9cM2RLwOMExeRh6_MKPr0	127.0.0.1	python-requests/2.32.4	2025-07-30 17:45:19.534574+00	2025-07-30 17:45:19.534574+00	2025-07-31 01:45:19.52425+00	t	\N
c7674c7b-6f01-489c-b2b7-672c74f87264	f6abc555-5b6c-6f7a-8b9c-0d123456789a	nwc8inFbzNRg87WwqkHV1id9EEAtwotDc1wuDc7Zc9k	127.0.0.1	python-requests/2.32.4	2025-07-30 17:45:52.408386+00	2025-07-30 17:45:52.408386+00	2025-07-31 01:45:52.406829+00	t	\N
4aaa1969-378e-4333-9aca-253a35f49e59	f6abc555-5b6c-6f7a-8b9c-0d123456789a	hiKSmEvXNz6WMacRBwwd2MwJjkfEr5DQKPgjNUVhIVg	127.0.0.1	python-requests/2.32.4	2025-07-30 17:46:25.501089+00	2025-07-30 17:46:25.501089+00	2025-07-31 01:46:25.497139+00	t	\N
04c406b6-3d2f-4cfa-bedd-e7d98e41c98f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	bRvSyoI-qqZvaTWNtjCF-DQ9DK1qari6NizeF3F4Lsg	127.0.0.1	python-requests/2.32.4	2025-07-30 17:47:15.771979+00	2025-07-30 17:47:15.771979+00	2025-07-31 01:47:15.768779+00	t	\N
5c0caa37-f29a-44b4-aeaf-807fb312ee93	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5I5z7vekVWNLNWRB0dtQpUpRrXIWuzr5h3wSGvXNzPg	172.18.0.1	python-requests/2.32.4	2025-07-30 18:01:16.767172+00	2025-07-30 18:01:16.767172+00	2025-07-31 02:01:16.764341+00	t	\N
7ba72b3f-e101-4f99-9cd4-4d2798c2b975	f6abc555-5b6c-6f7a-8b9c-0d123456789a	XJgIuMc0FHa9_TOV6dCbVWNO2GPLssgCSV-yXmIsWgM	172.18.0.1	python-requests/2.32.4	2025-07-30 18:01:17.343458+00	2025-07-30 18:01:17.343458+00	2025-07-31 02:01:17.342108+00	t	\N
b6d1913d-162c-4360-b7b4-3a211fef2ef3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PW_2HJwzOHXrQey807FiNyPfEZtKtV1ur7Xqq-9hGbk	172.18.0.1	python-requests/2.32.4	2025-07-30 18:01:17.870835+00	2025-07-30 18:01:17.870835+00	2025-07-31 02:01:17.869975+00	t	\N
6e9cef68-b6aa-4ac9-9a49-54716d61bbc3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	0Vmr8NYILP6g8uxruafQdqEeIOgFQB37gq5gCk4_etw	172.18.0.1	python-requests/2.32.4	2025-07-30 18:02:27.510584+00	2025-07-30 18:02:27.510584+00	2025-07-31 02:02:27.506688+00	t	\N
f2116776-8100-48df-8e19-175496afdb2a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	56ZDaXYNlET5dGYZ9pOW7A6fOH4lV4DxtVW-6bdV7D4	172.18.0.1	python-requests/2.32.4	2025-07-30 18:02:28.171622+00	2025-07-30 18:02:28.171622+00	2025-07-31 02:02:28.17029+00	t	\N
393f63d0-d6e3-471c-9bc4-734dbd8a9981	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pE5M9FIdAIWPYSRKlfx060VpYRn3ZkBac92J9EmO7W0	172.18.0.1	python-requests/2.32.4	2025-07-30 18:02:28.746891+00	2025-07-30 18:02:28.746891+00	2025-07-31 02:02:28.745115+00	t	\N
63e5a7b5-5d3a-48a7-be36-3e99e83c5f64	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Y_8dSxSQkGb8YSqiXGTbdoYX1G3alNG-lvbOCjQMgAQ	172.18.0.1	python-requests/2.32.4	2025-07-30 18:03:10.745378+00	2025-07-30 18:03:10.745378+00	2025-07-31 02:03:10.743261+00	t	\N
8cb4d75d-b5a6-4c65-a398-8ed2bfe346da	f6abc555-5b6c-6f7a-8b9c-0d123456789a	q-5EghbMLoAzWJJukpoPXet7ZGgSgAfHYobO5gv1NFI	172.18.0.1	python-requests/2.32.4	2025-07-30 18:03:11.201907+00	2025-07-30 18:03:11.201907+00	2025-07-31 02:03:11.201206+00	t	\N
8fea5949-e5b6-42a5-873c-bc98f00df8a5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1mJi6KtMI-ZpLPv56ELNNxujTK_HrApp6ZU5JrwDEc4	172.18.0.1	python-requests/2.32.4	2025-07-30 18:03:11.61705+00	2025-07-30 18:03:11.61705+00	2025-07-31 02:03:11.616437+00	t	\N
b06d8e33-ee24-4106-a21e-0fd7c90c92f4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8HOiFTPS5O3MVl7Y0w4C0orS9vhaXtHTbpT_wuiGncg	172.18.0.1	python-requests/2.32.4	2025-07-30 18:04:47.683104+00	2025-07-30 18:04:47.683104+00	2025-07-31 02:04:47.680488+00	t	\N
8f047290-80ab-4365-b1b8-c4629ebeb63e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Tg3o5TfkWLCDfvKo5pGCUGQ10rBGhUzWEsf1EeYcblQ	172.18.0.1	python-requests/2.32.4	2025-07-30 18:04:48.278876+00	2025-07-30 18:04:48.278876+00	2025-07-31 02:04:48.277667+00	t	\N
b9f1f930-e96b-4d48-bce3-b2502df63ec7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	S9ychD_7n3MR8axyfz9d4vfLMiy_1FIv46Nr-Uy0Giw	172.18.0.1	python-requests/2.32.4	2025-07-30 18:04:48.895971+00	2025-07-30 18:04:48.895971+00	2025-07-31 02:04:48.895151+00	t	\N
f7ebba1c-3bf5-4ac6-9383-df6795843bf9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	fhQOZXMspmRklLh8Oj91A7psFvdnm_umOljwZ-nFtS0	172.18.0.1	curl/8.6.0	2025-07-30 18:05:10.029063+00	2025-07-30 18:05:10.029063+00	2025-07-31 02:05:10.028354+00	t	\N
dee82eaa-78cd-4618-b22c-fc742aa235eb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	tSKFmnUgjTz2LN_fi00D6DbhuWyTBUcyN5diwL3paIc	172.18.0.1	python-requests/2.32.4	2025-07-30 18:07:15.663001+00	2025-07-30 18:07:15.663001+00	2025-07-31 02:07:15.661015+00	t	\N
f40a4bb4-bfb9-4614-83ca-76b80e725da7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Lv64k6bZ5UIhcLSwNPRh-SWplSZ-8uFFzi0eZS4qNDo	172.18.0.1	python-requests/2.32.4	2025-07-30 18:07:16.143588+00	2025-07-30 18:07:16.143588+00	2025-07-31 02:07:16.142846+00	t	\N
ce881a02-6b1c-4d16-968b-4dd30073799f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	U-AZQhYkJubzOVJIiDZf05wnjgu7WrHneWqvc-D6osQ	172.18.0.1	python-requests/2.32.4	2025-07-30 18:07:16.528333+00	2025-07-30 18:07:16.528333+00	2025-07-31 02:07:16.527529+00	t	\N
bfdc37a2-0b5b-48f5-9e57-79939814cfa4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	w2Z-aiYhdBdhsqpegY5J3Jx7bW7aWMRR0CIZZQPKibQ	172.18.0.1	curl/8.6.0	2025-07-30 18:13:04.312241+00	2025-07-30 18:13:04.312241+00	2025-07-31 02:13:04.311537+00	t	\N
f23ae7e6-bea0-4b86-a97e-21d4ea9936da	f6abc555-5b6c-6f7a-8b9c-0d123456789a	91rbz6jqh4LRdeajpomHmpz5fswhl4_bYUmEU1CrPTI	172.18.0.1	curl/8.6.0	2025-07-30 18:14:55.179706+00	2025-07-30 18:14:55.179706+00	2025-07-31 02:14:55.178025+00	t	\N
5e9ed0ea-c4f9-4de5-b4d5-17fe0550fe5e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	TTEDCg5Lk0NsairnZrI7CW-JUnEUGqVCyzlW2Dbma74	172.18.0.1	curl/8.6.0	2025-07-30 18:21:26.070678+00	2025-07-30 18:21:26.070678+00	2025-07-31 02:21:26.0697+00	t	\N
80c6bf59-6a05-461f-8b1b-793eea150afb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	nwuJkQrACjnTv5g9iUoBlwvGU0JYaTZUojrYF9CxZDg	172.18.0.1	curl/8.6.0	2025-07-30 18:23:19.283958+00	2025-07-30 18:23:19.283958+00	2025-07-31 02:23:19.283347+00	t	\N
caba6f74-33d7-437c-bda0-cf283e34641c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-ZKnXyaTU8vLVcc6ouXXVsUankjrtaiiUqm52TMu5cY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 21:21:40.474569+00	2025-07-30 21:21:40.474569+00	2025-07-31 05:21:40.473575+00	t	\N
20c54724-ecad-4c59-9f49-ac4f506897ee	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sOE0YFZagqp1b2yd_v5BYifvNM62xdVHx-Kd52qTiDw	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-30 21:22:15.85981+00	2025-07-30 21:22:15.85981+00	2025-07-31 05:22:15.859143+00	t	\N
aec981ee-da0f-414e-a4a8-757196981326	f6abc555-5b6c-6f7a-8b9c-0d123456789a	s4ngjPAYeKNBrEQKF_BopHNNSD_-dMPJEmyhIgyIXHo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 21:45:06.918533+00	2025-07-30 21:45:06.918533+00	2025-07-31 05:45:06.917912+00	t	\N
5d21493b-8b95-4f72-b2cd-726da939185a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	i5YyK2xIqXh_SPRSQG5LLpFrIy3teArMS7DE3olVncE	172.18.0.1	curl/8.6.0	2025-07-30 21:53:36.576822+00	2025-07-30 21:53:36.576822+00	2025-07-31 05:53:36.575989+00	t	\N
1e882d2b-f6f9-4864-8cf8-4c20a3669046	f6abc555-5b6c-6f7a-8b9c-0d123456789a	CcY2p1Q__mFejtpEgHbzMMEksDUssEGO-qZ5uohNf8M	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 21:56:34.075464+00	2025-07-30 21:56:34.075464+00	2025-07-31 05:56:34.074793+00	t	\N
00a74ff9-5209-424b-afe7-c214fdb79e2b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	cZGCVp_QFIVw_NMTXWfEU9URQnDbpot4C0OpiaapmO4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 21:57:56.429035+00	2025-07-30 21:57:56.429035+00	2025-07-31 05:57:56.4284+00	t	\N
cc07427b-9a03-4c8a-b7d3-d8c5fccbbb23	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5KlNZSAIgtgmWS0UcdZpjm_l_nhHTf8ICC2ebfPAZcw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 22:10:59.798112+00	2025-07-30 22:10:59.798112+00	2025-07-31 06:10:59.797373+00	t	\N
f9cb3e0a-faeb-4015-b44b-27ff12ec7c16	f6abc555-5b6c-6f7a-8b9c-0d123456789a	UEl8K1udokXE7xitkrcyaWc50FyOAPfshuycWjYnrDM	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 22:17:27.797665+00	2025-07-30 22:17:27.797665+00	2025-07-31 06:17:27.796575+00	t	\N
dab2d4c9-a28b-49ab-9c64-90f84a0c2312	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	Vck__yVvZrW4SkYhvW60T3G8nVbkQrlbzclx-qKJpOk	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-30 22:21:21.652409+00	2025-07-30 22:21:21.652409+00	2025-07-31 06:21:21.651808+00	t	\N
5c0c0be0-a250-42f6-849e-75f6f61e9982	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Y5qvD1NzB-dH0wLwn6Xrd4XMk--wRcRpuOFYQwoJO70	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 22:46:23.218071+00	2025-07-30 22:46:23.218071+00	2025-07-31 06:46:23.216399+00	t	\N
9fa61140-cdfa-45e4-8766-c9b5553da936	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sDmGTDcBqQ1xl27DDgfeRrNktw2e2ZN5_xDNSz8OAQg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 22:47:22.944846+00	2025-07-30 22:47:22.944846+00	2025-07-31 06:47:22.944303+00	t	\N
c9510eca-39c7-4795-9f20-1466c885884a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EVOu9iHu4MWTVrSiaJFXCqz2JHXH1xX3rI0UoSN5Zew	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 22:53:50.964232+00	2025-07-30 22:53:50.964232+00	2025-07-31 06:53:50.963237+00	t	\N
70c6e781-8afb-47ad-9919-151d4bc9bb27	f6abc555-5b6c-6f7a-8b9c-0d123456789a	NU0eX2f6erToI3Gdr-kHWDFW2Mhaq2TixhuSHwfkSOs	172.18.0.1	curl/8.6.0	2025-07-30 23:12:17.850219+00	2025-07-30 23:12:17.850219+00	2025-07-31 07:12:17.848201+00	t	\N
df08e1b4-946d-4aa5-b82e-fdafa42623ec	f6abc555-5b6c-6f7a-8b9c-0d123456789a	RwuzGXS46AYsNm5a9F3Cr_k85R1QiRjolb636sOVKwc	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 23:43:15.020135+00	2025-07-30 23:43:15.020135+00	2025-07-31 07:43:15.018307+00	t	\N
60d1449a-c8e7-497b-af72-1e4b66e4f04d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4tD3TJYUb8lVIijFtQr4VKNoqNn4ZlGoc6jccaGyFgc	172.18.0.1	curl/8.6.0	2025-07-31 08:23:59.102693+00	2025-07-31 08:23:59.102693+00	2025-07-31 16:23:59.10125+00	t	\N
603814e7-5bfb-462d-8902-086c19ccf1ef	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-ah7zS_O_3vBk9egpJmXqULbaS6Ca8Y3vN_bDU4bssM	172.18.0.1	python-requests/2.32.4	2025-07-31 08:26:26.900873+00	2025-07-31 08:26:26.900873+00	2025-07-31 16:26:26.900279+00	t	\N
b1c64a6e-36b5-4949-95d2-e935a4ae9338	f6abc555-5b6c-6f7a-8b9c-0d123456789a	O_4OlNKB6X4F0rd5D-fruvNN2vTkeVLTw-xfTfL0x-o	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-30 23:46:03.203854+00	2025-07-30 23:46:03.203854+00	2025-07-31 07:46:03.202327+00	t	\N
183e8c0d-12cf-44e2-99ad-6f5a87b5a00e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	v-SvR3e-n8YyT8LN7Fybmm7seBnwXuLWfTgjUgrvJZk	172.18.0.1	python-requests/2.32.4	2025-07-31 08:27:36.75905+00	2025-07-31 08:27:36.75905+00	2025-07-31 16:27:36.757187+00	t	\N
96445b11-c1d4-429b-9e22-fa584486b227	f6abc555-5b6c-6f7a-8b9c-0d123456789a	RxMvHaDHpQSLpcadAq2wwpHkjIwHHOHpLT3OOZPj958	172.18.0.1	python-requests/2.32.4	2025-07-31 08:28:15.901166+00	2025-07-31 08:28:15.901166+00	2025-07-31 16:28:15.900112+00	t	\N
2597ed56-1404-486d-9230-8954ce75a6b2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	TfGtFXxTt0gagn_giDMKlSzeW_KpIv0umyBC18VoUZs	172.18.0.1	python-requests/2.32.4	2025-07-31 08:28:36.055255+00	2025-07-31 08:28:36.055255+00	2025-07-31 16:28:36.054699+00	t	\N
79111dc2-418a-42fb-bd4a-529f200d7bf3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	odOFeanEFOJuvA_AtwxbgcMp20Y7mhBntqlSFeabolA	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 09:57:58.6122+00	2025-07-31 09:57:58.6122+00	2025-07-31 17:57:58.611549+00	t	\N
f6cdfd1f-58ce-4f89-b3ff-4dd4a5287fbc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Jr1fFLLN-4bOE0N4FR_mp3j5KTXh59mN6XKMRD5SZ3s	172.18.0.1	curl/8.6.0	2025-07-31 10:07:15.738532+00	2025-07-31 10:07:15.738532+00	2025-07-31 18:07:15.735001+00	t	\N
20d9b5c1-4f89-481f-a0a1-a3626d579296	f6abc555-5b6c-6f7a-8b9c-0d123456789a	7StDnr0BigJDJ69irdeoab54AzEksBfb0Jn4jCIa0b4	127.0.0.1	python-requests/2.32.4	2025-07-31 10:32:18.215562+00	2025-07-31 10:32:18.215562+00	2025-07-31 18:32:18.213404+00	t	\N
71642f98-c926-43f0-a79a-c45b81932342	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ByaKOG_Fstq4yAGCIPDXOm17oIS4v7WCN9pUjfzj98M	127.0.0.1	python-requests/2.32.4	2025-07-31 10:35:39.849394+00	2025-07-31 10:35:39.849394+00	2025-07-31 18:35:39.847922+00	t	\N
0d49679c-4ba7-4478-a3ac-44232b82ac8b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	WDiJoQRafw7pMGJFBZQw_MqjKDvjmws63HHn6sIdmLg	127.0.0.1	python-requests/2.32.4	2025-07-31 10:36:05.451934+00	2025-07-31 10:36:05.451934+00	2025-07-31 18:36:05.448198+00	t	\N
30b19d14-fd26-4eca-b3f1-568d0c8fc5a1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	CgXKRqgzCziWV3r0EkRbcSv6iz9noOVjNZy8aUX0klk	127.0.0.1	python-requests/2.32.4	2025-07-31 10:37:13.137691+00	2025-07-31 10:37:13.137691+00	2025-07-31 18:37:13.135942+00	t	\N
395bd32e-04e0-437e-82a4-be8dfc898d2a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	0bjYDRjK_ZoFi2dio7ryoBCBSBVJX5QN0q58a8BrV6M	127.0.0.1	python-requests/2.32.4	2025-07-31 10:38:34.516599+00	2025-07-31 10:38:34.516599+00	2025-07-31 18:38:34.514949+00	t	\N
ae94117e-7c88-4f28-ae8c-a9e2456a1df0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kh4IfJhpN0sVsQpChlTTn9MKjD8ROglbXnpa8dz6fhE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 10:45:23.130844+00	2025-07-31 10:45:23.130844+00	2025-07-31 18:45:23.130127+00	t	\N
1f28d28b-08ba-4f79-99eb-b67585e13cc6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	NPpof3M5yncb57_m5QNBEHZSv3RUfYi2X5aWH7-FLg4	172.18.0.1	python-requests/2.32.4	2025-07-31 11:21:53.974033+00	2025-07-31 11:21:53.974033+00	2025-07-31 19:21:53.972369+00	t	\N
0af21f70-f304-43d6-bb47-3b6a3de38913	f6abc555-5b6c-6f7a-8b9c-0d123456789a	UfA3pHyTLiZ6yA8v0XgW09lureeBi2mXdfVUWIDhytQ	172.18.0.1	python-requests/2.32.4	2025-07-31 11:24:15.763376+00	2025-07-31 11:24:15.763376+00	2025-07-31 19:24:15.760384+00	t	\N
ab1d7d67-e498-4ef7-a21c-0adc8ddbe05a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	DYY0XdILAu8v7wwObbwyZDOOtEHoO42ZSRX7LatMpFM	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:08.503684+00	2025-07-31 11:46:08.503684+00	2025-07-31 19:46:08.501978+00	t	\N
dd2d7104-3e84-49fe-966d-d7a87c3605eb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	P58hYBgS_Zl9ysxrBlgP7WVJ8HpzkfcZ7CuxW5FhjiA	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:08.758707+00	2025-07-31 11:46:08.758707+00	2025-07-31 19:46:08.758129+00	t	\N
32e33bf1-bff2-40c0-8559-5f13ba174b41	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8VsoChYSvEUBNtuc4b6DQVjgW4UWeKWRKX1yvVbpcws	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:08.990307+00	2025-07-31 11:46:08.990307+00	2025-07-31 19:46:08.989854+00	t	\N
a0ee5f9e-9a55-400a-990c-7a71212684b5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GGqWCiwj3b1Ya5Vl8jLkpZ4cNH15JLscaOfNT4dF_g4	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:09.271709+00	2025-07-31 11:46:09.271709+00	2025-07-31 19:46:09.270587+00	t	\N
264e23e2-92b8-4cf4-ae73-5a881ccd38fc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pwgCmdrQFVpBvxaCkpy0T0UfAEunb7CKZBmtQoxKrS4	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:09.543787+00	2025-07-31 11:46:09.543787+00	2025-07-31 19:46:09.543298+00	t	\N
448cfea8-0a74-42f0-a572-4dae8e7a6a41	f6abc555-5b6c-6f7a-8b9c-0d123456789a	v07N_qADlbNklqDseZa0DUgTn8IUFcU8qNfdqUhiuvk	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:09.766167+00	2025-07-31 11:46:09.766167+00	2025-07-31 19:46:09.765507+00	t	\N
4a9cd482-e5a3-4460-96e3-1c0ef83132a2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	d5iR2KHBtS9uXDgcsmLrkCSjoHNGlZnX9GuORKyAD_8	127.0.0.1	python-requests/2.32.4	2025-07-31 11:46:09.998604+00	2025-07-31 11:46:09.998604+00	2025-07-31 19:46:09.99805+00	t	\N
ad8080d2-c5e5-459e-b7af-eb65054d85fd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	e7We4f37GmQrHmS1n7ru8JILMAY-sIIe2LW5a-jq_QE	172.18.0.1	curl/8.6.0	2025-07-31 11:50:40.310118+00	2025-07-31 11:50:40.310118+00	2025-07-31 19:50:40.307556+00	t	\N
8c7e65c2-c59f-4f04-abd3-5ea3570e9a69	f6abc555-5b6c-6f7a-8b9c-0d123456789a	b0m1neN6WjzfoLi54wP6LXMbJ5YhbjyYkyNt4Ggly-o	172.18.0.1	curl/8.6.0	2025-07-31 11:51:22.550214+00	2025-07-31 11:51:22.550214+00	2025-07-31 19:51:22.549636+00	t	\N
87c29cc5-bb11-4c24-b9c4-b0bd019796b8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sDPYcUjkPGzqjkpTjfsOXgUuxADZc8M2GRHviVasuXU	172.18.0.1	curl/8.6.0	2025-07-31 11:51:32.09309+00	2025-07-31 11:51:32.09309+00	2025-07-31 19:51:32.091912+00	t	\N
f951ad47-cb19-4f48-8826-8d3a120e4ff1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	BPu5SEEAkNVC5ohwOaJ6jUeFhQ2dGbZJ42oMWJtCWS8	172.18.0.1	curl/8.6.0	2025-07-31 11:52:32.648544+00	2025-07-31 11:52:32.648544+00	2025-07-31 19:52:32.646868+00	t	\N
a7e80868-3bb0-4105-88ec-5cccbf0c421f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ok1GqMm5uheEteNN1Y5ZLECLJuV9aReYvWxpNZ_lfb8	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:39.132228+00	2025-07-31 11:52:39.132228+00	2025-07-31 19:52:39.131767+00	t	\N
e40a0743-ced6-4f96-9df7-6010cf3a0a38	f6abc555-5b6c-6f7a-8b9c-0d123456789a	v8EG3nM68DyTbVYUQAsvdCpDK2mQpz_p3wGyhdloo38	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:39.360521+00	2025-07-31 11:52:39.360521+00	2025-07-31 19:52:39.360056+00	t	\N
6dc98f87-8ebf-41ee-ad9b-c7df0d323f76	f6abc555-5b6c-6f7a-8b9c-0d123456789a	KGeOk4qi0pktEAYKTUj0PT32O9JEybm3sgnU9GebxOk	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:39.592005+00	2025-07-31 11:52:39.592005+00	2025-07-31 19:52:39.591545+00	t	\N
39407275-7d4f-4813-be7e-8cfb3205e14d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	jlnugUHDJ3oToz85yl3W0jokUhyNuCedztMev3YhpBw	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:39.880464+00	2025-07-31 11:52:39.880464+00	2025-07-31 19:52:39.87985+00	t	\N
597252d0-bc91-48cf-95e1-a41009a32e07	f6abc555-5b6c-6f7a-8b9c-0d123456789a	bU5DPi8O2IIkM6iJz08rxdf-ZWYzn35keKxt0SWJn-w	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:40.116712+00	2025-07-31 11:52:40.116712+00	2025-07-31 19:52:40.116227+00	t	\N
0c361c16-5061-4e02-a970-1b5699a518f8	f6abc555-5b6c-6f7a-8b9c-0d123456789a	KmZyVbF_YvDOrSwkmKEQ3zkCWpF7-cxgWy_5FUTlVH4	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:40.354396+00	2025-07-31 11:52:40.354396+00	2025-07-31 19:52:40.3538+00	t	\N
dbe0e242-cccc-494b-b779-b9c23728d3a4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	blmznnWpp16cZfFMjsn0TxZbx8ji-m_PHfGvfOGE25U	127.0.0.1	python-requests/2.32.4	2025-07-31 11:52:40.589885+00	2025-07-31 11:52:40.589885+00	2025-07-31 19:52:40.589316+00	t	\N
318cc7b9-7dcb-4794-a1ce-85af7cca8b6c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_Viltibr5rjUcOzwFeu8R3ClYix0GcFEt1401EZmhP4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 13:23:30.227869+00	2025-07-31 13:23:30.227869+00	2025-07-31 21:23:30.225675+00	t	\N
c684639a-16fc-48f2-8493-573e00d07554	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eJpTqDL0Vvwra7TtkP5F6MksKtY2pid1m56T-uFvo-w	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 13:24:24.29991+00	2025-07-31 13:24:24.29991+00	2025-07-31 21:24:24.299256+00	t	\N
24bc14ab-f5db-4040-8d3e-f2744b13ec2b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	toc8McVGxFXpN4SQM37FA716rJsRb_L5FGdxJOgBLuw	127.0.0.1	python-requests/2.32.4	2025-07-31 13:25:59.668209+00	2025-07-31 13:25:59.668209+00	2025-07-31 21:25:59.667543+00	t	\N
ff58be0d-b242-4c6f-9237-88513d124b41	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Mla0m6L9xGoj4H-LFwbikg0CDp8NoGiPPGm97vkJlxw	127.0.0.1	python-requests/2.32.4	2025-07-31 13:30:22.403872+00	2025-07-31 13:30:22.403872+00	2025-07-31 21:30:22.400979+00	t	\N
e9948b9d-6ea9-4f66-b2ee-d437c5d595eb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	YUnDvDhkINRxldF0g-vg6qT5ujr24x0bo4qpqVOWZGU	127.0.0.1	python-requests/2.32.4	2025-07-31 13:31:29.717848+00	2025-07-31 13:31:29.717848+00	2025-07-31 21:31:29.71506+00	t	\N
050d9c92-f479-418f-a052-504dc5974e3a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	RiBminunJ5Ctipyu3n6Ajka9xhNU3JULkJTA6Mg7V1c	127.0.0.1	python-requests/2.32.4	2025-07-31 13:32:24.664716+00	2025-07-31 13:32:24.664716+00	2025-07-31 21:32:24.661013+00	t	\N
6def7b07-e9d8-43fa-b841-6727c2650ecb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	QcFi1O-_ICGEbMzl-_OdrnWC7F0uVO8mVZ7QXmJtsug	127.0.0.1	python-requests/2.32.4	2025-07-31 13:32:47.619421+00	2025-07-31 13:32:47.619421+00	2025-07-31 21:32:47.615417+00	t	\N
2f22d6e1-c1f8-4abd-8f0c-2e85f94089fd	f6abc555-5b6c-6f7a-8b9c-0d123456789a	wymvnVwnmAsE7jhuyRC1CHfQofNqjBH_gmz0N2jfjQI	127.0.0.1	python-requests/2.32.4	2025-07-31 13:33:42.014715+00	2025-07-31 13:33:42.014715+00	2025-07-31 21:33:42.01244+00	t	\N
4ce25640-1203-4c7a-993c-15a3509b655c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	u656UcP19wzcTkyt4quJvLzh_97QcfotboJJi-GdRGk	127.0.0.1	python-requests/2.32.4	2025-07-31 15:04:41.246199+00	2025-07-31 15:04:41.246199+00	2025-07-31 23:04:41.23674+00	t	\N
058d236b-614b-4a70-8495-9c510a83849a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	xjbd9NdjFF02y691OMxbMIrsQ4DpZ3fKmFAJ_3iHxnQ	127.0.0.1	python-requests/2.32.4	2025-07-31 15:05:52.355348+00	2025-07-31 15:05:52.355348+00	2025-07-31 23:05:52.354012+00	t	\N
d5a0946d-525f-4025-885e-eb86d5ccb492	f6abc555-5b6c-6f7a-8b9c-0d123456789a	sk0G8xn9Wu9Gwzbn8yBudm3OrIYUM8QpREwyYeOhf6I	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 15:06:25.497034+00	2025-07-31 15:06:25.497034+00	2025-07-31 23:06:25.496428+00	t	\N
e33ab433-b0f9-4a4a-8853-ed9e5e6fe0a1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ikl6-toMr-j6NP0Tk3oniKMHPO6lGYfC1Zmvkd2vtJ4	127.0.0.1	python-requests/2.32.4	2025-07-31 15:13:51.484694+00	2025-07-31 15:13:51.484694+00	2025-07-31 23:13:51.484077+00	t	\N
ad75d49d-857a-448e-b0c2-ce0a856b7f66	f6abc555-5b6c-6f7a-8b9c-0d123456789a	0V8VLqUrSeJranv1fdx7O9kh4dsTHZFT63837XjMEbk	127.0.0.1	python-requests/2.32.4	2025-07-31 15:16:59.6125+00	2025-07-31 15:16:59.6125+00	2025-07-31 23:16:59.611799+00	t	\N
ff39cedc-36e0-45f7-9197-5969a57eeda5	f6abc555-5b6c-6f7a-8b9c-0d123456789a	xi7RRA5uIGoRaFwidmXmjYuka5-mTs5__NTCSvwwPOY	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 15:27:13.762307+00	2025-07-31 15:27:13.762307+00	2025-07-31 23:27:13.761657+00	t	\N
0663cc09-5e0d-482d-b339-52546171e9c2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5nuOQ4MjFkVmnz5kLZQdEAeL0VQkl2JXlHAu7jCmhtg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 15:08:42.918162+00	2025-07-31 15:08:42.918162+00	2025-07-31 23:08:42.917518+00	t	\N
0af11995-7c62-4db0-aeef-28214b26906b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	67KGk4KxWzVwHxfN3RCZIuCbedcxd00_VyINu9VucHg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 15:40:38.691059+00	2025-07-31 15:40:38.691059+00	2025-07-31 23:40:38.690267+00	t	\N
29895da1-0269-4d37-8472-76591a8b3654	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5Fa7Ox5DD7bmBS_WT6eKcauNNgO5I_uGn4jVa6dtzm4	127.0.0.1	python-requests/2.32.4	2025-07-31 15:47:01.770581+00	2025-07-31 15:47:01.770581+00	2025-07-31 23:47:01.769983+00	t	\N
92d60b2d-36b8-42b5-bb90-072d0c530a5c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	o7ShUAf2lgwTQb-09cLtRdxBlxz2-X7KSD1n3Sb5Drk	127.0.0.1	python-requests/2.32.4	2025-07-31 16:00:22.65089+00	2025-07-31 16:00:22.65089+00	2025-08-01 00:00:22.650131+00	t	\N
23f8c7cf-1768-4a43-8e03-042d032b1f26	f6abc555-5b6c-6f7a-8b9c-0d123456789a	L5eWwt9JoIdDPYIFVNUf1kZGzdYHUZrgAfeFqMaeN88	127.0.0.1	python-requests/2.32.4	2025-07-31 16:00:47.75871+00	2025-07-31 16:00:47.75871+00	2025-08-01 00:00:47.757994+00	t	\N
5fe8773c-3044-4fe2-8cb6-a6b5791035a2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	2wqME3zx60EVn4yGQipUBQPkLWR_6Pi5N6JBmaKyF1s	127.0.0.1	python-requests/2.32.4	2025-07-31 16:01:54.660157+00	2025-07-31 16:01:54.660157+00	2025-08-01 00:01:54.658134+00	t	\N
b97af1a0-48ac-41a0-9c39-d0ea986ce797	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kWfwdUObBtPBG91D2nAU1S8AAie41Y4TYoYuBauKbFY	127.0.0.1	python-requests/2.32.4	2025-07-31 16:03:13.891107+00	2025-07-31 16:03:13.891107+00	2025-08-01 00:03:13.889892+00	t	\N
c9e279c6-7c63-41cb-9bdc-834e3b897e27	f6abc555-5b6c-6f7a-8b9c-0d123456789a	pOBIotb4xOVnc6a_WcmHmt_FfAyVX2HpXikZLSRXZXw	127.0.0.1	python-requests/2.32.4	2025-07-31 16:05:34.494852+00	2025-07-31 16:05:34.494852+00	2025-08-01 00:05:34.493734+00	t	\N
1f727848-6ab3-4ee6-8c9b-57b308dd5e58	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8Q-bB4mPjfIxjZnNvid4GRXf1cRDslNmpD39am8HhX8	127.0.0.1	python-requests/2.32.4	2025-07-31 16:14:24.795222+00	2025-07-31 16:14:24.795222+00	2025-08-01 00:14:24.794725+00	t	\N
0f89500d-5fcb-4928-9985-25cf8f80675d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ca-Pg3gVu1RHeNuaoTZCxre4XybLji4TwsiJnMj1ujo	127.0.0.1	python-requests/2.32.4	2025-07-31 16:18:12.519872+00	2025-07-31 16:18:12.519872+00	2025-08-01 00:18:12.517956+00	t	\N
4bc50866-1307-46c8-a00d-ef9ab86d1d4d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	7YVH-S6IGjefyd1IDlKwa13K7iFiZkYR4O0jD3BMa8w	127.0.0.1	python-requests/2.32.4	2025-07-31 16:19:49.560967+00	2025-07-31 16:19:49.560967+00	2025-08-01 00:19:49.55713+00	t	\N
4e1d7656-196e-474c-a9f9-5f2f761c3b08	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EDNN_VFgKRJpr7lYBZRimJLz80f0eVwoEndmRLoICTQ	127.0.0.1	python-requests/2.32.4	2025-07-31 16:21:26.724009+00	2025-07-31 16:21:26.724009+00	2025-08-01 00:21:26.723102+00	t	\N
fd5d5de6-5642-45d9-9173-5058ebca9eaf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	yQihYTsDNSI8COnVSfUjEFmEU15_gqS1raa4Zef0F1w	127.0.0.1	python-requests/2.32.4	2025-07-31 16:34:07.081247+00	2025-07-31 16:34:07.081247+00	2025-08-01 00:34:07.07988+00	t	\N
6f99b5d7-2f81-4aec-8455-72261a5778b3	f6abc555-5b6c-6f7a-8b9c-0d123456789a	wuNDAqrUQ6uPr8NOZXb8AFLUeqoAd9Bfl8--TR7UIN8	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-07-31 16:40:23.846507+00	2025-07-31 16:40:23.846507+00	2025-08-01 00:40:23.845564+00	t	\N
3a1e6706-c1c8-43cd-8816-6171efa2b49f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ov-bRDXAOZk6wao0iXhw_M0kzxM7JU1JIJFHVXTk4HM	127.0.0.1	python-requests/2.32.4	2025-07-31 16:46:24.652446+00	2025-07-31 16:46:24.652446+00	2025-08-01 00:46:24.651697+00	t	\N
59ab2f1d-2f2f-446d-9274-52cc07d68931	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	3r0LZyLXGmR8pj8IjUNIJ9ugIstKnGaa3yPOzVoTrmE	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-31 17:03:22.095098+00	2025-07-31 17:03:22.095098+00	2025-08-01 01:03:22.094417+00	t	\N
bdf56565-2f3a-4a2c-b320-0778cbd19a3e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	XWeC6QckfPl4GiPMWuqBkDhEd--Ar8nK8a8Fo7_cjos	172.18.0.1	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36	2025-07-31 17:03:56.291018+00	2025-07-31 17:03:56.291018+00	2025-08-01 01:03:56.290175+00	t	\N
21d6896d-9282-4614-89c6-524b5ecb9f31	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Zv-m2buuhHgmH_3_aLFZeIWzHdvyuuk9UzxTZ4XkXqg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-03 21:58:37.360972+00	2025-08-03 21:58:37.360972+00	2025-08-04 05:58:37.358962+00	t	\N
9dc6ff6c-6a2d-4b93-8350-da12e8dc4f54	f6abc555-5b6c-6f7a-8b9c-0d123456789a	L6xhSf_v9iEGR7meRlv0TSwANXB-uw2Tsgm6FBvY79k	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-03 22:12:17.518896+00	2025-08-03 22:12:17.518896+00	2025-08-04 06:12:17.513375+00	t	\N
72793d1b-f049-4ecd-a7cc-38289a439d28	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Llmaa-l6xthHdGqnNJdWY8NEDz_Ta3StP5U9wsuELY0	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-03 22:12:25.519145+00	2025-08-03 22:12:25.519145+00	2025-08-04 06:12:25.51767+00	t	\N
17165f11-8972-4956-89ea-b9427e79dcfa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	W2Np30bz3-LtYNNRYL607ldXHw7lSXK5ytpSWyeGJWE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:30:46.226182+00	2025-08-05 22:30:46.226182+00	2025-08-06 06:30:46.223995+00	t	\N
434595c8-202d-4978-a118-d82b10295c8a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	I3um2eTTZvcdaciJ2iE54agNJFH7fIpmATon0kQdcf8	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:50:34.092358+00	2025-08-05 22:50:34.092358+00	2025-08-06 06:50:34.089309+00	t	\N
82367100-973b-45ff-9d79-8ee321d79271	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4mNNQFj0DtNwnIHn_bm0qvsJmOL48BTUj7ilLyvC75w	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:51:09.162079+00	2025-08-05 22:51:09.162079+00	2025-08-06 06:51:09.161114+00	t	\N
e65e23d5-5026-4004-81a9-a1826b03f8cf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	v2Id-dGCghV7PB-PDeNbRS4KMGGATC0vpl3LYxXgu_c	172.18.0.1	curl/8.6.0	2025-08-05 23:13:46.813364+00	2025-08-05 23:13:46.813364+00	2025-08-06 07:13:46.807955+00	t	\N
17825c70-3560-42fe-b8fa-da28731f3af9	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	5PjwnfqVhkkNl_y70jlDUC7IHTOCGt46Zm_no9oeNtE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:20:08.567289+00	2025-08-05 23:20:08.567289+00	2025-08-06 07:20:08.565208+00	t	\N
5eba61da-ab0d-45a8-ba9e-5bf326b1d5cf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eOCJ-nesRUuFUuX2cjw7NxtyCzF6HsK0fJ3lhkzTSik	172.18.0.1	curl/8.6.0	2025-08-06 13:04:10.024976+00	2025-08-06 13:04:10.024976+00	2025-08-06 21:04:10.024299+00	t	\N
74f06695-7127-487e-87fc-e40a2bb45feb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	SOA7an4EDb1n9AYq3CpCFqi7V1-ADnp7jXQdP7wlHuU	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-08-19 11:37:22.210328+00	2025-08-19 11:37:22.210328+00	2025-08-19 19:37:22.208914+00	t	\N
d5a5f40d-f4a0-401f-9727-172b90e6cf86	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Y2hiFbxM_A9NnhdL4HmrdeJIqZEsQS5BBYQjsIAcMrg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-08-23 14:57:32.965645+00	2025-08-23 14:57:32.965645+00	2025-08-23 22:57:32.964242+00	t	\N
263c9f63-8034-4b77-8c7e-f56dd48a4f2f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Z_oNcfJ2uSXFLFEhMW6GVdtWe8yc2ulREtOxXL4I4dU	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-08-24 11:46:44.671497+00	2025-08-24 11:46:44.671497+00	2025-08-24 19:46:44.669772+00	t	\N
3c76f437-5b78-4586-b8fe-b891e841beb9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	OXkx5VeqYhCAS7hD7zeejooanfEQPszOD8aIHJ4ZPu4	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-08-29 16:23:00.755754+00	2025-08-29 16:23:00.755754+00	2025-08-30 00:23:00.750103+00	t	\N
7a5975b7-476c-4094-a94f-b0d84bb5b3fa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	3t2IKbbRqja47pMPDT7Z_VRaID2kSOkV7Vp-JMnl19I	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-06 15:13:23.01812+00	2025-09-06 15:13:23.01812+00	2025-09-06 23:13:23.011577+00	t	\N
e935c600-9c8e-4eb9-b81b-4246dabb50f6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Tqt-0WVammJBJtGgVSWX2QJ8ArrJ8Gp0om-8wk_I7sQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-03 22:45:01.58754+00	2025-08-03 22:45:01.58754+00	2025-08-04 06:45:01.583938+00	t	\N
bb96b71c-480b-4e89-9bea-ca6dbc8588c4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	CPWgbHJMUmg8vUP06TXJDtnwujjHJ5NUwOK99D2LARw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 09:49:20.273094+00	2025-08-05 09:49:20.273094+00	2025-08-05 17:49:20.265325+00	t	\N
85bb0951-0f82-4626-8e28-3d73f8b6e39b	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	K03ksTZRBucGOKDIVQbcnQNeqsNpiU4gnvs4d6vwVWI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:35:25.147955+00	2025-08-05 22:35:25.147955+00	2025-08-06 06:35:25.145148+00	t	\N
d01679ac-9a3d-4cf9-b9a7-d31cef8be16f	f5abc444-4a5b-5e6f-7a8b-9c0123456789	C6PLyW8zpli2TUZmAyv7xcTfe6qaKKiaNX6Ia0AEcLo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:36:01.816082+00	2025-08-05 22:36:01.816082+00	2025-08-06 06:36:01.815233+00	t	\N
0c850cdc-7e50-4cd6-8441-4acde2806af2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	k8Y-Mw0wRWFVaTx_v2gYn_O54upOzcs6DxL5OZQmuE0	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:50:49.813942+00	2025-08-05 22:50:49.813942+00	2025-08-06 06:50:49.813216+00	t	\N
ff1bac5d-c167-4d11-a130-e294fcdf9dac	f6abc555-5b6c-6f7a-8b9c-0d123456789a	WcM4sBQGaW-TtKRH9mSP7UdMFlcj_QLfyqHetdtKs6c	172.18.0.1	curl/8.6.0	2025-08-05 23:15:33.750225+00	2025-08-05 23:15:33.750225+00	2025-08-06 07:15:33.748044+00	t	\N
49ae2682-db25-480c-856f-d175a75b1a90	f6abc555-5b6c-6f7a-8b9c-0d123456789a	AXPZlQrLDi0kqWrFMsP6iHeFRJcUDETAAFLvJlieVdo	172.18.0.1	curl/8.6.0	2025-08-05 23:32:23.425848+00	2025-08-05 23:32:23.425848+00	2025-08-06 07:32:23.423175+00	t	\N
6bc1a8b3-763e-42cc-8909-175bfd4a9620	f6abc555-5b6c-6f7a-8b9c-0d123456789a	I9cS1aEHRERMJBcCQ17z5T25GJNkmQ5dE_mQSlLlpo8	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-06 12:49:43.192232+00	2025-08-06 12:49:43.192232+00	2025-08-06 20:49:43.190901+00	t	\N
4223cfe6-1e9e-4c8e-ade2-8d97042a7620	f6abc555-5b6c-6f7a-8b9c-0d123456789a	V-DBNbX9X8zDYBBIYmvt8tyg1ycbhFsoHfl4iC9atq4	172.18.0.1	curl/8.6.0	2025-08-06 13:07:55.711612+00	2025-08-06 13:07:55.711612+00	2025-08-06 21:07:55.709489+00	t	\N
e8fb2829-4bff-4902-acda-915ac57dc63e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	fitbCqF4ftX-qin4ZDEe_NfzgTPxtvxT34InJizug7o	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-07 13:05:49.716539+00	2025-08-07 13:05:49.716539+00	2025-08-07 21:05:49.712391+00	t	\N
3039865b-550f-419a-a1c6-ee5c9f10c990	f6abc555-5b6c-6f7a-8b9c-0d123456789a	-Nr7ZKYVfq0FdabP-MdPVQb2iZGgy6OAR3KoUk3-AIg	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:24:21.096126+00	2025-08-05 22:24:21.096126+00	2025-08-06 06:24:21.092246+00	t	\N
df619a14-daeb-4cc3-b837-7c18a8f85e6d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	EadEux9CL8Vh9EVNb9w3O2WnuS42CXtGPelGy-6GMvE	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:26:19.773876+00	2025-08-05 22:26:19.773876+00	2025-08-06 06:26:19.772984+00	t	\N
4c703bde-f002-452a-9ca6-ba5cad177cd1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	MaeCK1vmVtFjx5pmOVM5Oil-eDkeqeHrHHJnq1htm2M	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:58:44.357499+00	2025-08-05 22:58:44.357499+00	2025-08-06 06:58:44.355224+00	t	\N
717296b2-c0dc-4920-8d58-42e14d2a560b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5XWRFDG1BapX61MwDJrKne9K9NWscJV0AYh61Xt4ekw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:05:11.736117+00	2025-08-05 23:05:11.736117+00	2025-08-06 07:05:11.734298+00	t	\N
cd7a9f32-ad50-43e8-82ca-1c72d7c9080a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	QRWcDjpgyyYD7szWC9rsvDWvGKY6ISPD9CNIfxk-Rp8	172.18.0.1	curl/8.6.0	2025-08-05 23:11:07.841826+00	2025-08-05 23:11:07.841826+00	2025-08-06 07:11:07.840946+00	t	\N
6a754a40-74ca-4f9e-b04a-c6be75d72b37	f6abc555-5b6c-6f7a-8b9c-0d123456789a	MAG_-shYWNeM4T3GiYCAM_0wf-Rnr-PaFz-3eVLFqL0	172.18.0.1	curl/8.6.0	2025-08-05 23:17:07.640276+00	2025-08-05 23:17:07.640276+00	2025-08-06 07:17:07.637325+00	t	\N
8b4d9502-161a-45e2-9fe0-7a4dc6ccd4f8	f5abc444-4a5b-5e6f-7a8b-9c0123456789	0i7cFdA2DDgEP38zXVTEQcn-iFs5x7KNgL7SbCApjRI	172.18.0.1	curl/8.6.0	2025-08-05 23:17:33.840431+00	2025-08-05 23:17:33.840431+00	2025-08-06 07:17:33.839378+00	t	\N
6db7b1db-32ba-48a5-bd5d-f1753ef6f240	f5abc444-4a5b-5e6f-7a8b-9c0123456789	xcBqhRnohMkgwaz2s3HmY_hBM5mykRyyDpbDCc-bZTw	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:17:51.818603+00	2025-08-05 23:17:51.818603+00	2025-08-06 07:17:51.817041+00	t	\N
a796310b-69ae-4e9f-8e1b-4ccb544df7b4	f6abc555-5b6c-6f7a-8b9c-0d123456789a	actW5ZuoI_YcDPAk1SqvmbrCmO05GY2DZfxv5Qsdg3s	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-06 12:47:52.617692+00	2025-08-06 12:47:52.617692+00	2025-08-06 20:47:52.614342+00	t	\N
1c23c67d-5348-4a92-9d83-c39ccc25b2e1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PYOaEsIbGr52BrRFdrDgxa3EHv7ah1Wvlgklq9b-IkM	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-06 13:17:22.383175+00	2025-08-06 13:17:22.383175+00	2025-08-06 21:17:22.381734+00	t	\N
b77dacab-aec0-4d5e-a226-1e3388504285	f6abc555-5b6c-6f7a-8b9c-0d123456789a	j-KU9w7SBPWylflJ4GiDqb6tzMm6ML5q__Q063ljGXM	172.18.0.1	curl/8.6.0	2025-08-06 13:23:54.01231+00	2025-08-06 13:23:54.01231+00	2025-08-06 21:23:54.011406+00	t	\N
e29044d5-1cdd-4e2b-8091-befd68019718	f6abc555-5b6c-6f7a-8b9c-0d123456789a	K9X3kpsAY4_HVgHvtKO-fqycad-SrCcirhUcms_sNjo	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:27:37.374977+00	2025-08-05 22:27:37.374977+00	2025-08-06 06:27:37.374111+00	t	\N
26c6bc8d-434c-479a-87cf-621896e6ff8b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	3MatzElbv-F_TLI8Qy5ABtYBInP-vfukaMzZkap5FfI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:28:12.368725+00	2025-08-05 22:28:12.368725+00	2025-08-06 06:28:12.367829+00	t	\N
46cc91ae-f62a-4c11-8164-56afe72b7340	f6abc555-5b6c-6f7a-8b9c-0d123456789a	GuhS8xS98ianI2hWeupLweBm9-VKfazLu7dalhL83UI	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:28:22.320438+00	2025-08-05 22:28:22.320438+00	2025-08-06 06:28:22.319588+00	t	\N
db97ec95-94e4-4f3e-9d97-883791ef9a66	f6abc555-5b6c-6f7a-8b9c-0d123456789a	y1owkI67Flqqo8BdWtYCH_m0FmvOnZNmHEfr8Dvh_f8	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 22:58:53.489708+00	2025-08-05 22:58:53.489708+00	2025-08-06 06:58:53.488648+00	t	\N
aab8a162-ae34-450f-8f44-96cc307448b0	f5abc444-4a5b-5e6f-7a8b-9c0123456789	-Ruj77SqzoDvrcE2a1gjSo23XJE02072nSH2XfP_lVQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:05:40.136161+00	2025-08-05 23:05:40.136161+00	2025-08-06 07:05:40.134609+00	t	\N
a0a982ac-266c-409e-a61d-65f68603c711	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	o4pSi4AtK-OXscLwkqaBRWrkOi7ryAANqP8e3nGggWc	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:07:02.763964+00	2025-08-05 23:07:02.763964+00	2025-08-06 07:07:02.762861+00	t	\N
ebdff448-e69a-4307-9959-adbaa138b93d	f5abc444-4a5b-5e6f-7a8b-9c0123456789	Bt7VdT6Z2HpFbYlXyI-ATbd9DawjIbd9l6gYavnyrRM	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:07:23.732733+00	2025-08-05 23:07:23.732733+00	2025-08-06 07:07:23.731125+00	t	\N
80e9bd07-ef5a-4877-801b-d03f63763ae9	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ZDxhSuag4m71sIHGm8A8z_KdtlTO3aMvt7QwzhZQlAQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:18:38.478481+00	2025-08-05 23:18:38.478481+00	2025-08-06 07:18:38.476834+00	t	\N
bbf7ddef-0413-4598-9c6e-97ec96cac90a	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	4P2128lZ4RQ9yYNMxWRRFdNEkw7odDVl5D-y4VIddkM	172.18.0.1	curl/8.6.0	2025-08-05 23:19:21.825795+00	2025-08-05 23:19:21.825795+00	2025-08-06 07:19:21.823813+00	t	\N
0f14d6ec-a548-4beb-a16a-8c3c79c6c363	f5abc444-4a5b-5e6f-7a8b-9c0123456789	xDoHHxShxkCy3xLf9vw9pXplm-nzMXjCQLSO-yzmuQ8	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-05 23:20:29.131691+00	2025-08-05 23:20:29.131691+00	2025-08-06 07:20:29.129549+00	t	\N
b4587a72-281b-4ad9-939f-824beb4092a1	f5abc444-4a5b-5e6f-7a8b-9c0123456789	iFpGt7f8q5YFyWH6uQM-RCvR2HetJydGxSIzQWKl-KQ	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36	2025-08-06 12:48:07.148549+00	2025-08-06 12:48:07.148549+00	2025-08-06 20:48:07.14716+00	t	\N
e23e46b1-c4e5-409a-9c16-8cb6cca3855c	f6abc555-5b6c-6f7a-8b9c-0d123456789a	RxADZ4CYaIJv-oyAg2-SVwyGqxT03modB3OC-cjxY4o	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-10 22:00:54.954143+00	2025-09-10 22:00:54.954143+00	2025-09-11 06:00:54.950828+00	t	\N
0f8694f4-7dc0-461e-be14-7a398c4fcf66	f6abc555-5b6c-6f7a-8b9c-0d123456789a	Z1vBfnM26D_FbCFXTxNQiINWc2VQEX36hS-RfljoXxs	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-10 23:32:49.580514+00	2025-09-10 23:32:49.580514+00	2025-09-11 07:32:49.57731+00	t	\N
3ede80e9-ba76-4ad9-9699-697483a6f4be	f6abc555-5b6c-6f7a-8b9c-0d123456789a	HfzYFUrDYCCqJjHai6hlbsnt7QNvAvdfPnp602CQ9fA	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-10 23:33:34.190452+00	2025-09-10 23:33:34.190452+00	2025-09-11 07:33:34.18819+00	t	\N
451fb585-9b83-4cb2-b39a-4f925c71f4a7	f6abc555-5b6c-6f7a-8b9c-0d123456789a	PcdmbAShPQRDxUDVgKbvI3lRjqzBVbXJdSTpjbbAd2U	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-11 13:06:58.228084+00	2025-09-11 13:06:58.228084+00	2025-09-11 21:06:58.226548+00	t	\N
749fa76e-f378-4c96-90ef-180c959b595e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_r7hQn4LavSOx2rhVS_igYbKaWSxaHQ7Kv6mQHwfWKg	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-11 13:10:21.646824+00	2025-09-11 13:10:21.646824+00	2025-09-11 21:10:21.645934+00	t	\N
79bb0216-1b59-4f79-a3a6-a27aaed06f98	f6abc555-5b6c-6f7a-8b9c-0d123456789a	O3tZxrj-scoWPYlTEjL1mcXeXMhmYVbXvNUQSDVn03Y	176.79.222.12	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-11 14:15:27.10783+00	2025-09-11 14:15:27.10783+00	2025-09-11 22:15:27.105828+00	t	\N
56a891d2-9748-41af-8cd2-b99893db1025	f6abc555-5b6c-6f7a-8b9c-0d123456789a	jdJ2kj8y6jYqKny7ubOTZRjAsfJ0nJ72ndnvizqsm1Q	176.79.222.12	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36	2025-09-11 14:16:44.520912+00	2025-09-11 14:16:44.520912+00	2025-09-11 22:16:44.517379+00	t	\N
5ffffd45-b669-492b-8a45-30482b1873fc	f6abc555-5b6c-6f7a-8b9c-0d123456789a	lC-xTJYu2X50EPXUEULhUus4zK3jtF2lqgNHgnjRIR4	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-11 17:15:47.512165+00	2025-09-11 17:15:47.512165+00	2025-09-12 01:15:47.510872+00	t	\N
c1ce4d1a-e5dc-4a25-b0fc-3d8fb9b70d6e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1d6y44v319RP8jvt5FaGHDY4X0WWB2x4mbl3Rtm8rh8	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-11 17:19:47.16995+00	2025-09-11 17:19:47.16995+00	2025-09-12 01:19:47.168962+00	t	\N
15abe4fd-97c4-4bdc-a3c8-292b5a5446df	f6abc555-5b6c-6f7a-8b9c-0d123456789a	oc3QuEwYk0EWcwwRqJ9gGhMA1XwVOdN2eNDcp9XtOCs	94.66.244.130	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-11 17:26:48.927683+00	2025-09-11 17:26:48.927683+00	2025-09-12 01:26:48.926078+00	t	\N
be4e35c7-0fec-4794-9414-d742d1dceebf	ec000c4c-dd24-4f95-b86d-b0835204843c	JrjiOc23WxXENjoLNRHngoQY2TdnE5lfGSAUA-Bz3sc	94.66.244.130	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-11 17:44:09.652673+00	2025-09-11 17:44:09.652673+00	2025-09-12 01:44:09.651446+00	t	\N
2da7ae83-e65f-499a-9f96-25929c14fa31	f6abc555-5b6c-6f7a-8b9c-0d123456789a	DLWrWz860BuuGH70fOLykSJknkRvhDAlZ9vY8_Q2XN0	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-12 10:06:01.27365+00	2025-09-12 10:06:01.27365+00	2025-09-12 18:06:01.272226+00	t	\N
d404e5a4-db83-4edc-9d95-33510ce967fa	f6abc555-5b6c-6f7a-8b9c-0d123456789a	S1c3Bmn163z0_Xk93TbVylmQhVm0Pnk-d8asAWHt1eg	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-12 17:08:20.516958+00	2025-09-12 17:08:20.516958+00	2025-09-13 01:08:20.514521+00	t	\N
6ae881c6-e290-4af3-b3dc-8702d3366979	ec000c4c-dd24-4f95-b86d-b0835204843c	UTps6j8_D7lPo1izqCzrSCSz5GNHDlMsPdzkxk4P1FM	94.66.244.130	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-12 18:32:11.857292+00	2025-09-12 18:32:11.857292+00	2025-09-13 02:32:11.855535+00	t	\N
6bcb9a67-337f-48dc-b13e-49d0315e4a0b	ec000c4c-dd24-4f95-b86d-b0835204843c	bYtukl0UjtkQ0HKOQv60NwiD3RvGxlW69bd94tYDX6o	31.152.66.217	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-15 09:11:01.018475+00	2025-09-15 09:11:01.018475+00	2025-09-15 17:11:01.015378+00	t	\N
4cb3b789-9dda-4947-a55c-f97947f07d6e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	NsEmm5inHSv1Qi9pwDCgq6bmOOt6-9AdMUIKKrM_GUw	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-15 13:36:05.600048+00	2025-09-15 13:36:05.600048+00	2025-09-15 21:36:05.599412+00	t	\N
14be260c-d7c9-4f1f-b9e9-7d11b1baf156	4db3f5bf-0946-43c0-979b-7ac671e0fbb9	J3zbqJcK2iAEHJ4CULhZlJf_Zuo1zx0ETz5zUiYSN58	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-15 13:38:11.929914+00	2025-09-15 13:38:11.929914+00	2025-09-15 21:38:11.928757+00	t	\N
c79c581e-a423-4c14-b348-2fd2fb12424b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	eVcQfwhUkulXKzqkxoaGLG7hJAvVxP3KO489z_ckcqk	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-15 13:38:38.580592+00	2025-09-15 13:38:38.580592+00	2025-09-15 21:38:38.579808+00	t	\N
3c824de3-96ce-4479-865c-16c98db9772e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	LbxqURX956NH4tcu6C9xnqwu_ByrzzRM3jSPIG2WWQg	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-15 22:06:37.161771+00	2025-09-15 22:06:37.161771+00	2025-09-16 06:06:37.160464+00	t	\N
1980ef3f-fa6e-415a-9fe2-dbc54a995454	f6abc555-5b6c-6f7a-8b9c-0d123456789a	p8v5Sd5k1oZXnuVI20McCrt1DH90fNLKf2lpPkzEuaY	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-16 00:03:21.659612+00	2025-09-16 00:03:21.659612+00	2025-09-16 08:03:21.658188+00	t	\N
a7d835ed-01f1-4629-9350-87901bc0af4d	ec000c4c-dd24-4f95-b86d-b0835204843c	iUSvGWCKVPitg_k4r_yOxnMu9QvEQ1lcVUbbY__AjjE	31.152.66.217	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-17 11:24:25.589962+00	2025-09-17 11:24:25.589962+00	2025-09-17 19:24:25.58898+00	t	\N
010a4c27-67b0-4168-ace2-7d2e1f529979	ec000c4c-dd24-4f95-b86d-b0835204843c	VC_Uo9JlLCjfzeExluKzIcQ4UApO4OjMnt5A0UztK2Y	94.66.240.156	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-20 08:00:42.099817+00	2025-09-20 08:00:42.099817+00	2025-09-20 16:00:42.098747+00	t	\N
f70c4675-8e76-481b-84fd-c82f25ab9d73	f6abc555-5b6c-6f7a-8b9c-0d123456789a	YxF0K9oePq81WHa7lOGuvOguDbS7zH-uNHPvnIFxtng	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-22 21:10:13.090652+00	2025-09-22 21:10:13.090652+00	2025-09-23 05:10:13.088989+00	t	\N
021e144d-0175-461e-816f-1201b70f268c	ec000c4c-dd24-4f95-b86d-b0835204843c	-UGqu3SM0K8zcWQpbDUzxehYAT7l22SS341kzc29PDU	31.152.66.217	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-15 10:14:52.377366+00	2025-09-15 10:14:52.377366+00	2025-09-15 18:14:52.376607+00	t	\N
e1508798-6ac1-4f58-ac4d-7752684d2fc1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	oyJS5pj5s4DwK1QfFzJQue5AIo6WgnfwtZlursuHE7Y	87.58.94.209	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36	2025-09-15 15:47:24.547897+00	2025-09-15 15:47:24.547897+00	2025-09-15 23:47:24.546779+00	t	\N
f2f12471-a374-4106-a02d-e969c021a3cb	f6abc555-5b6c-6f7a-8b9c-0d123456789a	BZkeIzXCz_Mih7EgLOB1VaTCMK8PU-Wd_ZGO1NROYkQ	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-15 23:58:36.545742+00	2025-09-15 23:58:36.545742+00	2025-09-16 07:58:36.540668+00	t	\N
127faf66-d0f5-4bfe-9146-22d690ff3768	f6abc555-5b6c-6f7a-8b9c-0d123456789a	8z523DXVOdFoWhPhyVm75twJkoc0nUstbwQLeL_3Y5s	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-16 00:03:55.829973+00	2025-09-16 00:03:55.829973+00	2025-09-16 08:03:55.828915+00	t	\N
593563eb-bb6a-4a49-a4a5-1cb221cceef8	ec000c4c-dd24-4f95-b86d-b0835204843c	rp3R1JWGfxmGCylYzLcVXvxEue9dKgovlYydvgK1cKY	31.152.66.217	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-19 12:10:14.45079+00	2025-09-19 12:10:14.45079+00	2025-09-19 20:10:14.449679+00	t	\N
84a3ef80-e0e4-4906-848f-0d3855f91507	ec000c4c-dd24-4f95-b86d-b0835204843c	y0Q8BHg-eCysPlSntMX61x4Ut2k7C_a3OhiEMzjse0E	185.16.164.65	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-22 04:37:32.383621+00	2025-09-22 04:37:32.383621+00	2025-09-22 12:37:32.382654+00	t	\N
16bb2532-eee9-4580-80e5-e8ae83948eb1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	uiBaYMUr5lnLe31gwQYoPin7nKx4aBtoC4TeMs_0Cok	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-23 10:48:31.242396+00	2025-09-23 10:48:31.242396+00	2025-09-23 18:48:31.241266+00	t	\N
4f1047a3-3064-44bc-bd52-e31018c1bc67	f6abc555-5b6c-6f7a-8b9c-0d123456789a	5g9rrTOffTAnFB-VPCX7vO8aOXuYwR-I-2RughDeEDs	87.58.94.213	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-23 15:11:55.240685+00	2025-09-23 15:11:55.240685+00	2025-09-23 23:11:55.236198+00	t	\N
c2615d69-253c-47ce-91fc-f2727fe332cf	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kcJE1j1UvXWkN2HEJli2ynoI8XaSHxFB6ZsKGgyLunI	87.58.94.213	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-23 15:17:47.831158+00	2025-09-23 15:17:47.831158+00	2025-09-23 23:17:47.827557+00	t	\N
8c4cf8a6-66f2-466e-9854-d4aedf5cf86d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	upe_hganpgQDysg87cc3oi2thfiE0IMJ-xKMfXqRpK0	87.58.94.213	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-23 15:18:01.726844+00	2025-09-23 15:18:01.726844+00	2025-09-23 23:18:01.724871+00	t	\N
c0a2ee17-3e4f-4d3d-a0df-d4c223e681a0	f6abc555-5b6c-6f7a-8b9c-0d123456789a	7fRIs8FXGSem7pxnCN3rnpFqziVXC0L5U2K22eumO4s	87.58.94.213	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-24 15:05:54.28965+00	2025-09-24 15:05:54.28965+00	2025-09-24 23:05:54.286518+00	t	\N
883547bf-1f07-4470-b72a-b3746c4a4a4b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	_LEBnHoFbSwjJ_BwOAjJBPscwKnIJs_kD84PwcomtTg	87.58.94.213	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-24 15:10:39.422036+00	2025-09-24 15:10:39.422036+00	2025-09-24 23:10:39.418579+00	t	\N
426e0318-a08e-45f3-b2e9-aa51349d299b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	4Livgq24xq-YadGQO_eQtr0VPS9SbBJ1uX_1wiBjmps	87.58.94.213	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-24 15:11:02.088561+00	2025-09-24 15:11:02.088561+00	2025-09-24 23:11:02.084801+00	t	\N
fba01961-f053-4cd6-8f57-baa13a07c8cf	ec000c4c-dd24-4f95-b86d-b0835204843c	rKIG0FuhRkc3gx72KO9ettAe5lbs-g1XD3PplDL2gw4	94.66.245.246	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-28 20:56:56.351874+00	2025-09-28 20:56:56.351874+00	2025-09-29 04:56:56.346849+00	t	\N
8bbb6afb-a133-437b-a228-0d59f00b8fbe	ec000c4c-dd24-4f95-b86d-b0835204843c	jFQGAe79Hq4a4UCpflZUUsnSEbLmqoB7Sc-lPuow13I	109.178.233.94	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-29 09:57:30.328766+00	2025-09-29 09:57:30.328766+00	2025-09-29 17:57:30.325975+00	t	\N
1fb58a4b-f925-4b78-b33a-64f97dad4f9a	f6abc555-5b6c-6f7a-8b9c-0d123456789a	dPCXu-SvUMuFefX3aEZKx0g27bavJN-muQArDwSeoCw	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-29 11:35:31.084779+00	2025-09-29 11:35:31.084779+00	2025-09-29 19:35:31.080824+00	t	\N
0f420aad-4efc-49f3-b370-2bed6e82e187	f6abc555-5b6c-6f7a-8b9c-0d123456789a	aoZophyUIqxWXReYduueFIsRojJjUZ5sC7OQk0fYX8c	87.58.94.219	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-29 17:13:15.801365+00	2025-09-29 17:13:15.801365+00	2025-09-30 01:13:15.800216+00	t	\N
941c407b-ef5e-4a25-9039-d350c2038d4d	f6abc555-5b6c-6f7a-8b9c-0d123456789a	WHZ2wNjykI3Xj4HlgYmYkAMnt8RdTzoGooTgQ2iad_4	87.58.94.219	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-29 17:18:17.765038+00	2025-09-29 17:18:17.765038+00	2025-09-30 01:18:17.761905+00	t	\N
808692fa-0a0e-4154-a889-d9666601115b	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ysP-DG7OP5OM_ncNPF8yJvTGAjIHrx9p-DktkkqFu4Y	87.58.94.219	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-29 17:21:50.358012+00	2025-09-29 17:21:50.358012+00	2025-09-30 01:21:50.351656+00	t	\N
dac558c3-ced6-484d-8f44-17209591f6e5	ec000c4c-dd24-4f95-b86d-b0835204843c	1XMyX5tMYFS7ds-tUq4iofBBCMS_gqd0fftTCzEdvr0	94.66.245.246	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-30 20:30:48.821378+00	2025-09-30 20:30:48.821378+00	2025-10-01 04:30:48.803995+00	t	\N
28d252f6-3681-4a17-9b8e-3d92eed3a95b	ec000c4c-dd24-4f95-b86d-b0835204843c	qLaEvtZcUCVjnygQUj1WjH-BA_VSwaJz88ixLcMicws	79.131.185.227	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-01 10:36:53.081593+00	2025-10-01 10:36:53.081593+00	2025-10-01 18:36:53.064381+00	t	\N
eb2bb5b5-4312-41c6-a52d-1f872f2edb4e	f6abc555-5b6c-6f7a-8b9c-0d123456789a	heg6jBgJ-KgKY9daQaZO9OFDUIvtJLUI2vrKYmTSonY	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-02 14:17:29.445216+00	2025-10-02 14:17:29.445216+00	2025-10-02 22:17:29.430934+00	t	\N
d1c5c04a-13eb-44bf-acdb-9ad4617beb92	f6abc555-5b6c-6f7a-8b9c-0d123456789a	jmAD_0EV4iGyl3ziQ-OKIX39qcYCUQQYAKUd9DBr4KI	87.58.94.219	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-02 16:31:33.819167+00	2025-10-02 16:31:33.819167+00	2025-10-03 00:31:33.814447+00	t	\N
361b5c93-30b8-4b26-8b15-906d57b363c1	ec000c4c-dd24-4f95-b86d-b0835204843c	7fEoYMUGscf5PpVoBKE8FjvaW2SdwL9aHhyMgnJn1yo	109.178.53.227	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-09 09:48:01.405176+00	2025-10-09 09:48:01.405176+00	2025-10-09 17:48:01.401026+00	t	\N
042e6ecb-052b-4b19-b315-1855cdedba15	49245fcc-06f5-43a6-9fa6-8f59648a0527	5jbYqL0R65mItPAZyZGpop4QG9GQuF4VAsaT-CoE5mA	109.178.53.227	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-09 09:49:54.634373+00	2025-10-09 09:49:54.634373+00	2025-10-09 17:49:54.631679+00	t	\N
ae83e118-e537-4ee0-9025-653fda1ea42c	ec000c4c-dd24-4f95-b86d-b0835204843c	z3y7mMtOnZotcFIPLmd7jtEj8kTbqAzVx9sOnrK6Q_A	109.178.53.227	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-09 10:06:55.66696+00	2025-10-09 10:06:55.66696+00	2025-10-09 18:06:55.664245+00	t	\N
410d0d98-a833-4475-a064-347eef23424b	ec000c4c-dd24-4f95-b86d-b0835204843c	ujv8qGigTbptAtW279-n7rY9P863elxFeJJw18Rxn4c	109.178.25.139	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-20 11:14:38.449588+00	2025-10-20 11:14:38.449588+00	2025-10-20 19:14:38.434835+00	t	\N
e20f861b-02be-4ddd-b6bf-81398dfdb1eb	49245fcc-06f5-43a6-9fa6-8f59648a0527	CETKOCGDs7AhUZ_Xagc-zg0vIEsQVLrD9MKxAhknorI	109.178.25.139	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-20 11:15:12.450604+00	2025-10-20 11:15:12.450604+00	2025-10-20 19:15:12.449125+00	t	\N
fe094332-da66-4133-92ba-a99d610f551c	ec000c4c-dd24-4f95-b86d-b0835204843c	_QEglALBj7uxIMSUiJckdhHuIGjJnQLg2Zc5PSRL6lI	109.178.25.139	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-20 11:17:38.737398+00	2025-10-20 11:17:38.737398+00	2025-10-20 19:17:38.734151+00	t	\N
f60cb353-0b09-4be8-8225-6914758e1fd1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	ymLbk-tIc7wDrhgiO3M_piApG5CEdIIaGghB0pYtnNw	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 00:00:47.087146+00	2025-10-21 00:00:47.087146+00	2025-10-21 08:00:47.081728+00	t	\N
fd711753-9a71-4fe2-a23a-b57a8a02f456	c1ddd000-0d1d-1e23-4567-890123456789	JhhaRH4n-evVaUKec-QvVSPxZLes12h9MbZfqLoN34I	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 00:02:00.871953+00	2025-10-21 00:02:00.871953+00	2025-10-21 08:02:00.866515+00	t	\N
fea296a6-5b79-4865-aa0e-dc107ca0a566	f6abc555-5b6c-6f7a-8b9c-0d123456789a	1-L8TeD2I0RR9w0aTTYgJZ2wDtrK0A9giIdLFvJCoi0	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 00:03:49.70412+00	2025-10-21 00:03:49.70412+00	2025-10-21 08:03:49.70026+00	t	\N
725a8b6c-697a-49d6-a997-d5b411c92341	49245fcc-06f5-43a6-9fa6-8f59648a0527	1FK1ablGneSjUul1_ptpyXCDgi3w92nwA1I_5lqJcnU	109.178.25.139	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-21 10:04:34.989148+00	2025-10-21 10:04:34.989148+00	2025-10-21 18:04:34.987827+00	t	\N
fed68e2d-494e-4057-b5b7-6d604e12a1c1	49245fcc-06f5-43a6-9fa6-8f59648a0527	5kWwhdYTE2U7x1S7im8s3n1rAarvU_jaqtavZvlKdfs	109.178.25.139	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-10-21 10:10:19.717901+00	2025-10-21 10:10:19.717901+00	2025-10-21 18:10:19.716451+00	t	\N
db886443-b0cd-4470-934e-78528f3b4daa	c1ddd000-0d1d-1e23-4567-890123456789	F4Zm0qfK-KUR03ZTx4aT1JVNI5gzHlfMaRv0yvsmG3s	46.50.3.68	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 16:43:02.95166+00	2025-10-21 16:43:02.95166+00	2025-10-22 00:43:02.947548+00	t	\N
c5a22f13-9314-4a2f-b5e0-dd5058c18bb1	f6abc555-5b6c-6f7a-8b9c-0d123456789a	3JxTImcgN59t1RVi-hgl-EIxmPx6TB3Ck09EIIlmX6E	46.50.3.68	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 16:44:55.010387+00	2025-10-21 16:44:55.010387+00	2025-10-22 00:44:55.008525+00	t	\N
6b4a2fb6-2399-4347-986a-5d9f4636e188	49245fcc-06f5-43a6-9fa6-8f59648a0527	PVhfJPPrcB7cbMfbJ4kuHvH_lhIztnf3C3Nk7-tEX0g	2.87.187.224	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36	2025-10-21 16:54:13.090652+00	2025-10-21 16:54:13.090652+00	2025-10-22 00:54:13.086027+00	t	\N
5f568095-f0bd-4789-9949-164c4978842f	f6abc555-5b6c-6f7a-8b9c-0d123456789a	kcQUzU_ybX6XVShSFx0px9sFRu-tLJaVFvDBSt8WOlU	46.50.3.68	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 17:19:52.750643+00	2025-10-21 17:19:52.750643+00	2025-10-22 01:19:52.747605+00	t	\N
72dbbc04-ed5d-4a57-84b3-024d2458c2c2	f6abc555-5b6c-6f7a-8b9c-0d123456789a	lXiSNqS_Wu2GQY9bCAF3AxxWR_ZvAuFrQmwI9YopIwM	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 23:18:33.905357+00	2025-10-21 23:18:33.905357+00	2025-10-22 07:18:33.90163+00	t	\N
386214f7-70ad-4ee4-aae4-046aa53fe3d6	f6abc555-5b6c-6f7a-8b9c-0d123456789a	YrPukfsvGhy6CWpxbSD7o-wdA2l4oAbiSwI6ffLTE1A	176.79.222.12	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-21 23:28:48.900546+00	2025-10-21 23:28:48.900546+00	2025-10-22 07:28:48.896518+00	t	\N
dd8a2bc4-ed1a-4da8-858a-877f9d5542da	ec000c4c-dd24-4f95-b86d-b0835204843c	mo0telMhmH6VMidlvbtU8wBk7c1-I8GsOYn_FjqjB0g	109.178.25.139	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-22 07:28:12.59102+00	2025-10-22 07:28:12.59102+00	2025-10-22 15:28:12.586859+00	t	\N
43074a68-0aec-4ce3-b6ee-5c5cd8b420e1	ec000c4c-dd24-4f95-b86d-b0835204843c	wyoszwR4pFM0Hav3yVdwVmKGDTw7Zz9UVlJ3aTEVdIc	2.87.187.224	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-22 15:29:43.459797+00	2025-10-22 15:29:43.459797+00	2025-10-22 23:29:43.455391+00	t	\N
78d16b16-7cad-4318-aea3-a484f7017805	49245fcc-06f5-43a6-9fa6-8f59648a0527	yX2LRgRBugfjUIyjJ7LVLnMIvcuYPZfKeNkWXFtRArI	2.87.187.224	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-22 15:48:48.62211+00	2025-10-22 15:48:48.62211+00	2025-10-22 23:48:48.618424+00	t	\N
092b5199-77b6-489e-b706-251712ec43b8	ec000c4c-dd24-4f95-b86d-b0835204843c	6DzgqiVB5Hrh94TOFs86blGpSkGlwviVKdjvIwrByqg	2.87.187.224	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-22 15:51:29.230131+00	2025-10-22 15:51:29.230131+00	2025-10-22 23:51:29.228792+00	t	\N
9003ecbb-869c-4447-9df2-e034c7066cbf	ec000c4c-dd24-4f95-b86d-b0835204843c	T59gbgvruiS6rLq63fiMewlpOjWtebI8rXkFhA3cbO8	94.66.251.74	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-24 11:28:25.810217+00	2025-10-24 11:28:25.810217+00	2025-10-24 19:28:25.787996+00	t	\N
256d26b8-657d-45c5-b18b-5acff936c8fd	c068d54f-9f9c-4735-a4e1-ef3ecd0c2510	UGN1Yge9z7e84PITCBGfkENVc_SGfMNkDKJlHhgbFMc	94.66.251.74	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-10-24 11:41:04.850304+00	2025-10-24 11:41:04.850304+00	2025-10-24 19:41:04.848703+00	t	\N
9e306a29-0c2a-49f7-88b1-cb56f8801a55	ec000c4c-dd24-4f95-b86d-b0835204843c	jniyCWyDFKVikRGANiXEXkfSh06PBb5Q74_KXgYtljo	2.87.154.6	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-11-02 14:53:42.53197+00	2025-11-02 14:53:42.53197+00	2025-11-02 22:53:42.500527+00	t	\N
88365801-d421-4698-b617-421d345261e9	49245fcc-06f5-43a6-9fa6-8f59648a0527	Zqxqu10BGxj7i1eOfa-gexvvbx89eoz5HvYqn3EA6kI	2.87.154.6	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-11-02 14:54:14.442011+00	2025-11-02 14:54:14.442011+00	2025-11-02 22:54:14.440561+00	t	\N
7e2b9d1f-4339-41d6-8c0c-ca4d0ea117bb	ec000c4c-dd24-4f95-b86d-b0835204843c	vzWx97Rsl0npqgRX7BMW83Tayseuz3H3dDH6uHy0Gl0	2.87.154.6	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36	2025-11-05 19:57:20.381341+00	2025-11-05 19:57:20.381341+00	2025-11-06 03:57:20.365876+00	t	\N
a5e0083d-bf89-4e08-8266-18fa56325c18	ec000c4c-dd24-4f95-b86d-b0835204843c	PhJ0_2JwjiQ5Y2FMvwKVnHUMVQMGZiC399bIoqZhHEg	2.87.154.6	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-11-06 07:48:58.070345+00	2025-11-06 07:48:58.070345+00	2025-11-06 15:48:58.047045+00	t	\N
429e7ba4-8636-45e2-896d-a4e4456b184c	49245fcc-06f5-43a6-9fa6-8f59648a0527	tzXDz_yCN7gMZG6ICOerZBcZbTzs2iDAGWDidwWpYhY	79.131.186.241	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-11-08 17:55:22.421786+00	2025-11-08 17:55:22.421786+00	2025-11-09 01:55:22.388343+00	t	\N
15e2609e-117f-4051-9ed1-54f62bd78974	ec000c4c-dd24-4f95-b86d-b0835204843c	AJ0a6jBEJto0yjtFbed_qVlzbbnMW8MtFQookO2u_80	109.178.153.193	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36	2025-11-10 06:57:08.236154+00	2025-11-10 06:57:08.236154+00	2025-11-10 14:57:08.211157+00	t	\N
3e33f988-d757-4450-b244-f8725d89e8f3	ec000c4c-dd24-4f95-b86d-b0835204843c	BOcmQ7md0TjyoSOtWKMhiozRvU1q1dPMRUcbeXLlw-g	109.178.153.193	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	2025-11-10 13:48:04.906814+00	2025-11-10 13:48:04.906814+00	2025-11-10 21:48:04.87929+00	t	\N
052f8528-beca-4edf-a825-b035320f5d9e	ec000c4c-dd24-4f95-b86d-b0835204843c	kOc8pJQuHiGE4QBLZgPFt6YoKMBOAShPhJApSjeqov4	109.178.153.193	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-12 11:57:31.99612+00	2025-11-12 11:57:31.99612+00	2025-11-12 19:57:31.967464+00	t	\N
6392b7ff-a7a7-40fe-8714-7991e3f25f4d	49245fcc-06f5-43a6-9fa6-8f59648a0527	EaCvTDeuj9wYVu7AZ7aD_OsNaqT1SpigbJQuDm3E0Rw	109.178.153.193	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-12 12:02:40.148467+00	2025-11-12 12:02:40.148467+00	2025-11-12 20:02:40.146605+00	t	\N
e573122d-b184-4c4f-be7f-b4e8749b5120	ec000c4c-dd24-4f95-b86d-b0835204843c	qK6oxw78SKnoTjerGYCkss7nkf67wa08OR0M6PReQxE	109.178.153.193	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-12 12:08:24.840528+00	2025-11-12 12:08:24.840528+00	2025-11-12 20:08:24.839136+00	t	\N
286e51d8-c9bd-475d-87c8-35883fec7c3a	ec000c4c-dd24-4f95-b86d-b0835204843c	0nimNFJ2EkednOYp8YbmPUZFz-767QakbQB9CiGTzmQ	109.178.153.193	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36	2025-11-12 12:22:57.657313+00	2025-11-12 12:22:57.657313+00	2025-11-12 20:22:57.655267+00	t	\N
a642440a-3d9f-4678-a197-fac8e93a4a19	ec000c4c-dd24-4f95-b86d-b0835204843c	SFXdAJZBrgkWGWCDb1aKknoVm9CPg6sbmwE59pretBg	31.152.50.242	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-13 10:30:48.863912+00	2025-11-13 10:30:48.863912+00	2025-11-13 18:30:48.837535+00	t	\N
24de234c-a42e-4e05-9f32-f89ddebf97f4	49245fcc-06f5-43a6-9fa6-8f59648a0527	xbxrmgu70gf6PuSQ9gLKaUcVQIhwvx6O7fNpY-scLvo	31.152.50.242	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-17 11:17:00.559533+00	2025-11-17 11:17:00.559533+00	2025-11-17 19:17:00.528294+00	t	\N
c2112be3-ed21-4025-b11c-7b688d85d53b	49245fcc-06f5-43a6-9fa6-8f59648a0527	_38UP0yv0o9jIWzjalKtGvfSpe1qbu5Kvd16IlG35EA	31.152.50.242	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-18 14:57:12.294152+00	2025-11-18 14:57:12.294152+00	2025-11-18 22:57:12.266871+00	t	\N
082ab519-0fb9-4faf-a553-d120a9a778e7	d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	Il6CClKPmsAZJharB-dlKwe2A6rBXhpHdrnd85irRuk	31.152.50.242	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-18 14:59:00.883517+00	2025-11-18 14:59:00.883517+00	2025-11-18 22:59:00.881274+00	t	\N
3a7b0e56-c733-455a-863c-73619de28d88	49245fcc-06f5-43a6-9fa6-8f59648a0527	Sdvhwuza7wynpHx397ndKBGOwPJs9JsRh6DpBc2SXWk	31.152.50.242	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-19 12:48:00.944693+00	2025-11-19 12:48:00.944693+00	2025-11-19 20:48:00.929571+00	t	\N
4863df87-08c3-45b4-a2e2-adfa7989f066	ec000c4c-dd24-4f95-b86d-b0835204843c	rh0rzds7eAh9AIZZ2gakSr2P30jTkaZ0ZbWLRF2kfZ4	31.152.50.242	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2025-11-20 09:18:25.497358+00	2025-11-20 09:18:25.497358+00	2025-11-20 17:18:25.481392+00	t	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.users (id, organization_id, username, password_hash, email, name, role, user_status, failed_login_attempts, locked_until, last_login, invitation_token, invitation_expires_at, password_reset_token, password_reset_expires_at, is_active, created_at, updated_at, invited_by_user_id, email_verification_token, email_verification_expires_at, pending_email, preferred_language, preferred_country, localization_preferences, profile_photo_url) FROM stdin;
b0ccc999-9c0c-0d12-3456-789012345678	c2dee111-1e2d-2b3c-4d5e-6f7a8b9c0123	autoparts_user	$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2	user@autoparts.com	AutoParts User	user	active	0	\N	\N	\N	\N	\N	\N	t	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N	\N	\N
d2eee111-1e2e-2f34-5678-901234567890	e4fac333-3c4f-4d5e-6f7a-8b9c01234568	industrial_user	$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2	user@industrial.com	Industrial User	user	active	0	\N	\N	\N	\N	\N	\N	t	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N	\N	\N
f5abc444-4a5b-5e6f-7a8b-9c0123456789	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	autoboss_admin	$2b$12$iPjCrXM5KgyxmQ99HA.k2ux95xNuxxHTZFrsE4QXRCe1AZS68H8Uy	admin@autoboss.com	Autoboss Admin	admin	active	0	\N	2025-08-06 12:48:07.152169+00	\N	\N	\N	\N	t	2025-08-03 14:53:16.435722+00	2025-08-06 12:48:07.148549+00	\N	\N	\N	\N	\N	\N	\N	\N
49245fcc-06f5-43a6-9fa6-8f59648a0527	0f676a79-6c15-4c67-9096-0ac3467d404f	Zisis	$2b$12$82Qz9OxHAfWWl/0.73W15OSxduSN0WCj96lzZLkSNUoYMeZ4Y6fNW	diogo.thomaz@gmail.com	Zisis Petmezas	admin	active	0	\N	2025-11-21 11:50:28.519319+00	\N	\N	\N	\N	t	2025-10-09 09:49:34.510262+00	2025-11-21 11:50:28.174219+00	\N	\N	\N	\N	\N	\N	\N	/static/images/profile_e95955d3-34e9-48e7-8bd7-5d8dde3b7cef.png
f6abc555-5b6c-6f7a-8b9c-0d123456789a	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	superadmin	$2b$12$EZmnkx4PtmMm3iNZkn6JcuYdDDXKIgD7hqe8D9wkuTx7sD9D8/h.K	superadmin@oraseas.com	Super Admin	super_admin	active	0	\N	2025-11-21 12:06:11.332167+00	\N	\N	\N	\N	t	2025-08-03 14:53:16.435722+00	2025-11-21 12:06:10.962942+00	\N	\N	\N	\N	\N	\N	\N	\N
ec000c4c-dd24-4f95-b86d-b0835204843c	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	dthomaz	$2b$12$tQ.q7SlDF2Sil2kRzHaOkeiCDsK0GSb8BJqvl6UPV.PYpfc7yCJtW	diogothomaz@oraseas.com	Diogo Thomaz	super_admin	active	0	\N	2025-11-21 12:07:20.984827+00	\N	\N	\N	\N	t	2025-09-11 17:42:51.985996+00	2025-11-21 12:07:20.639417+00	\N	\N	\N	\N	\N	\N	\N	/static/images/profile_b4995e2b-4b53-4ff9-aeaf-d95db6953237.png
bc37ae83-a8e6-4edd-b672-d86f510a76ec	434b0c43-4461-462c-8e0d-b6dd4236c8fa	jamie	$2b$12$RKwylU/M9UNUMqR0WFM6yOAWwbVSduqQxzvyxg0xlfcQuWqigNZ16	jamie@bossserv.co.uk	Jamie Clark	super_admin	active	0	\N	\N	\N	\N	\N	\N	t	2025-11-21 12:16:31.086034+00	2025-11-21 12:16:31.086034+00	\N	\N	\N	\N	\N	\N	\N	\N
c1ddd000-0d1d-1e23-4567-890123456789	d3eff222-2f3e-3c4d-5e6f-7a8b9c012346	robomech_user	$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2	user@robomech.com	RoboMech User	user	active	0	\N	2025-10-21 16:43:02.95443+00	\N	\N	\N	\N	t	2025-08-03 14:53:16.435722+00	2025-10-21 16:43:02.95166+00	\N	\N	\N	\N	\N	\N	\N	\N
d3eff222-2f3e-3c4d-5e6f-7a8b9c012345	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	oraseasee_admin	$2b$12$iPjCrXM5KgyxmQ99HA.k2ux95xNuxxHTZFrsE4QXRCe1AZS68H8Uy	admin@oraseas.com	Oraseas Admin	admin	active	0	\N	2025-11-18 14:59:00.885765+00	\N	\N	\N	\N	t	2025-08-03 14:53:16.435722+00	2025-11-18 14:59:00.883517+00	\N	\N	\N	\N	\N	\N	\N	\N
4db3f5bf-0946-43c0-979b-7ac671e0fbb9	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	testuser	$2b$12$RDuKxFpuv67R1fpE.b3WyueMclhoD.Y5pYT8D/Jk18vYz6yVHxC7S	testuser@oraseas.com	TestUser	user	active	0	\N	2025-09-15 13:38:11.931902+00	\N	\N	\N	\N	t	2025-09-15 13:37:41.986185+00	2025-09-15 13:38:11.929914+00	\N	\N	\N	\N	\N	\N	\N	\N
c068d54f-9f9c-4735-a4e1-ef3ecd0c2510	160d8213-2d5b-4d58-84cc-fbf53becb528	dimitris	$2b$12$ENAXU8AwCN2SSVl7Oj2YS.iBNOOcoWDVrDz878bnA7PaIJo5N/6Py	coo@tharawatseas.com.sa	Dimitris Dimopoulos	admin	active	0	\N	2025-10-24 11:41:04.852134+00	\N	\N	\N	\N	t	2025-10-24 11:40:43.546508+00	2025-10-24 11:41:04.850304+00	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: abparts_user
--

COPY public.warehouses (id, organization_id, name, location, description, is_active, created_at, updated_at, address, contact_person, phone, email, capacity_limit, warehouse_type) FROM stdin;
11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	Main Warehouse	Building A, 123 Main St, Auckland	Primary storage facility	t	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N
22eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	Spare Parts Warehouse	Building B, 123 Main St, Auckland	Specialized spare parts storage	t	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N
33cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01	Production Warehouse	456 Tech Park, Wellington	On-site parts storage	t	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N
44eff222-2f3e-3c4d-5e6f-7a8b9c012346	d3eff222-2f3e-3c4d-5e6f-7a8b9c012346	RoboMech Storage	101 Automation Drive, Hamilton	Customer parts inventory	t	2025-08-03 14:53:16.435722+00	2025-08-03 14:53:16.435722+00	\N	\N	\N	\N	\N	\N
1e019a80-2852-4269-b3d3-2c5a46ded47f	0f676a79-6c15-4c67-9096-0ac3467d404f	Kefalonia Fisheries SA	Kefalonia	Default warehouse for Kefalonia Fisheries SA	t	2025-09-15 09:14:21.021774+00	2025-09-15 09:14:21.021774+00	\N	\N	\N	\N	\N	\N
1c080c84-de25-4a8b-b490-121f445eacfb	0449761e-0b70-4f21-a4ab-f526e7c1528b	Kito Fishfarming SA	Leros Island	Default warehouse for Kito Fishfarming SA	t	2025-09-15 09:14:44.417896+00	2025-09-15 09:14:44.417896+00	\N	\N	\N	\N	\N	\N
b1982afa-f726-4bb9-adef-78924f14f481	1f7dcfa6-0e84-4597-8285-33c1bfbaca5d	Petalas Bros SA	Kalymnos Island	Default warehouse for Petalas Bros SA	t	2025-09-15 09:15:10.187516+00	2025-09-15 09:15:10.187516+00	\N	\N	\N	\N	\N	\N
3324e865-0f94-4a3f-814a-4b854ed0d169	d5b34232-ad40-45dd-8e8a-c57e0b993aa5	Leros Fishfarming SA	Leros Island	Default warehouse for Leros Fishfarming SA	t	2025-09-15 09:15:37.102234+00	2025-09-15 09:15:37.102234+00	\N	\N	\N	\N	\N	\N
ab005090-a8ab-4673-9c52-6944ea951eec	ed6d6318-8c68-49e6-9f73-f5b8346ef0db	Korfos Fishfarming	Korfos, Greece	Default warehouse for Korfos Fishfarming	t	2025-09-15 09:16:01.439016+00	2025-09-15 09:16:01.439016+00	\N	\N	\N	\N	\N	\N
e8f25870-452e-4440-888d-8d4dda6d3fe6	81b293ec-0a56-463a-a75a-df699b125779	Philosofish SA	Athens, Greece	Default warehouse for Philosofish SA	t	2025-09-15 09:16:24.590935+00	2025-09-15 09:16:24.590935+00	\N	\N	\N	\N	\N	\N
5806626c-4b8b-47b4-bc6f-856fa76e8a01	160d8213-2d5b-4d58-84cc-fbf53becb528	Tharawat Seas LLC	Jeddah, KSA	Default warehouse for Tharawat Seas LLC	t	2025-09-15 09:16:54.916079+00	2025-09-15 09:16:54.916079+00	\N	\N	\N	\N	\N	\N
b5f0718a-c914-40ac-baff-2d1e4fac8aa4	3833cea1-8178-4ce6-a705-01492d91c850	Temri	Cyprus	Default warehouse for Temri	t	2025-09-15 09:17:15.120921+00	2025-09-15 09:17:15.120921+00	\N	\N	\N	\N	\N	\N
402317bf-7d65-432f-9099-6ed4a852b95c	3833cea1-8178-4ce6-a705-01492d91c850	Test WH	Test WH Street		t	2025-09-15 14:49:18.570838+00	2025-09-15 14:49:18.570838+00	\N	\N	\N	\N	\N	\N
70851ed9-1146-4abb-8463-699907dfefe9	3833cea1-8178-4ce6-a705-01492d91c850	Test WH II	Test WH II Street		t	2025-09-15 15:01:13.275467+00	2025-09-15 15:01:13.275467+00	\N	\N	\N	\N	\N	\N
\.


--
-- Name: machine_part_compatibility _machine_part_uc; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_part_compatibility
    ADD CONSTRAINT _machine_part_uc UNIQUE (machine_id, part_id);


--
-- Name: warehouses _org_warehouse_name_uc; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT _org_warehouse_name_uc UNIQUE (organization_id, name);


--
-- Name: inventory _warehouse_part_uc; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT _warehouse_part_uc UNIQUE (warehouse_id, part_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: customer_order_items customer_order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_order_items
    ADD CONSTRAINT customer_order_items_pkey PRIMARY KEY (id);


--
-- Name: customer_orders customer_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_pkey PRIMARY KEY (id);


--
-- Name: inventory_adjustments inventory_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_pkey PRIMARY KEY (id);


--
-- Name: inventory_alerts inventory_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_alerts
    ADD CONSTRAINT inventory_alerts_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_warehouse_id_part_id_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_warehouse_id_part_id_key UNIQUE (warehouse_id, part_id);


--
-- Name: invitation_audit_logs invitation_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.invitation_audit_logs
    ADD CONSTRAINT invitation_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: machine_hours machine_hours_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_hours
    ADD CONSTRAINT machine_hours_pkey PRIMARY KEY (id);


--
-- Name: machine_maintenance machine_maintenance_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_maintenance
    ADD CONSTRAINT machine_maintenance_pkey PRIMARY KEY (id);


--
-- Name: machine_part_compatibility machine_part_compatibility_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_part_compatibility
    ADD CONSTRAINT machine_part_compatibility_pkey PRIMARY KEY (id);


--
-- Name: machine_predictions machine_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_predictions
    ADD CONSTRAINT machine_predictions_pkey PRIMARY KEY (id);


--
-- Name: machine_sales machine_sales_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_sales
    ADD CONSTRAINT machine_sales_pkey PRIMARY KEY (id);


--
-- Name: machines machines_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_pkey PRIMARY KEY (id);


--
-- Name: machines machines_serial_number_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_serial_number_key UNIQUE (serial_number);


--
-- Name: maintenance_part_usage maintenance_part_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_pkey PRIMARY KEY (id);


--
-- Name: maintenance_recommendations maintenance_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_recommendations
    ADD CONSTRAINT maintenance_recommendations_pkey PRIMARY KEY (id);


--
-- Name: organization_configurations organization_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organization_configurations
    ADD CONSTRAINT organization_configurations_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_name_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_name_key UNIQUE (name);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: part_order_items part_order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_items
    ADD CONSTRAINT part_order_items_pkey PRIMARY KEY (id);


--
-- Name: part_order_requests part_order_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_requests
    ADD CONSTRAINT part_order_requests_pkey PRIMARY KEY (id);


--
-- Name: part_usage_items part_usage_items_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_items
    ADD CONSTRAINT part_usage_items_pkey PRIMARY KEY (id);


--
-- Name: part_usage part_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage
    ADD CONSTRAINT part_usage_pkey PRIMARY KEY (id);


--
-- Name: part_usage_records part_usage_records_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_records
    ADD CONSTRAINT part_usage_records_pkey PRIMARY KEY (id);


--
-- Name: parts parts_part_number_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.parts
    ADD CONSTRAINT parts_part_number_key UNIQUE (part_number);


--
-- Name: parts parts_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.parts
    ADD CONSTRAINT parts_pkey PRIMARY KEY (id);


--
-- Name: predictive_maintenance_models predictive_maintenance_models_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.predictive_maintenance_models
    ADD CONSTRAINT predictive_maintenance_models_pkey PRIMARY KEY (id);


--
-- Name: security_event_logs security_event_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.security_event_logs
    ADD CONSTRAINT security_event_logs_pkey PRIMARY KEY (id);


--
-- Name: security_events security_events_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.security_events
    ADD CONSTRAINT security_events_pkey PRIMARY KEY (id);


--
-- Name: stock_adjustments stock_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_pkey PRIMARY KEY (id);


--
-- Name: stocktake_items stocktake_items_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktake_items
    ADD CONSTRAINT stocktake_items_pkey PRIMARY KEY (id);


--
-- Name: stocktakes stocktakes_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktakes
    ADD CONSTRAINT stocktakes_pkey PRIMARY KEY (id);


--
-- Name: supplier_order_items supplier_order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.supplier_order_items
    ADD CONSTRAINT supplier_order_items_pkey PRIMARY KEY (id);


--
-- Name: supplier_orders supplier_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.supplier_orders
    ADD CONSTRAINT supplier_orders_pkey PRIMARY KEY (id);


--
-- Name: system_configurations system_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.system_configurations
    ADD CONSTRAINT system_configurations_pkey PRIMARY KEY (id);


--
-- Name: transaction_approvals transaction_approvals_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transaction_approvals
    ADD CONSTRAINT transaction_approvals_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: user_management_audit_logs user_management_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.user_management_audit_logs
    ADD CONSTRAINT user_management_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: warehouses warehouses_organization_id_name_key; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_organization_id_name_key UNIQUE (organization_id, name);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: idx_inventory_warehouse_part; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_inventory_warehouse_part ON public.inventory USING btree (warehouse_id, part_id);


--
-- Name: idx_machines_customer; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_machines_customer ON public.machines USING btree (customer_organization_id);


--
-- Name: idx_organizations_name; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_organizations_name ON public.organizations USING btree (name);


--
-- Name: idx_parts_manufacturer; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_parts_manufacturer ON public.parts USING btree (manufacturer) WHERE (manufacturer IS NOT NULL);


--
-- Name: idx_parts_name_fulltext; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_parts_name_fulltext ON public.parts USING gin (to_tsvector('english'::regconfig, (name)::text));


--
-- Name: idx_parts_part_number; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_parts_part_number ON public.parts USING btree (part_number);


--
-- Name: idx_parts_type_proprietary; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_parts_type_proprietary ON public.parts USING btree (part_type, is_proprietary);


--
-- Name: idx_transactions_date; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_transactions_date ON public.transactions USING btree (transaction_date);


--
-- Name: idx_transactions_part; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_transactions_part ON public.transactions USING btree (part_id);


--
-- Name: idx_transactions_warehouse; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_transactions_warehouse ON public.transactions USING btree (from_warehouse_id, to_warehouse_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_org_role; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_users_org_role ON public.users USING btree (organization_id, role);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: ix_inventory_adjustments_adjustment_date; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_adjustments_adjustment_date ON public.inventory_adjustments USING btree (adjustment_date);


--
-- Name: ix_inventory_adjustments_part_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_adjustments_part_id ON public.inventory_adjustments USING btree (part_id);


--
-- Name: ix_inventory_adjustments_stocktake_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_adjustments_stocktake_id ON public.inventory_adjustments USING btree (stocktake_id);


--
-- Name: ix_inventory_adjustments_warehouse_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_adjustments_warehouse_id ON public.inventory_adjustments USING btree (warehouse_id);


--
-- Name: ix_inventory_alerts_alert_type; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_alerts_alert_type ON public.inventory_alerts USING btree (alert_type);


--
-- Name: ix_inventory_alerts_is_active; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_alerts_is_active ON public.inventory_alerts USING btree (is_active);


--
-- Name: ix_inventory_alerts_part_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_alerts_part_id ON public.inventory_alerts USING btree (part_id);


--
-- Name: ix_inventory_alerts_severity; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_alerts_severity ON public.inventory_alerts USING btree (severity);


--
-- Name: ix_inventory_alerts_warehouse_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_inventory_alerts_warehouse_id ON public.inventory_alerts USING btree (warehouse_id);


--
-- Name: ix_organizations_name; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_organizations_name ON public.organizations USING btree (name);


--
-- Name: ix_part_order_requests_order_number; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_part_order_requests_order_number ON public.part_order_requests USING btree (order_number);


--
-- Name: ix_parts_part_number; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_parts_part_number ON public.parts USING btree (part_number);


--
-- Name: ix_stocktake_items_part_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_stocktake_items_part_id ON public.stocktake_items USING btree (part_id);


--
-- Name: ix_stocktake_items_stocktake_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_stocktake_items_stocktake_id ON public.stocktake_items USING btree (stocktake_id);


--
-- Name: ix_stocktakes_scheduled_date; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_stocktakes_scheduled_date ON public.stocktakes USING btree (scheduled_date);


--
-- Name: ix_stocktakes_status; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_stocktakes_status ON public.stocktakes USING btree (status);


--
-- Name: ix_stocktakes_warehouse_id; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE INDEX ix_stocktakes_warehouse_id ON public.stocktakes USING btree (warehouse_id);


--
-- Name: ix_system_configurations_key; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_system_configurations_key ON public.system_configurations USING btree (key);


--
-- Name: ix_user_sessions_session_token; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_user_sessions_session_token ON public.user_sessions USING btree (session_token);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: unique_bossaqua; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX unique_bossaqua ON public.organizations USING btree (organization_type) WHERE (organization_type = 'bossaqua'::public.organizationtype);


--
-- Name: unique_oraseas_ee; Type: INDEX; Schema: public; Owner: abparts_user
--

CREATE UNIQUE INDEX unique_oraseas_ee ON public.organizations USING btree (organization_type) WHERE (organization_type = 'oraseas_ee'::public.organizationtype);


--
-- Name: inventory trigger_check_inventory_balance; Type: TRIGGER; Schema: public; Owner: abparts_user
--

CREATE TRIGGER trigger_check_inventory_balance BEFORE UPDATE ON public.inventory FOR EACH ROW EXECUTE FUNCTION public.check_inventory_balance();


--
-- Name: transactions trigger_update_inventory_on_transaction; Type: TRIGGER; Schema: public; Owner: abparts_user
--

CREATE TRIGGER trigger_update_inventory_on_transaction AFTER INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.update_inventory_on_transaction();


--
-- Name: customer_order_items customer_order_items_customer_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_order_items
    ADD CONSTRAINT customer_order_items_customer_order_id_fkey FOREIGN KEY (customer_order_id) REFERENCES public.customer_orders(id);


--
-- Name: customer_order_items customer_order_items_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_order_items
    ADD CONSTRAINT customer_order_items_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: customer_orders customer_orders_customer_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_customer_organization_id_fkey FOREIGN KEY (customer_organization_id) REFERENCES public.organizations(id);


--
-- Name: customer_orders customer_orders_oraseas_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_oraseas_organization_id_fkey FOREIGN KEY (oraseas_organization_id) REFERENCES public.organizations(id);


--
-- Name: customer_orders customer_orders_ordered_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_ordered_by_user_id_fkey FOREIGN KEY (ordered_by_user_id) REFERENCES public.users(id);


--
-- Name: customer_orders customer_orders_shipped_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_shipped_by_user_id_fkey FOREIGN KEY (shipped_by_user_id) REFERENCES public.users(id);


--
-- Name: inventory_adjustments inventory_adjustments_adjusted_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_adjusted_by_user_id_fkey FOREIGN KEY (adjusted_by_user_id) REFERENCES public.users(id);


--
-- Name: inventory_adjustments inventory_adjustments_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: inventory_adjustments inventory_adjustments_stocktake_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_stocktake_id_fkey FOREIGN KEY (stocktake_id) REFERENCES public.stocktakes(id);


--
-- Name: inventory_adjustments inventory_adjustments_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.transactions(id);


--
-- Name: inventory_adjustments inventory_adjustments_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: inventory_alerts inventory_alerts_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_alerts
    ADD CONSTRAINT inventory_alerts_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: inventory_alerts inventory_alerts_resolved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_alerts
    ADD CONSTRAINT inventory_alerts_resolved_by_user_id_fkey FOREIGN KEY (resolved_by_user_id) REFERENCES public.users(id);


--
-- Name: inventory_alerts inventory_alerts_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory_alerts
    ADD CONSTRAINT inventory_alerts_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: inventory inventory_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: inventory inventory_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: invitation_audit_logs invitation_audit_logs_performed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.invitation_audit_logs
    ADD CONSTRAINT invitation_audit_logs_performed_by_user_id_fkey FOREIGN KEY (performed_by_user_id) REFERENCES public.users(id);


--
-- Name: machine_hours machine_hours_recorded_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_hours
    ADD CONSTRAINT machine_hours_recorded_by_user_id_fkey FOREIGN KEY (recorded_by_user_id) REFERENCES public.users(id);


--
-- Name: machine_part_compatibility machine_part_compatibility_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_part_compatibility
    ADD CONSTRAINT machine_part_compatibility_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: machine_part_compatibility machine_part_compatibility_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_part_compatibility
    ADD CONSTRAINT machine_part_compatibility_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: machine_predictions machine_predictions_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_predictions
    ADD CONSTRAINT machine_predictions_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: machine_predictions machine_predictions_predictive_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_predictions
    ADD CONSTRAINT machine_predictions_predictive_model_id_fkey FOREIGN KEY (predictive_model_id) REFERENCES public.predictive_maintenance_models(id);


--
-- Name: machine_sales machine_sales_from_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_sales
    ADD CONSTRAINT machine_sales_from_organization_id_fkey FOREIGN KEY (from_organization_id) REFERENCES public.organizations(id);


--
-- Name: machine_sales machine_sales_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_sales
    ADD CONSTRAINT machine_sales_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: machine_sales machine_sales_performed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_sales
    ADD CONSTRAINT machine_sales_performed_by_user_id_fkey FOREIGN KEY (performed_by_user_id) REFERENCES public.users(id);


--
-- Name: machine_sales machine_sales_to_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machine_sales
    ADD CONSTRAINT machine_sales_to_organization_id_fkey FOREIGN KEY (to_organization_id) REFERENCES public.organizations(id);


--
-- Name: machines machines_customer_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_customer_organization_id_fkey FOREIGN KEY (customer_organization_id) REFERENCES public.organizations(id);


--
-- Name: maintenance_part_usage maintenance_part_usage_maintenance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_maintenance_id_fkey FOREIGN KEY (maintenance_id) REFERENCES public.machine_maintenance(id);


--
-- Name: maintenance_part_usage maintenance_part_usage_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: maintenance_part_usage maintenance_part_usage_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: maintenance_recommendations maintenance_recommendations_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_recommendations
    ADD CONSTRAINT maintenance_recommendations_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: maintenance_recommendations maintenance_recommendations_prediction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_recommendations
    ADD CONSTRAINT maintenance_recommendations_prediction_id_fkey FOREIGN KEY (prediction_id) REFERENCES public.machine_predictions(id);


--
-- Name: maintenance_recommendations maintenance_recommendations_resolved_by_maintenance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.maintenance_recommendations
    ADD CONSTRAINT maintenance_recommendations_resolved_by_maintenance_id_fkey FOREIGN KEY (resolved_by_maintenance_id) REFERENCES public.machine_maintenance(id);


--
-- Name: organization_configurations organization_configurations_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organization_configurations
    ADD CONSTRAINT organization_configurations_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: organization_configurations organization_configurations_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organization_configurations
    ADD CONSTRAINT organization_configurations_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: organization_configurations organization_configurations_updated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organization_configurations
    ADD CONSTRAINT organization_configurations_updated_by_user_id_fkey FOREIGN KEY (updated_by_user_id) REFERENCES public.users(id);


--
-- Name: organizations organizations_parent_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_parent_organization_id_fkey FOREIGN KEY (parent_organization_id) REFERENCES public.organizations(id);


--
-- Name: part_order_items part_order_items_order_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_items
    ADD CONSTRAINT part_order_items_order_request_id_fkey FOREIGN KEY (order_request_id) REFERENCES public.part_order_requests(id);


--
-- Name: part_order_items part_order_items_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_items
    ADD CONSTRAINT part_order_items_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: part_order_requests part_order_requests_approved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_requests
    ADD CONSTRAINT part_order_requests_approved_by_user_id_fkey FOREIGN KEY (approved_by_user_id) REFERENCES public.users(id);


--
-- Name: part_order_requests part_order_requests_customer_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_requests
    ADD CONSTRAINT part_order_requests_customer_organization_id_fkey FOREIGN KEY (customer_organization_id) REFERENCES public.organizations(id);


--
-- Name: part_order_requests part_order_requests_received_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_requests
    ADD CONSTRAINT part_order_requests_received_by_user_id_fkey FOREIGN KEY (received_by_user_id) REFERENCES public.users(id);


--
-- Name: part_order_requests part_order_requests_requested_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_requests
    ADD CONSTRAINT part_order_requests_requested_by_user_id_fkey FOREIGN KEY (requested_by_user_id) REFERENCES public.users(id);


--
-- Name: part_order_requests part_order_requests_supplier_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_order_requests
    ADD CONSTRAINT part_order_requests_supplier_organization_id_fkey FOREIGN KEY (supplier_organization_id) REFERENCES public.organizations(id);


--
-- Name: part_usage part_usage_customer_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage
    ADD CONSTRAINT part_usage_customer_organization_id_fkey FOREIGN KEY (customer_organization_id) REFERENCES public.organizations(id);


--
-- Name: part_usage_items part_usage_items_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_items
    ADD CONSTRAINT part_usage_items_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: part_usage_items part_usage_items_usage_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_items
    ADD CONSTRAINT part_usage_items_usage_record_id_fkey FOREIGN KEY (usage_record_id) REFERENCES public.part_usage_records(id);


--
-- Name: part_usage part_usage_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage
    ADD CONSTRAINT part_usage_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: part_usage part_usage_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage
    ADD CONSTRAINT part_usage_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: part_usage part_usage_recorded_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage
    ADD CONSTRAINT part_usage_recorded_by_user_id_fkey FOREIGN KEY (recorded_by_user_id) REFERENCES public.users(id);


--
-- Name: part_usage_records part_usage_records_from_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_records
    ADD CONSTRAINT part_usage_records_from_warehouse_id_fkey FOREIGN KEY (from_warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: part_usage_records part_usage_records_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_records
    ADD CONSTRAINT part_usage_records_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: part_usage_records part_usage_records_performed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage_records
    ADD CONSTRAINT part_usage_records_performed_by_user_id_fkey FOREIGN KEY (performed_by_user_id) REFERENCES public.users(id);


--
-- Name: part_usage part_usage_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.part_usage
    ADD CONSTRAINT part_usage_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: predictive_maintenance_models predictive_maintenance_models_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.predictive_maintenance_models
    ADD CONSTRAINT predictive_maintenance_models_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: stock_adjustments stock_adjustments_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventory(id);


--
-- Name: stock_adjustments stock_adjustments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stocktake_items stocktake_items_counted_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktake_items
    ADD CONSTRAINT stocktake_items_counted_by_user_id_fkey FOREIGN KEY (counted_by_user_id) REFERENCES public.users(id);


--
-- Name: stocktake_items stocktake_items_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktake_items
    ADD CONSTRAINT stocktake_items_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: stocktake_items stocktake_items_stocktake_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktake_items
    ADD CONSTRAINT stocktake_items_stocktake_id_fkey FOREIGN KEY (stocktake_id) REFERENCES public.stocktakes(id) ON DELETE CASCADE;


--
-- Name: stocktakes stocktakes_completed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktakes
    ADD CONSTRAINT stocktakes_completed_by_user_id_fkey FOREIGN KEY (completed_by_user_id) REFERENCES public.users(id);


--
-- Name: stocktakes stocktakes_scheduled_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktakes
    ADD CONSTRAINT stocktakes_scheduled_by_user_id_fkey FOREIGN KEY (scheduled_by_user_id) REFERENCES public.users(id);


--
-- Name: stocktakes stocktakes_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.stocktakes
    ADD CONSTRAINT stocktakes_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: supplier_order_items supplier_order_items_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.supplier_order_items
    ADD CONSTRAINT supplier_order_items_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: supplier_order_items supplier_order_items_supplier_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.supplier_order_items
    ADD CONSTRAINT supplier_order_items_supplier_order_id_fkey FOREIGN KEY (supplier_order_id) REFERENCES public.supplier_orders(id);


--
-- Name: supplier_orders supplier_orders_ordering_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.supplier_orders
    ADD CONSTRAINT supplier_orders_ordering_organization_id_fkey FOREIGN KEY (ordering_organization_id) REFERENCES public.organizations(id);


--
-- Name: system_configurations system_configurations_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.system_configurations
    ADD CONSTRAINT system_configurations_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: system_configurations system_configurations_updated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.system_configurations
    ADD CONSTRAINT system_configurations_updated_by_user_id_fkey FOREIGN KEY (updated_by_user_id) REFERENCES public.users(id);


--
-- Name: transaction_approvals transaction_approvals_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transaction_approvals
    ADD CONSTRAINT transaction_approvals_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.users(id);


--
-- Name: transaction_approvals transaction_approvals_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transaction_approvals
    ADD CONSTRAINT transaction_approvals_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.transactions(id);


--
-- Name: transactions transactions_from_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_from_warehouse_id_fkey FOREIGN KEY (from_warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: transactions transactions_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.machines(id);


--
-- Name: transactions transactions_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.parts(id);


--
-- Name: transactions transactions_performed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_performed_by_user_id_fkey FOREIGN KEY (performed_by_user_id) REFERENCES public.users(id);


--
-- Name: transactions transactions_to_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_to_warehouse_id_fkey FOREIGN KEY (to_warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: user_management_audit_logs user_management_audit_logs_performed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.user_management_audit_logs
    ADD CONSTRAINT user_management_audit_logs_performed_by_user_id_fkey FOREIGN KEY (performed_by_user_id) REFERENCES public.users(id);


--
-- Name: user_management_audit_logs user_management_audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.user_management_audit_logs
    ADD CONSTRAINT user_management_audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_invited_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_invited_by_user_id_fkey FOREIGN KEY (invited_by_user_id) REFERENCES public.users(id);


--
-- Name: users users_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: warehouses warehouses_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abparts_user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- PostgreSQL database dump complete
--

\unrestrict w5I08gy0xqu20Z9QKaAKtxzvDvQ7TQ295A8P4RyLjpSRug4iTeC3dzjJgi0Nw8M

