"""Mock product data for category-based batching - MVP with 2 categories.

Categories:
1. Spark Plugs (Bugi): 2 products
2. Air Conditioning System: 3 products
"""

from typing import Dict, List, Any

# Category definitions with product mappings
CATEGORY_PRODUCTS = {
    "Spark_Plugs": {
        "category_name": "Spark Plugs",
        "category_name_vi": "Bugi Ô Tô",
        "description": "Automotive spark plugs for ignition systems",
        "products": [
            {
                "product_code": "BUGI-IRIDIUM-VCH20",
                "product_name": "Bugi Ô Tô Iridium Tough VCH20",
                "denso_code": "MW267700-7671",
                "full_name": "Bugi Ô Tô Iridium Tough VCH20 - Mã MW267700-7671",
                "category": "Spark_Plugs",
                "subcategory": "Iridium Spark Plug",
                "unit_price": 450000,  # VND
                "manufacturer": "DENSO Japan",
                "application": "High-performance vehicles, Toyota, Honda, Mazda",
                "historical_sales": [
                    {"period": "2024-07", "quantity": 850, "revenue": 382500000},
                    {"period": "2024-08", "quantity": 920, "revenue": 414000000},
                    {"period": "2024-09", "quantity": 980, "revenue": 441000000},
                    {"period": "2024-10", "quantity": 1050, "revenue": 472500000},
                    {"period": "2024-11", "quantity": 1120, "revenue": 504000000},
                    {"period": "2024-12", "quantity": 1200, "revenue": 540000000},
                ],
                "inventory": {
                    "current_stock": 2500,
                    "safety_stock": 800,
                    "reorder_point": 1000,
                    "warehouse": "Hanoi Distribution Center",
                    "lead_time_days": 30,
                },
            },
            {
                "product_code": "BUGI-PLATIN-PK16TT",
                "product_name": "Bugi Ô Tô Platin PK16TT",
                "denso_code": "267700-6320",
                "full_name": "Bugi Ô Tô Platin PK16TT - Mã sản phẩm: 267700-6320",
                "category": "Spark_Plugs",
                "subcategory": "Platinum Spark Plug",
                "unit_price": 320000,  # VND
                "manufacturer": "DENSO Japan",
                "application": "Standard vehicles, Toyota, Honda, Nissan",
                "historical_sales": [
                    {"period": "2024-07", "quantity": 1200, "revenue": 384000000},
                    {"period": "2024-08", "quantity": 1280, "revenue": 409600000},
                    {"period": "2024-09", "quantity": 1350, "revenue": 432000000},
                    {"period": "2024-10", "quantity": 1420, "revenue": 454400000},
                    {"period": "2024-11", "quantity": 1500, "revenue": 480000000},
                    {"period": "2024-12", "quantity": 1580, "revenue": 505600000},
                ],
                "inventory": {
                    "current_stock": 3200,
                    "safety_stock": 1000,
                    "reorder_point": 1200,
                    "warehouse": "Hanoi Distribution Center",
                    "lead_time_days": 30,
                },
            },
        ],
    },
    "AC_System": {
        "category_name": "Air Conditioning System",
        "category_name_vi": "Hệ Thống Điều Hòa",
        "description": "Automotive air conditioning components",
        "products": [
            {
                "product_code": "AC-COMPRESSOR-6SEU14C",
                "product_name": "Máy Nén Điều Hòa 6SEU14C",
                "denso_code": "447220-9700",
                "full_name": "Máy Nén Điều Hòa DENSO 6SEU14C - Mã 447220-9700",
                "category": "AC_System",
                "subcategory": "AC Compressor",
                "unit_price": 4500000,  # VND
                "manufacturer": "DENSO Thailand",
                "application": "Toyota Camry, Honda Accord, Mazda 6",
                "historical_sales": [
                    {"period": "2024-07", "quantity": 180, "revenue": 810000000},
                    {"period": "2024-08", "quantity": 195, "revenue": 877500000},
                    {"period": "2024-09", "quantity": 210, "revenue": 945000000},
                    {"period": "2024-10", "quantity": 225, "revenue": 1012500000},
                    {"period": "2024-11", "quantity": 240, "revenue": 1080000000},
                    {"period": "2024-12", "quantity": 260, "revenue": 1170000000},
                ],
                "inventory": {
                    "current_stock": 450,
                    "safety_stock": 150,
                    "reorder_point": 200,
                    "warehouse": "Ho Chi Minh Distribution Center",
                    "lead_time_days": 45,
                },
            },
            {
                "product_code": "AC-EVAPORATOR-CORE",
                "product_name": "Giàn Lạnh (Evaporator)",
                "denso_code": "447500-2890",
                "full_name": "Giàn Lạnh Điều Hòa DENSO - Mã 447500-2890",
                "category": "AC_System",
                "subcategory": "Evaporator",
                "unit_price": 2800000,  # VND
                "manufacturer": "DENSO Thailand",
                "application": "Toyota Vios, Honda City, Mazda 3",
                "historical_sales": [
                    {"period": "2024-07", "quantity": 320, "revenue": 896000000},
                    {"period": "2024-08", "quantity": 340, "revenue": 952000000},
                    {"period": "2024-09", "quantity": 360, "revenue": 1008000000},
                    {"period": "2024-10", "quantity": 380, "revenue": 1064000000},
                    {"period": "2024-11", "quantity": 400, "revenue": 1120000000},
                    {"period": "2024-12", "quantity": 420, "revenue": 1176000000},
                ],
                "inventory": {
                    "current_stock": 850,
                    "safety_stock": 300,
                    "reorder_point": 400,
                    "warehouse": "Ho Chi Minh Distribution Center",
                    "lead_time_days": 40,
                },
            },
            {
                "product_code": "AC-CONDENSER-CORE",
                "product_name": "Giàn Nóng (Condenser)",
                "denso_code": "447700-1450",
                "full_name": "Giàn Nóng Điều Hòa DENSO - Mã 447700-1450",
                "category": "AC_System",
                "subcategory": "Condenser",
                "unit_price": 3200000,  # VND
                "manufacturer": "DENSO Thailand",
                "application": "Toyota Corolla, Honda Civic, Mazda CX-5",
                "historical_sales": [
                    {"period": "2024-07", "quantity": 280, "revenue": 896000000},
                    {"period": "2024-08", "quantity": 300, "revenue": 960000000},
                    {"period": "2024-09", "quantity": 320, "revenue": 1024000000},
                    {"period": "2024-10", "quantity": 340, "revenue": 1088000000},
                    {"period": "2024-11", "quantity": 360, "revenue": 1152000000},
                    {"period": "2024-12", "quantity": 380, "revenue": 1216000000},
                ],
                "inventory": {
                    "current_stock": 720,
                    "safety_stock": 250,
                    "reorder_point": 350,
                    "warehouse": "Ho Chi Minh Distribution Center",
                    "lead_time_days": 40,
                },
            },
        ],
    },
}


def get_all_categories() -> List[str]:
    """Get list of all product categories."""
    return list(CATEGORY_PRODUCTS.keys())


def get_category_info(category: str) -> Dict[str, Any]:
    """Get category information."""
    return CATEGORY_PRODUCTS.get(category, {})


def get_products_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all products in a category."""
    category_data = CATEGORY_PRODUCTS.get(category, {})
    return category_data.get("products", [])


def get_all_product_codes() -> List[str]:
    """Get all product codes across all categories."""
    codes = []
    for category_data in CATEGORY_PRODUCTS.values():
        for product in category_data.get("products", []):
            codes.append(product["product_code"])
    return codes


def get_product_by_code(product_code: str) -> Dict[str, Any]:
    """Get product data by product code."""
    for category_data in CATEGORY_PRODUCTS.values():
        for product in category_data.get("products", []):
            if product["product_code"] == product_code:
                return product
    raise ValueError(f"Product code {product_code} not found")


def get_category_for_product(product_code: str) -> str:
    """Get category for a product code."""
    product = get_product_by_code(product_code)
    return product["category"]
