"""Seasonal demand prediction using time series forecasting models."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd
from langgraph.runtime import Runtime
from prophet import Prophet

from agent.data_integration import validate_data
from agent.types import Context, State


async def forecast_seasonal_demand(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Generate seasonal demand forecast using Prophet.

    Args:
        state: Current state with historical data
        runtime: Runtime context

    Returns:
        Dictionary with forecast results
    """
    # Get forecast horizon from context or use default
    forecast_horizon = 30
    if runtime.context and "forecast_horizon_days" in runtime.context:
        forecast_horizon = runtime.context["forecast_horizon_days"]
    if not hasattr(state, "historical_data") or state.historical_data is None:
        return {
            "seasonal_forecast": {
                "error": "No historical data available",
                "forecast": None,
            }
        }

    df = state.historical_data.copy()
    validation = validate_data(df)

    if not validation["is_valid"]:
        return {
            "seasonal_forecast": {
                "error": validation.get("error", "Data validation failed"),
                "forecast": None,
            }
        }

    try:
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = pd.DataFrame({
            "ds": pd.to_datetime(df["date"]),
            "y": df["sales"],
        })

        # Add promotional regressor if available
        if "promotion" in df.columns:
            prophet_df["promotion"] = df["promotion"].values

        # Initialize and fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
        )

        # Add promotional regressor if available
        if "promotion" in prophet_df.columns:
            model.add_regressor("promotion")

        model.fit(prophet_df)

        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_horizon)

        # Add promotional regressor to future (assuming no promotions in future)
        if "promotion" in prophet_df.columns:
            future["promotion"] = 0

        # Generate forecast
        forecast = model.predict(future)

        # Extract forecast for future dates only
        last_date = prophet_df["ds"].max()
        future_forecast = forecast[forecast["ds"] > last_date].copy()

        # Format forecast results
        forecast_results = {
            "forecast_dates": [d.isoformat() for d in future_forecast["ds"]],
            "forecast_values": [float(v) for v in future_forecast["yhat"]],
            "forecast_lower": [float(v) for v in future_forecast["yhat_lower"]],
            "forecast_upper": [float(v) for v in future_forecast["yhat_upper"]],
            "last_historical_date": last_date.isoformat(),
            "forecast_horizon_days": forecast_horizon,
            "model_components": {
                "trend": "detected" if len(prophet_df) > 30 else "insufficient_data",
                "yearly_seasonality": True,
                "weekly_seasonality": True,
            },
        }

        return {"seasonal_forecast": forecast_results}

    except Exception as e:
        # Fallback to simple moving average if Prophet fails
        try:
            window = min(7, len(df) // 4)
            if window < 1:
                window = 1

            last_sales = df["sales"].tail(window).mean()
            future_dates = [
                (df["date"].max() + timedelta(days=i + 1)).isoformat()
                for i in range(forecast_horizon)
            ]

            return {
                "seasonal_forecast": {
                    "forecast_dates": future_dates,
                    "forecast_values": [float(last_sales)] * forecast_horizon,
                    "forecast_lower": [float(last_sales * 0.8)] * forecast_horizon,
                    "forecast_upper": [float(last_sales * 1.2)] * forecast_horizon,
                    "last_historical_date": df["date"].max().isoformat(),
                    "forecast_horizon_days": forecast_horizon,
                    "model_components": {"trend": "simple_average", "seasonality": False},
                    "warning": f"Prophet model failed, using simple average: {str(e)}",
                }
            }
        except Exception as fallback_error:
            return {
                "seasonal_forecast": {
                    "error": f"Forecast generation failed: {str(e)}, fallback failed: {str(fallback_error)}",
                    "forecast": None,
                }
            }

