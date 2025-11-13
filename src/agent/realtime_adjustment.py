"""Real-time forecast adjustment based on recent data."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from langgraph.runtime import Runtime

from agent.types import Context, State


async def adjust_forecast_realtime(
    state: State,
    runtime: Runtime[Context],
    recent_days: int = 7,
) -> Dict[str, Any]:
    """Adjust forecast based on recent actual sales data.

    Args:
        state: Current state with forecast and recent data
        runtime: Runtime context
        recent_days: Number of recent days to use for adjustment

    Returns:
        Dictionary with adjusted forecast
    """
    seasonal_forecast = getattr(state, "seasonal_forecast", None)
    historical_data = getattr(state, "historical_data", None)

    if not seasonal_forecast or "forecast_values" not in seasonal_forecast:
        return {
            "realtime_adjustment": {
                "error": "Base forecast required for real-time adjustment",
            }
        }

    if historical_data is None or len(historical_data) == 0:
        return {
            "realtime_adjustment": {
                "error": "Historical data required for adjustment",
            }
        }

    # Get recent actual sales
    df = pd.DataFrame(historical_data) if not isinstance(historical_data, pd.DataFrame) else historical_data
    df["date"] = pd.to_datetime(df["date"])

    # Get most recent dates
    recent_data = df.nlargest(recent_days, "date")
    if len(recent_data) == 0:
        return {
            "realtime_adjustment": {
                "error": "Insufficient recent data",
            }
        }

    # Calculate forecast accuracy for recent period
    # (This would compare forecast vs actual, but for MVP we'll use trend adjustment)
    recent_avg = recent_data["sales"].mean()
    historical_avg = df["sales"].mean()

    # Calculate adjustment factor
    if historical_avg > 0:
        trend_factor = recent_avg / historical_avg
    else:
        trend_factor = 1.0

    # Get base forecast
    base_forecast = seasonal_forecast["forecast_values"]
    forecast_dates = seasonal_forecast.get("forecast_dates", [])

    # Apply trend adjustment
    adjusted_forecast = [v * trend_factor for v in base_forecast]

    # Calculate forecast variance (for confidence intervals)
    forecast_std = np.std(base_forecast) if len(base_forecast) > 1 else 0

    adjustment_results = {
        "base_forecast": base_forecast,
        "adjusted_forecast": [round(float(v), 2) for v in adjusted_forecast],
        "forecast_dates": forecast_dates,
        "adjustment_metrics": {
            "trend_factor": round(float(trend_factor), 4),
            "recent_avg_sales": round(float(recent_avg), 2),
            "historical_avg_sales": round(float(historical_avg), 2),
            "adjustment_percentage": round(float((trend_factor - 1.0) * 100), 2),
        },
        "confidence": {
            "level": "high" if abs(trend_factor - 1.0) < 0.1 else "medium" if abs(trend_factor - 1.0) < 0.2 else "low",
            "variance": round(float(forecast_std), 2),
        },
        "recommendations": [
            f"Forecast adjusted by {((trend_factor - 1.0) * 100):.1f}% based on recent trends",
            "Continue monitoring actual sales vs forecast",
            "Recalibrate model if adjustment exceeds 20%",
        ],
    }

    return {"realtime_adjustment": adjustment_results}

