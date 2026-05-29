-- Create suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    contact_email VARCHAR(100)
);

-- Create inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    purchase_order_id VARCHAR(50) UNIQUE NOT NULL,
    supplier_id VARCHAR(20) REFERENCES suppliers(supplier_id),
    store_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    units_ordered INTEGER NOT NULL,
    units_received INTEGER NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    current_stock INTEGER NOT NULL,
    reorder_threshold INTEGER NOT NULL,
    warehouse_location VARCHAR(50),
    delivery_date DATE,
    delivery_status VARCHAR(20),
    delivery_cost DECIMAL(10,2),
    last_restocked_date DATE
);

-- Seed suppliers
INSERT INTO suppliers VALUES
    ('SUP_001', 'Zimbabwe Grain Board', 'Zimbabwe', 'orders@zgb.co.zw'),
    ('SUP_002', 'Olivine Industries', 'Zimbabwe', 'supply@olivine.co.zw'),
    ('SUP_003', 'Cairns Foods', 'Zimbabwe', 'logistics@cairns.co.zw'),
    ('SUP_004', 'Dairiboard Zimbabwe', 'Zimbabwe', 'orders@dairiboard.co.zw');

-- Seed inventory
INSERT INTO inventory (
    purchase_order_id, supplier_id, store_id, product_id, product_name,
    units_ordered, units_received, unit_cost, total_cost, current_stock,
    reorder_threshold, warehouse_location, delivery_date, delivery_status,
    delivery_cost, last_restocked_date
) VALUES
    ('PO_001', 'SUP_001', 'STORE_001', 'SKU_001', 'Maize Meal 10kg',
     500, 500, 8.50, 4250.00, 320, 100, 'Harare Central', '2026-05-20', 'delivered', 150.00, '2026-05-20'),

    ('PO_002', 'SUP_001', 'STORE_002', 'SKU_001', 'Maize Meal 10kg',
     400, 380, 8.50, 3230.00, 95, 100, 'Bulawayo West', '2026-05-21', 'delivered', 120.00, '2026-05-21'),

    ('PO_003', 'SUP_002', 'STORE_001', 'SKU_002', 'Cooking Oil 2L',
     300, 300, 5.20, 1560.00, 210, 80, 'Harare Central', '2026-05-22', 'delivered', 90.00, '2026-05-22'),

    ('PO_004', 'SUP_003', 'STORE_003', 'SKU_003', 'Rice 5kg',
     600, 600, 6.30, 3780.00, 450, 120, 'Mutare East', '2026-05-23', 'delivered', 180.00, '2026-05-23'),

    ('PO_005', 'SUP_003', 'STORE_002', 'SKU_003', 'Rice 5kg',
     200, 150, 6.30, 945.00, 60, 80, 'Bulawayo West', '2026-05-24', 'delivered', 75.00, '2026-05-24'),

    ('PO_006', 'SUP_004', 'STORE_001', 'SKU_006', 'Milk 1L',
     1000, 1000, 1.20, 1200.00, 45, 150, 'Harare Central', '2026-05-25', 'delivered', 50.00, '2026-05-25'),

    ('PO_007', 'SUP_001', 'STORE_003', 'SKU_004', 'Sugar 2kg',
     350, 350, 3.10, 1085.00, 280, 90, 'Mutare East', '2026-05-26', 'delivered', 95.00, '2026-05-26'),

    ('PO_008', 'SUP_002', 'STORE_001', 'SKU_005', 'Bread Loaf',
     800, 790, 1.50, 1185.00, 310, 200, 'Harare Central', '2026-05-27', 'delivered', 60.00, '2026-05-27'),

    ('PO_009', 'SUP_003', 'STORE_002', 'SKU_007', 'Eggs 6 pack',
     400, 400, 2.20, 880.00, 30, 100, 'Bulawayo West', '2026-05-28', 'in_transit', 110.00, '2026-04-15'),

    ('PO_010', 'SUP_004', 'STORE_003', 'SKU_008', 'Chicken 1kg',
     250, 0, 4.50, 0.00, 15, 50, 'Mutare East', '2026-05-29', 'ordered', 85.00, '2026-04-20');
