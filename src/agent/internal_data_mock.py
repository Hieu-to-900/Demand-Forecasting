"""Mock internal data for 5 EV Inverter products - Realistic structure for demo.

This module provides mock internal data that simulates what would come from
a PostgreSQL + TimescaleDB database in production.
"""

from typing import Dict, List, Any
import math


def generate_sales_trend(base_quantity: int, months: int = 36, growth_rate: float = 0.02, seasonal_factor: float = 0.1) -> List[Dict[str, Any]]:
    """Generate realistic sales data with trend and seasonality.
    
    Args:
        base_quantity: Starting monthly quantity
        months: Number of months to generate
        growth_rate: Monthly growth rate (e.g., 0.02 = 2% per month)
        seasonal_factor: Seasonal variation factor
        
    Returns:
        List of sales dictionaries with period, quantity, and revenue
    """
    sales = []
    year = 2022
    month = 1
    
    for i in range(months):
        # Calculate trend (exponential growth)
        trend_quantity = base_quantity * (1 + growth_rate) ** i
        
        # Add seasonal variation (higher in Q4, lower in Q1)
        seasonal_multiplier = 1.0
        if (month - 1) % 12 in [9, 10, 11]:  # Q4 (Oct, Nov, Dec)
            seasonal_multiplier = 1 + seasonal_factor
        elif (month - 1) % 12 in [0, 1, 2]:  # Q1 (Jan, Feb, Mar)
            seasonal_multiplier = 1 - seasonal_factor * 0.5
        
        # Add some random variation (±5%)
        variation = 1.0 + (i % 7 - 3) * 0.015  # Pseudo-random variation
        
        quantity = int(trend_quantity * seasonal_multiplier * variation)
        
        # Format period as YYYY-MM
        period = f"{year}-{month:02d}"
        sales.append({
            "period": period,
            "quantity": max(quantity, 10),  # Ensure minimum quantity
            "revenue": 0.0  # Will be calculated by product
        })
        
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return sales


# Mock database data structure
INTERNAL_PRODUCT_DATA = {
    "INV-001": {
        # Product Master Data
        "product_code": "INV-001",
        "product_name": "Denso EV Power Inverter 150kW",
        "category": "Power Electronics",
        "subcategory": "Traction Inverter",
        "unit_price": 1250.00,
        "unit_of_measure": "unit",
        "supplier_id": "SUP-DENSO-001",
        "manufacturing_location": "Japan",
        "product_lifecycle": "mature",
        "launch_date": "2020-01-15",
        
        # Historical Sales (36 months - Jan 2022 to Dec 2024)
        "historical_sales": [
            {"period": "2022-01", "quantity": 850, "revenue": 1062500.00},
            {"period": "2022-02", "quantity": 820, "revenue": 1025000.00},
            {"period": "2022-03", "quantity": 880, "revenue": 1100000.00},
            {"period": "2022-04", "quantity": 920, "revenue": 1150000.00},
            {"period": "2022-05", "quantity": 950, "revenue": 1187500.00},
            {"period": "2022-06", "quantity": 980, "revenue": 1225000.00},
            {"period": "2022-07", "quantity": 1000, "revenue": 1250000.00},
            {"period": "2022-08", "quantity": 1020, "revenue": 1275000.00},
            {"period": "2022-09", "quantity": 1050, "revenue": 1312500.00},
            {"period": "2022-10", "quantity": 1100, "revenue": 1375000.00},
            {"period": "2022-11", "quantity": 1120, "revenue": 1400000.00},
            {"period": "2022-12", "quantity": 1150, "revenue": 1437500.00},
            {"period": "2023-01", "quantity": 1000, "revenue": 1250000.00},
            {"period": "2023-02", "quantity": 1050, "revenue": 1312500.00},
            {"period": "2023-03", "quantity": 1100, "revenue": 1375000.00},
            {"period": "2023-04", "quantity": 1120, "revenue": 1400000.00},
            {"period": "2023-05", "quantity": 1150, "revenue": 1437500.00},
            {"period": "2023-06", "quantity": 1180, "revenue": 1475000.00},
            {"period": "2023-07", "quantity": 1200, "revenue": 1500000.00},
            {"period": "2023-08", "quantity": 1220, "revenue": 1525000.00},
            {"period": "2023-09", "quantity": 1250, "revenue": 1562500.00},
            {"period": "2023-10", "quantity": 1300, "revenue": 1625000.00},
            {"period": "2023-11", "quantity": 1320, "revenue": 1650000.00},
            {"period": "2023-12", "quantity": 1350, "revenue": 1687500.00},
            {"period": "2024-01", "quantity": 1250, "revenue": 1562500.00},
            {"period": "2024-02", "quantity": 1180, "revenue": 1475000.00},
            {"period": "2024-03", "quantity": 1320, "revenue": 1650000.00},
            {"period": "2024-04", "quantity": 1400, "revenue": 1750000.00},
            {"period": "2024-05", "quantity": 1450, "revenue": 1812500.00},
            {"period": "2024-06", "quantity": 1500, "revenue": 1875000.00},
            {"period": "2024-07", "quantity": 1480, "revenue": 1850000.00},
            {"period": "2024-08", "quantity": 1550, "revenue": 1937500.00},
            {"period": "2024-09", "quantity": 1620, "revenue": 2025000.00},
            {"period": "2024-10", "quantity": 1680, "revenue": 2100000.00},
            {"period": "2024-11", "quantity": 1750, "revenue": 2187500.00},
            {"period": "2024-12", "quantity": 1800, "revenue": 2250000.00},
        ],
        
        # Inventory Data
        "inventory_levels": {
            "current_stock": 3200,
            "safety_stock": 1500,
            "reorder_point": 2000,
            "max_stock": 5000,
            "warehouse_location": "Tokyo Main Warehouse",
            "lead_time_days": 45,
            "stock_status": "adequate",
            "last_updated": "2024-12-15T10:00:00"
        },
        
        # Production Plans (next 3 months)
        "production_plans": [
            {"period": "2025-01", "planned_quantity": 1900, "production_line": "Line-A", "status": "confirmed"},
            {"period": "2025-02", "planned_quantity": 2000, "production_line": "Line-A", "status": "confirmed"},
            {"period": "2025-03", "planned_quantity": 2100, "production_line": "Line-A", "status": "draft"},
        ],
        
        # Additional Business Metrics
        "quality_metrics": {
            "defect_rate": 0.002,  # 0.2%
            "customer_satisfaction": 4.7,
            "warranty_claims": 12,
            "return_rate": 0.001
        },
        
        "market_segments": ["Premium EV", "Commercial EV"],
        "regions": ["Japan", "China", "EU", "North America"],
    },
    
    "INV-002": {
        "product_code": "INV-002",
        "product_name": "Denso EV Power Inverter 200kW",
        "category": "Power Electronics",
        "subcategory": "Traction Inverter",
        "unit_price": 1650.00,
        "unit_of_measure": "unit",
        "supplier_id": "SUP-DENSO-001",
        "manufacturing_location": "Japan",
        "product_lifecycle": "growth",
        "launch_date": "2022-06-20",
        
        "historical_sales": [
            {"period": "2022-01", "quantity": 0, "revenue": 0.00},  # Not launched yet
            {"period": "2022-02", "quantity": 0, "revenue": 0.00},
            {"period": "2022-03", "quantity": 0, "revenue": 0.00},
            {"period": "2022-04", "quantity": 0, "revenue": 0.00},
            {"period": "2022-05", "quantity": 0, "revenue": 0.00},
            {"period": "2022-06", "quantity": 50, "revenue": 82500.00},  # Launch month
            {"period": "2022-07", "quantity": 120, "revenue": 198000.00},
            {"period": "2022-08", "quantity": 180, "revenue": 297000.00},
            {"period": "2022-09", "quantity": 250, "revenue": 412500.00},
            {"period": "2022-10", "quantity": 320, "revenue": 528000.00},
            {"period": "2022-11", "quantity": 380, "revenue": 627000.00},
            {"period": "2022-12", "quantity": 450, "revenue": 742500.00},
            {"period": "2023-01", "quantity": 400, "revenue": 660000.00},
            {"period": "2023-02", "quantity": 450, "revenue": 742500.00},
            {"period": "2023-03", "quantity": 500, "revenue": 825000.00},
            {"period": "2023-04", "quantity": 550, "revenue": 907500.00},
            {"period": "2023-05", "quantity": 600, "revenue": 990000.00},
            {"period": "2023-06", "quantity": 650, "revenue": 1072500.00},
            {"period": "2023-07", "quantity": 700, "revenue": 1155000.00},
            {"period": "2023-08", "quantity": 750, "revenue": 1237500.00},
            {"period": "2023-09", "quantity": 800, "revenue": 1320000.00},
            {"period": "2023-10", "quantity": 900, "revenue": 1485000.00},
            {"period": "2023-11", "quantity": 950, "revenue": 1567500.00},
            {"period": "2023-12", "quantity": 1000, "revenue": 1650000.00},
            {"period": "2024-01", "quantity": 850, "revenue": 1402500.00},
            {"period": "2024-02", "quantity": 920, "revenue": 1518000.00},
            {"period": "2024-03", "quantity": 980, "revenue": 1617000.00},
            {"period": "2024-04", "quantity": 1050, "revenue": 1732500.00},
            {"period": "2024-05", "quantity": 1120, "revenue": 1848000.00},
            {"period": "2024-06", "quantity": 1180, "revenue": 1947000.00},
            {"period": "2024-07", "quantity": 1200, "revenue": 1980000.00},
            {"period": "2024-08", "quantity": 1250, "revenue": 2062500.00},
            {"period": "2024-09", "quantity": 1320, "revenue": 2178000.00},
            {"period": "2024-10", "quantity": 1400, "revenue": 2310000.00},
            {"period": "2024-11", "quantity": 1480, "revenue": 2442000.00},
            {"period": "2024-12", "quantity": 1550, "revenue": 2557500.00},
        ],
        
        "inventory_levels": {
            "current_stock": 2400,
            "safety_stock": 1200,
            "reorder_point": 1500,
            "max_stock": 4000,
            "warehouse_location": "Tokyo Main Warehouse",
            "lead_time_days": 50,
            "stock_status": "adequate",
            "last_updated": "2024-12-15T10:00:00"
        },
        
        "production_plans": [
            {"period": "2025-01", "planned_quantity": 1650, "production_line": "Line-B", "status": "confirmed"},
            {"period": "2025-02", "planned_quantity": 1750, "production_line": "Line-B", "status": "confirmed"},
            {"period": "2025-03", "planned_quantity": 1850, "production_line": "Line-B", "status": "draft"},
        ],
        
        "quality_metrics": {
            "defect_rate": 0.0015,
            "customer_satisfaction": 4.8,
            "warranty_claims": 8,
            "return_rate": 0.0008
        },
        
        "market_segments": ["Premium EV", "Performance EV"],
        "regions": ["Japan", "EU", "North America"],
    },
    
    "INV-003": {
        "product_code": "INV-003",
        "product_name": "Denso EV Power Inverter 100kW Compact",
        "category": "Power Electronics",
        "subcategory": "Traction Inverter",
        "unit_price": 980.00,
        "unit_of_measure": "unit",
        "supplier_id": "SUP-DENSO-001",
        "manufacturing_location": "Thailand",
        "product_lifecycle": "mature",
        "launch_date": "2019-03-10",
        
        "historical_sales": [
            {"period": "2022-01", "quantity": 1500, "revenue": 1470000.00},
            {"period": "2022-02", "quantity": 1450, "revenue": 1421000.00},
            {"period": "2022-03", "quantity": 1600, "revenue": 1568000.00},
            {"period": "2022-04", "quantity": 1650, "revenue": 1617000.00},
            {"period": "2022-05", "quantity": 1700, "revenue": 1666000.00},
            {"period": "2022-06", "quantity": 1750, "revenue": 1715000.00},
            {"period": "2022-07", "quantity": 1800, "revenue": 1764000.00},
            {"period": "2022-08", "quantity": 1850, "revenue": 1813000.00},
            {"period": "2022-09", "quantity": 1900, "revenue": 1862000.00},
            {"period": "2022-10", "quantity": 2000, "revenue": 1960000.00},
            {"period": "2022-11", "quantity": 2050, "revenue": 2009000.00},
            {"period": "2022-12", "quantity": 2100, "revenue": 2058000.00},
            {"period": "2023-01", "quantity": 1900, "revenue": 1862000.00},
            {"period": "2023-02", "quantity": 1950, "revenue": 1911000.00},
            {"period": "2023-03", "quantity": 2000, "revenue": 1960000.00},
            {"period": "2023-04", "quantity": 2050, "revenue": 2009000.00},
            {"period": "2023-05", "quantity": 2100, "revenue": 2058000.00},
            {"period": "2023-06", "quantity": 2150, "revenue": 2107000.00},
            {"period": "2023-07", "quantity": 2200, "revenue": 2156000.00},
            {"period": "2023-08", "quantity": 2250, "revenue": 2205000.00},
            {"period": "2023-09", "quantity": 2300, "revenue": 2254000.00},
            {"period": "2023-10", "quantity": 2400, "revenue": 2352000.00},
            {"period": "2023-11", "quantity": 2450, "revenue": 2401000.00},
            {"period": "2023-12", "quantity": 2500, "revenue": 2450000.00},
            {"period": "2024-01", "quantity": 2100, "revenue": 2058000.00},
            {"period": "2024-02", "quantity": 2050, "revenue": 2009000.00},
            {"period": "2024-03", "quantity": 2200, "revenue": 2156000.00},
            {"period": "2024-04", "quantity": 2150, "revenue": 2107000.00},
            {"period": "2024-05", "quantity": 2300, "revenue": 2254000.00},
            {"period": "2024-06", "quantity": 2250, "revenue": 2205000.00},
            {"period": "2024-07", "quantity": 2400, "revenue": 2352000.00},
            {"period": "2024-08", "quantity": 2350, "revenue": 2303000.00},
            {"period": "2024-09", "quantity": 2500, "revenue": 2450000.00},
            {"period": "2024-10", "quantity": 2450, "revenue": 2401000.00},
            {"period": "2024-11", "quantity": 2600, "revenue": 2548000.00},
            {"period": "2024-12", "quantity": 2550, "revenue": 2499000.00},
        ],
        
        "inventory_levels": {
            "current_stock": 4800,
            "safety_stock": 2000,
            "reorder_point": 2500,
            "max_stock": 6000,
            "warehouse_location": "Bangkok Regional Warehouse",
            "lead_time_days": 30,
            "stock_status": "adequate",
            "last_updated": "2024-12-15T10:00:00"
        },
        
        "production_plans": [
            {"period": "2025-01", "planned_quantity": 2700, "production_line": "Line-C", "status": "confirmed"},
            {"period": "2025-02", "planned_quantity": 2800, "production_line": "Line-C", "status": "confirmed"},
            {"period": "2025-03", "planned_quantity": 2900, "production_line": "Line-C", "status": "draft"},
        ],
        
        "quality_metrics": {
            "defect_rate": 0.0025,
            "customer_satisfaction": 4.6,
            "warranty_claims": 15,
            "return_rate": 0.0012
        },
        
        "market_segments": ["Entry EV", "Compact EV", "Hybrid EV"],
        "regions": ["Asia-Pacific", "EU", "Latin America"],
    },
    
    "INV-004": {
        "product_code": "INV-004",
        "product_name": "Denso EV Power Inverter 300kW High-Performance",
        "category": "Power Electronics",
        "subcategory": "Traction Inverter",
        "unit_price": 2200.00,
        "unit_of_measure": "unit",
        "supplier_id": "SUP-DENSO-001",
        "manufacturing_location": "Japan",
        "product_lifecycle": "new",
        "launch_date": "2024-01-15",
        
        "historical_sales": [
            {"period": "2022-01", "quantity": 0, "revenue": 0.00},  # Not launched
            {"period": "2022-02", "quantity": 0, "revenue": 0.00},
            {"period": "2022-03", "quantity": 0, "revenue": 0.00},
            {"period": "2022-04", "quantity": 0, "revenue": 0.00},
            {"period": "2022-05", "quantity": 0, "revenue": 0.00},
            {"period": "2022-06", "quantity": 0, "revenue": 0.00},
            {"period": "2022-07", "quantity": 0, "revenue": 0.00},
            {"period": "2022-08", "quantity": 0, "revenue": 0.00},
            {"period": "2022-09", "quantity": 0, "revenue": 0.00},
            {"period": "2022-10", "quantity": 0, "revenue": 0.00},
            {"period": "2022-11", "quantity": 0, "revenue": 0.00},
            {"period": "2022-12", "quantity": 0, "revenue": 0.00},
            {"period": "2023-01", "quantity": 0, "revenue": 0.00},
            {"period": "2023-02", "quantity": 0, "revenue": 0.00},
            {"period": "2023-03", "quantity": 0, "revenue": 0.00},
            {"period": "2023-04", "quantity": 0, "revenue": 0.00},
            {"period": "2023-05", "quantity": 0, "revenue": 0.00},
            {"period": "2023-06", "quantity": 0, "revenue": 0.00},
            {"period": "2023-07", "quantity": 0, "revenue": 0.00},
            {"period": "2023-08", "quantity": 0, "revenue": 0.00},
            {"period": "2023-09", "quantity": 0, "revenue": 0.00},
            {"period": "2023-10", "quantity": 0, "revenue": 0.00},
            {"period": "2023-11", "quantity": 0, "revenue": 0.00},
            {"period": "2023-12", "quantity": 0, "revenue": 0.00},
            {"period": "2024-01", "quantity": 120, "revenue": 264000.00},  # Launch month
            {"period": "2024-02", "quantity": 180, "revenue": 396000.00},
            {"period": "2024-03", "quantity": 250, "revenue": 550000.00},
            {"period": "2024-04", "quantity": 320, "revenue": 704000.00},
            {"period": "2024-05", "quantity": 400, "revenue": 880000.00},
            {"period": "2024-06", "quantity": 480, "revenue": 1056000.00},
            {"period": "2024-07", "quantity": 550, "revenue": 1210000.00},
            {"period": "2024-08", "quantity": 620, "revenue": 1364000.00},
            {"period": "2024-09", "quantity": 700, "revenue": 1540000.00},
            {"period": "2024-10", "quantity": 780, "revenue": 1716000.00},
            {"period": "2024-11", "quantity": 850, "revenue": 1870000.00},
            {"period": "2024-12", "quantity": 920, "revenue": 2024000.00},
        ],
        
        "inventory_levels": {
            "current_stock": 800,
            "safety_stock": 400,
            "reorder_point": 500,
            "max_stock": 1500,
            "warehouse_location": "Tokyo Main Warehouse",
            "lead_time_days": 60,
            "stock_status": "low",
            "last_updated": "2024-12-15T10:00:00"
        },
        
        "production_plans": [
            {"period": "2025-01", "planned_quantity": 1000, "production_line": "Line-D", "status": "confirmed"},
            {"period": "2025-02", "planned_quantity": 1100, "production_line": "Line-D", "status": "confirmed"},
            {"period": "2025-03", "planned_quantity": 1200, "production_line": "Line-D", "status": "draft"},
        ],
        
        "quality_metrics": {
            "defect_rate": 0.003,
            "customer_satisfaction": 4.5,
            "warranty_claims": 5,
            "return_rate": 0.0015
        },
        
        "market_segments": ["Luxury EV", "Performance EV", "Racing EV"],
        "regions": ["Japan", "EU", "North America"],
    },
    
    "INV-005": {
        "product_code": "INV-005",
        "product_name": "Denso EV Power Inverter 80kW Entry-Level",
        "category": "Power Electronics",
        "subcategory": "Traction Inverter",
        "unit_price": 750.00,
        "unit_of_measure": "unit",
        "supplier_id": "SUP-DENSO-001",
        "manufacturing_location": "China",
        "product_lifecycle": "growth",
        "launch_date": "2023-05-10",
        
        "historical_sales": [
            {"period": "2022-01", "quantity": 0, "revenue": 0.00},  # Not launched
            {"period": "2022-02", "quantity": 0, "revenue": 0.00},
            {"period": "2022-03", "quantity": 0, "revenue": 0.00},
            {"period": "2022-04", "quantity": 0, "revenue": 0.00},
            {"period": "2022-05", "quantity": 0, "revenue": 0.00},
            {"period": "2022-06", "quantity": 0, "revenue": 0.00},
            {"period": "2022-07", "quantity": 0, "revenue": 0.00},
            {"period": "2022-08", "quantity": 0, "revenue": 0.00},
            {"period": "2022-09", "quantity": 0, "revenue": 0.00},
            {"period": "2022-10", "quantity": 0, "revenue": 0.00},
            {"period": "2022-11", "quantity": 0, "revenue": 0.00},
            {"period": "2022-12", "quantity": 0, "revenue": 0.00},
            {"period": "2023-01", "quantity": 0, "revenue": 0.00},
            {"period": "2023-02", "quantity": 0, "revenue": 0.00},
            {"period": "2023-03", "quantity": 0, "revenue": 0.00},
            {"period": "2023-04", "quantity": 0, "revenue": 0.00},
            {"period": "2023-05", "quantity": 200, "revenue": 150000.00},  # Launch month
            {"period": "2023-06", "quantity": 350, "revenue": 262500.00},
            {"period": "2023-07", "quantity": 500, "revenue": 375000.00},
            {"period": "2023-08", "quantity": 650, "revenue": 487500.00},
            {"period": "2023-09", "quantity": 800, "revenue": 600000.00},
            {"period": "2023-10", "quantity": 1000, "revenue": 750000.00},
            {"period": "2023-11", "quantity": 1200, "revenue": 900000.00},
            {"period": "2023-12", "quantity": 1400, "revenue": 1050000.00},
            {"period": "2024-01", "quantity": 1800, "revenue": 1350000.00},
            {"period": "2024-02", "quantity": 1950, "revenue": 1462500.00},
            {"period": "2024-03", "quantity": 2100, "revenue": 1575000.00},
            {"period": "2024-04", "quantity": 2250, "revenue": 1687500.00},
            {"period": "2024-05", "quantity": 2400, "revenue": 1800000.00},
            {"period": "2024-06", "quantity": 2550, "revenue": 1912500.00},
            {"period": "2024-07", "quantity": 2700, "revenue": 2025000.00},
            {"period": "2024-08", "quantity": 2850, "revenue": 2137500.00},
            {"period": "2024-09", "quantity": 3000, "revenue": 2250000.00},
            {"period": "2024-10", "quantity": 3150, "revenue": 2362500.00},
            {"period": "2024-11", "quantity": 3300, "revenue": 2475000.00},
            {"period": "2024-12", "quantity": 3450, "revenue": 2587500.00},
        ],
        
        "inventory_levels": {
            "current_stock": 5200,
            "safety_stock": 2500,
            "reorder_point": 3000,
            "max_stock": 7000,
            "warehouse_location": "Shanghai Regional Warehouse",
            "lead_time_days": 25,
            "stock_status": "adequate",
            "last_updated": "2024-12-15T10:00:00"
        },
        
        "production_plans": [
            {"period": "2025-01", "planned_quantity": 3600, "production_line": "Line-E", "status": "confirmed"},
            {"period": "2025-02", "planned_quantity": 3800, "production_line": "Line-E", "status": "confirmed"},
            {"period": "2025-03", "planned_quantity": 4000, "production_line": "Line-E", "status": "draft"},
        ],
        
        "quality_metrics": {
            "defect_rate": 0.003,
            "customer_satisfaction": 4.4,
            "warranty_claims": 20,
            "return_rate": 0.0015
        },
        
        "market_segments": ["Entry EV", "Budget EV", "Fleet EV"],
        "regions": ["China", "Asia-Pacific", "Latin America"],
    },
}

# Calculate revenue for all products
for product_code, product_data in INTERNAL_PRODUCT_DATA.items():
    unit_price = product_data["unit_price"]
    for sale in product_data["historical_sales"]:
        if sale["revenue"] == 0.0 and sale["quantity"] > 0:
            sale["revenue"] = sale["quantity"] * unit_price


def get_internal_data_for_product(product_code: str) -> Dict[str, Any]:
    """Get internal data for a specific product code.
    
    Args:
        product_code: Product code (e.g., "INV-001")
        
    Returns:
        Dictionary with internal data structure
        
    Raises:
        ValueError: If product code not found
    """
    if product_code not in INTERNAL_PRODUCT_DATA:
        raise ValueError(f"Product code {product_code} not found in internal data")
    
    return INTERNAL_PRODUCT_DATA[product_code]


def get_historical_sales_array(product_code: str, periods: int = 5) -> List[int]:
    """Get historical sales quantities as array (for forecasting).
    
    Args:
        product_code: Product code
        periods: Number of recent periods to return
        
    Returns:
        List of sales quantities (most recent first)
    """
    product_data = get_internal_data_for_product(product_code)
    sales = product_data["historical_sales"]
    # Return last N periods, most recent first
    return [s["quantity"] for s in sales[-periods:]]


def get_inventory_level(product_code: str) -> int:
    """Get current inventory level for product."""
    product_data = get_internal_data_for_product(product_code)
    return product_data["inventory_levels"]["current_stock"]


def get_production_plans_array(product_code: str) -> List[int]:
    """Get production plans as array."""
    product_data = get_internal_data_for_product(product_code)
    return [p["planned_quantity"] for p in product_data["production_plans"]]


def get_all_product_codes() -> List[str]:
    """Get list of all available product codes."""
    return list(INTERNAL_PRODUCT_DATA.keys())

