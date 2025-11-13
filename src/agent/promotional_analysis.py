"""Promotional impact analysis for demand forecasting."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from agent.types import Context, State


async def analyze_promotional_impact(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze historical promotion effects and predict future impact.

    Args:
        state: Current state with historical and promotional data
        runtime: Runtime context

    Returns:
        Dictionary with promotional analysis results
    """
    historical_data = getattr(state, "historical_data", None)
    if historical_data is None:
        return {
            "promotional_analysis": {
                "error": "No historical data available",
            }
        }

    df = historical_data.copy()

    # Check if we have promotion data
    if "promotion" not in df.columns:
        return {
            "promotional_analysis": {
                "error": "No promotional data in historical records",
            }
        }

    # Analyze historical promotions
    promo_days = df[df["promotion"] == 1]
    non_promo_days = df[df["promotion"] == 0]

    if len(promo_days) == 0:
        return {
            "promotional_analysis": {
                "error": "No historical promotions found",
                "recommendation": "Consider running a test promotion to gather data",
            }
        }

    # Calculate promotion lift
    avg_promo_sales = promo_days["sales"].mean()
    avg_non_promo_sales = non_promo_days["sales"].mean()

    if avg_non_promo_sales > 0:
        lift_percentage = ((avg_promo_sales - avg_non_promo_sales) / avg_non_promo_sales) * 100
    else:
        lift_percentage = 0

    # Analyze promotion patterns
    promo_stats = {
        "total_promotions": len(promo_days),
        "avg_promo_sales": float(avg_promo_sales),
        "avg_non_promo_sales": float(avg_non_promo_sales),
        "lift_percentage": round(float(lift_percentage), 2),
        "max_promo_sales": float(promo_days["sales"].max()),
        "min_promo_sales": float(promo_days["sales"].min()),
    }

    # Prepare context for LLM analysis
    context = f"""
    Historical Promotion Analysis:
    - Total promotional days: {promo_stats['total_promotions']}
    - Average sales during promotions: {promo_stats['avg_promo_sales']:.2f}
    - Average sales without promotions: {promo_stats['avg_non_promo_sales']:.2f}
    - Sales lift: {promo_stats['lift_percentage']:.2f}%
    - Maximum promotion sales: {promo_stats['max_promo_sales']:.2f}
    - Minimum promotion sales: {promo_stats['min_promo_sales']:.2f}
    """

    # Use LLM for strategic analysis
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
    As a demand forecasting expert, analyze the following promotional impact data:

    {context}

    Provide insights on:
    1. Effectiveness of past promotions
    2. Optimal promotion timing
    3. Expected impact of future promotions
    4. Recommendations for promotional strategy

    Consider factors like:
    - Promotion frequency
    - Seasonal timing
    - Diminishing returns from over-promotion
    - Customer behavior patterns
    """

    try:
        response = llm.invoke(prompt)
        analysis = response.content if hasattr(response, "content") else str(response)

        # Predict future promotion impact
        # Use historical lift as baseline, with some decay for frequent promotions
        future_promo_lift = lift_percentage
        if promo_stats["total_promotions"] > len(df) * 0.2:  # More than 20% promotional days
            future_promo_lift = lift_percentage * 0.8  # Diminishing returns

        promotional_analysis = {
            "historical_stats": promo_stats,
            "predicted_lift_percentage": round(float(future_promo_lift), 2),
            "effectiveness": "high" if lift_percentage > 30 else "medium" if lift_percentage > 10 else "low",
            "llm_insights": analysis[:500],
            "recommendations": [
                f"Expected sales increase during promotions: {future_promo_lift:.1f}%",
                "Monitor promotion fatigue if promotions are too frequent",
                "Consider seasonal timing for maximum impact",
            ],
        }

        return {"promotional_analysis": promotional_analysis}

    except Exception as e:
        # Fallback analysis
        return {
            "promotional_analysis": {
                "historical_stats": promo_stats,
                "predicted_lift_percentage": round(float(lift_percentage), 2),
                "effectiveness": "high" if lift_percentage > 30 else "medium" if lift_percentage > 10 else "low",
                "error": f"LLM analysis failed: {str(e)}",
                "recommendations": [
                    f"Historical lift: {lift_percentage:.1f}%",
                    "Use promotions strategically to maximize impact",
                ],
            }
        }


async def predict_promotional_demand(
    state: State,
    runtime: Runtime[Context],
    promotion_dates: list[str] | None = None,
) -> Dict[str, Any]:
    """Predict demand for specific promotional dates.

    Args:
        state: Current state
        runtime: Runtime context
        promotion_dates: List of dates (ISO format) for planned promotions

    Returns:
        Dictionary with promotional demand predictions
    """
    # Get base forecast
    seasonal_forecast = getattr(state, "seasonal_forecast", None)
    promotional_analysis = getattr(state, "promotional_analysis", None)

    if not seasonal_forecast or "forecast_values" not in seasonal_forecast:
        return {
            "promotional_demand": {
                "error": "Base forecast required for promotional predictions",
            }
        }

    base_forecast = seasonal_forecast["forecast_values"]
    forecast_dates = seasonal_forecast.get("forecast_dates", [])

    # Get expected lift
    lift = 1.0
    if promotional_analysis and "predicted_lift_percentage" in promotional_analysis:
        lift = 1.0 + (promotional_analysis["predicted_lift_percentage"] / 100.0)

    # Apply promotion boost to specified dates
    promo_forecast = base_forecast.copy()
    if promotion_dates:
        for i, date in enumerate(forecast_dates):
            if date in promotion_dates and i < len(promo_forecast):
                promo_forecast[i] = promo_forecast[i] * lift

    return {
        "promotional_demand": {
            "forecast_dates": forecast_dates,
            "base_forecast": base_forecast,
            "promotional_forecast": [round(float(v), 2) for v in promo_forecast],
            "promotion_lift": round(float((lift - 1.0) * 100), 2),
            "promotion_dates": promotion_dates or [],
        }
    }

