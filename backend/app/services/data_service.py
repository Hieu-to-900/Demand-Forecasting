"""Data service for generating and managing product data."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import pandas as pd

from app.utils.data_generator import generate_ev_inverter_data


class DataService:
    """Service for managing product data."""

    @staticmethod
    def get_ev_inverter_data(
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        days: int = 365,
    ) -> Dict[str, Any]:
        """Get EV Inverter data, optionally filtered by date range.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            days: Number of days of historical data to generate

        Returns:
            Dictionary with historical_data, product_info, competitor_data
        """
        data = generate_ev_inverter_data(start_date=start_date, days=days)

        # Filter by date range if provided
        if start_date or end_date:
            df = data["historical_data"]
            if start_date:
                df = df[df["date"] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df["date"] <= pd.to_datetime(end_date)]
            data["historical_data"] = df

        return data

    @staticmethod
    def get_products() -> list[Dict[str, Any]]:
        """Get list of available products.

        Returns:
            List of product dictionaries
        """
        return [{
            "product_id": "DENSO_EV_INVERTER",
            "name": "Denso EV Inverter",
            "category": "Automotive Electronics",
        }]

