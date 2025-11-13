"""Data integration and cleansing module for demand forecasting.

Provides mock data generation and data cleansing capabilities.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def generate_mock_sales_data(
    product_id: str,
    start_date: datetime,
    days: int = 365,
    base_demand: float = 100.0,
    seasonal_amplitude: float = 20.0,
    trend: float = 0.1,
    noise_level: float = 10.0,
    promotional_days: List[datetime] | None = None,
    promotional_boost: float = 1.5,
) -> pd.DataFrame:
    """Generate mock historical sales data with realistic patterns.

    Args:
        product_id: Unique identifier for the product
        start_date: Starting date for the data
        days: Number of days of data to generate
        base_demand: Base daily demand level
        seasonal_amplitude: Amplitude of seasonal variation
        trend: Daily trend coefficient
        noise_level: Standard deviation of random noise
        promotional_days: List of dates with promotions
        promotional_boost: Multiplier for demand during promotions

    Returns:
        DataFrame with columns: date, product_id, sales, price, promotion
    """
    dates = [start_date + timedelta(days=i) for i in range(days)]
    promotional_set = set(promotional_days) if promotional_days else set()

    sales_data = []
    for i, date in enumerate(dates):
        # Base demand with trend
        demand = base_demand + (trend * i)

        # Seasonal component (yearly cycle)
        day_of_year = date.timetuple().tm_yday
        seasonal = seasonal_amplitude * np.sin(2 * np.pi * day_of_year / 365.25)

        # Weekly pattern (lower on weekends)
        day_of_week = date.weekday()
        weekly_factor = 0.8 if day_of_week >= 5 else 1.0

        # Promotional boost
        promo_factor = promotional_boost if date in promotional_set else 1.0

        # Random noise
        noise = np.random.normal(0, noise_level)

        # Calculate final sales
        sales = max(0, (demand + seasonal) * weekly_factor * promo_factor + noise)

        # Generate price (with occasional discounts during promotions)
        base_price = 50.0
        price = base_price * (0.8 if date in promotional_set else 1.0)

        sales_data.append({
            "date": date,
            "product_id": product_id,
            "sales": round(sales, 2),
            "price": round(price, 2),
            "promotion": 1 if date in promotional_set else 0,
        })

    return pd.DataFrame(sales_data)


def cleanse_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate sales data.

    Args:
        df: Raw sales data DataFrame

    Returns:
        Cleaned DataFrame with validated data
    """
    df_clean = df.copy()

    # Remove negative sales
    df_clean = df_clean[df_clean["sales"] >= 0]

    # Handle missing values
    df_clean = df_clean.dropna(subset=["date", "product_id", "sales"])

    # Remove outliers using IQR method
    if len(df_clean) > 0:
        Q1 = df_clean["sales"].quantile(0.25)
        Q3 = df_clean["sales"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Keep outliers but flag them (for now, we keep them)
        # df_clean = df_clean[
        #     (df_clean["sales"] >= lower_bound) & (df_clean["sales"] <= upper_bound)
        # ]

    # Ensure date is datetime
    df_clean["date"] = pd.to_datetime(df_clean["date"])

    # Sort by date
    df_clean = df_clean.sort_values("date").reset_index(drop=True)

    return df_clean


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate data quality and return validation report.

    Args:
        df: Sales data DataFrame to validate

    Returns:
        Dictionary with validation results
    """
    report = {
        "is_valid": True,
        "total_records": len(df),
        "missing_values": df.isnull().sum().to_dict(),
        "negative_sales": (df["sales"] < 0).sum() if "sales" in df.columns else 0,
        "date_range": None,
        "unique_products": 0,
    }

    if len(df) == 0:
        report["is_valid"] = False
        report["error"] = "Empty dataset"
        return report

    if "date" in df.columns:
        report["date_range"] = {
            "start": df["date"].min().isoformat() if pd.notna(df["date"].min()) else None,
            "end": df["date"].max().isoformat() if pd.notna(df["date"].max()) else None,
        }

    if "product_id" in df.columns:
        report["unique_products"] = df["product_id"].nunique()

    if report["negative_sales"] > 0:
        report["is_valid"] = False
        report["error"] = f"Found {report['negative_sales']} records with negative sales"

    if report["total_records"] < 30:
        report["is_valid"] = False
        report["error"] = "Insufficient data (need at least 30 records)"

    return report


def generate_mock_product_info(product_ids: List[str]) -> pd.DataFrame:
    """Generate mock product information.

    Args:
        product_ids: List of product identifiers

    Returns:
        DataFrame with product information
    """
    categories = ["Electronics", "Clothing", "Food", "Home", "Sports"]
    data = []
    for product_id in product_ids:
        data.append({
            "product_id": product_id,
            "category": random.choice(categories),
            "launch_date": datetime.now() - timedelta(days=random.randint(30, 1000)),
            "base_price": round(random.uniform(20, 200), 2),
        })
    return pd.DataFrame(data)


def generate_mock_competitor_data(
    product_id: str,
    start_date: datetime,
    days: int = 365,
) -> pd.DataFrame:
    """Generate mock competitor data.

    Args:
        product_id: Product identifier
        start_date: Starting date
        days: Number of days

    Returns:
        DataFrame with competitor information
    """
    dates = [start_date + timedelta(days=i) for i in range(days)]
    competitors = ["Competitor A", "Competitor B", "Competitor C"]

    data = []
    for date in dates:
        # Random competitor actions
        if random.random() < 0.1:  # 10% chance of competitor action
            competitor = random.choice(competitors)
            action_type = random.choice(["price_change", "new_product", "promotion"])

            data.append({
                "date": date,
                "product_id": product_id,
                "competitor": competitor,
                "action_type": action_type,
                "impact_score": round(random.uniform(0.5, 2.0), 2),
            })

    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["date", "product_id", "competitor", "action_type", "impact_score"]
    )

