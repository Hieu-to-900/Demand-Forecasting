"""EV Inverter specific data generator."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import sys
from pathlib import Path

# Add src to path to import agent modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from agent.data_integration import (
    cleanse_data,
    generate_mock_competitor_data,
    generate_mock_product_info,
    generate_mock_sales_data,
)


def generate_ev_inverter_data(
    start_date: datetime | None = None,
    days: int = 365,
) -> dict:
    """Generate mock data specifically for Denso EV Inverter.

    Args:
        start_date: Starting date for data generation
        days: Number of days of historical data

    Returns:
        Dictionary with historical_data, product_info, and competitor_data
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=days)

    product_id = "DENSO_EV_INVERTER"

    # EV Inverter specific parameters
    # Higher base demand due to EV market growth
    base_demand = 175.0  # 150-200 range, using middle
    # Stronger seasonal pattern for automotive (Q2-Q3 peak)
    seasonal_amplitude = 35.0
    # Positive trend reflecting EV market growth
    trend = 0.15
    # Lower noise (more predictable for B2B automotive)
    noise_level = 8.0

    # Quarterly promotions aligned with automotive seasons
    promotional_dates = []
    for quarter_start in [0, 90, 180, 270]:
        promo_date = start_date + timedelta(days=quarter_start + random.randint(0, 15))
        promotional_dates.append(promo_date)

    # Generate sales data
    df = generate_mock_sales_data(
        product_id=product_id,
        start_date=start_date,
        days=days,
        base_demand=base_demand,
        seasonal_amplitude=seasonal_amplitude,
        trend=trend,
        noise_level=noise_level,
        promotional_days=promotional_dates,
        promotional_boost=1.4,  # Moderate boost for B2B
    )

    # Adjust prices for automotive component pricing ($800-1200)
    base_price = 1000.0
    df["price"] = base_price * (0.85 if df["promotion"] == 1 else 1.0)

    # Cleanse data
    df_clean = cleanse_data(df)

    # Generate product info with EV Inverter specifics
    product_info_data = [{
        "product_id": product_id,
        "category": "Automotive Electronics",
        "name": "Denso EV Inverter",
        "launch_date": start_date - timedelta(days=730),  # Launched 2 years ago
        "base_price": base_price,
        "description": "High-performance EV inverter for electric vehicles",
    }]
    product_info = pd.DataFrame(product_info_data)

    # Generate competitor data
    competitor_data = generate_mock_competitor_data(
        product_id=product_id,
        start_date=start_date,
        days=days,
    )

    return {
        "historical_data": df_clean,
        "product_info": product_info,
        "competitor_data": competitor_data,
        "product_id": product_id,
    }

