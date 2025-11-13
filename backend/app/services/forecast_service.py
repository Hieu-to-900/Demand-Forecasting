"""Forecast service for running LangGraph forecasting."""

from __future__ import annotations

from typing import Any, Dict

import sys
from pathlib import Path

# Add src to path to import agent modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from agent.graph import graph
from agent.types import Context, State


class ForecastService:
    """Service for running demand forecasting."""

    @staticmethod
    async def run_forecast(
        product_id: str,
        forecast_mode: str = "comprehensive",
        forecast_horizon_days: int = 30,
        historical_data: Any = None,
        product_info: Any = None,
        competitor_data: Any = None,
    ) -> Dict[str, Any]:
        """Run forecasting graph and return results.

        Args:
            product_id: Product identifier
            forecast_mode: Forecast mode (seasonal/comprehensive/promotional/new_product)
            forecast_horizon_days: Number of days to forecast ahead
            historical_data: Optional pre-generated historical data
            product_info: Optional product info
            competitor_data: Optional competitor data

        Returns:
            Dictionary with all forecast results
        """
        # Create context
        context: Context = {
            "forecast_mode": forecast_mode,
            "forecast_horizon_days": forecast_horizon_days,
            "llm_model": "gpt-4o-mini",
            "product_id": product_id,
            "new_product_id": None,
            "new_product_category": None,
        }

        # Create initial state
        state = State(
            product_id=product_id,
            historical_data=historical_data,
            product_info=product_info,
            competitor_data=competitor_data,
            forecast_mode=forecast_mode,
        )

        # Run the graph
        result = await graph.ainvoke(state, config={"configurable": context})

        # Extract and format results for frontend
        return {
            "product_id": product_id,
            "forecast_mode": forecast_mode,
            "forecast_horizon_days": forecast_horizon_days,
            "historical_data": ForecastService._format_dataframe(result.historical_data) if result.historical_data is not None else None,
            "pattern_analysis": result.pattern_analysis,
            "seasonal_forecast": result.seasonal_forecast,
            "new_product_forecast": result.new_product_forecast,
            "promotional_analysis": result.promotional_analysis,
            "promotional_demand": result.promotional_demand,
            "competitor_analysis": result.competitor_analysis,
            "competitor_adjusted_forecast": result.competitor_adjusted_forecast,
            "supply_chain_optimization": result.supply_chain_optimization,
            "scenario_planning": result.scenario_planning,
            "realtime_adjustment": result.realtime_adjustment,
        }

    @staticmethod
    def _format_dataframe(df: Any) -> list[Dict[str, Any]]:
        """Convert DataFrame to list of dictionaries for JSON serialization.

        Args:
            df: Pandas DataFrame

        Returns:
            List of dictionaries
        """
        if df is None:
            return []
        # Convert date to string for JSON
        df_copy = df.copy()
        if "date" in df_copy.columns:
            df_copy["date"] = df_copy["date"].astype(str)
        return df_copy.to_dict("records")

