"""Competitor analysis for demand forecasting."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from agent.types import Context, State


async def analyze_competitor_impact(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze competitor actions and predict their impact on demand.

    Args:
        state: Current state with competitor data
        runtime: Runtime context

    Returns:
        Dictionary with competitor analysis results
    """
    competitor_data = getattr(state, "competitor_data", None)
    historical_data = getattr(state, "historical_data", None)

    if competitor_data is None or len(competitor_data) == 0:
        return {
            "competitor_analysis": {
                "error": "No competitor data available",
                "recommendation": "Monitor competitor activities to assess market impact",
            }
        }

    # Analyze competitor actions
    df = pd.DataFrame(competitor_data) if not isinstance(competitor_data, pd.DataFrame) else competitor_data

    if len(df) == 0:
        return {
            "competitor_analysis": {
                "error": "Empty competitor dataset",
            }
        }

    # Count actions by type
    action_counts = df["action_type"].value_counts().to_dict() if "action_type" in df.columns else {}
    competitor_counts = df["competitor"].value_counts().to_dict() if "competitor" in df.columns else {}

    # Calculate average impact
    avg_impact = float(df["impact_score"].mean()) if "impact_score" in df.columns else 1.0

    # Prepare context for LLM
    context = f"""
    Competitor Activity Analysis:
    - Total competitor actions: {len(df)}
    - Action types: {action_counts}
    - Most active competitors: {competitor_counts}
    - Average impact score: {avg_impact:.2f}
    """

    # Use LLM for strategic analysis
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
    As a demand forecasting expert, analyze competitor activities and their potential impact:

    {context}

    Provide insights on:
    1. Competitive threat level
    2. Expected impact on demand
    3. Recommended response strategies
    4. Market positioning implications

    Consider:
    - Price changes (can reduce our demand)
    - New product launches (can capture market share)
    - Promotions (can shift customer behavior)
    - Market dynamics and customer loyalty
    """

    try:
        response = llm.invoke(prompt)
        analysis = response.content if hasattr(response, "content") else str(response)

        # Estimate demand impact
        # Negative impact for competitor actions (they take market share)
        demand_impact_percentage = -avg_impact * 10  # Scale impact score to percentage

        competitor_analysis = {
            "activity_summary": {
                "total_actions": len(df),
                "action_breakdown": action_counts,
                "competitor_breakdown": competitor_counts,
                "average_impact_score": round(float(avg_impact), 2),
            },
            "demand_impact": {
                "estimated_impact_percentage": round(float(demand_impact_percentage), 2),
                "threat_level": "high" if avg_impact > 1.5 else "medium" if avg_impact > 1.0 else "low",
            },
            "llm_insights": analysis[:500],
            "recommendations": [
                f"Expected demand reduction: {abs(demand_impact_percentage):.1f}% due to competitor actions",
                "Monitor competitor pricing strategies closely",
                "Consider defensive promotions or product differentiation",
                "Focus on customer retention and value proposition",
            ],
        }

        return {"competitor_analysis": competitor_analysis}

    except Exception as e:
        # Fallback analysis
        demand_impact = -avg_impact * 10
        return {
            "competitor_analysis": {
                "activity_summary": {
                    "total_actions": len(df),
                    "action_breakdown": action_counts,
                    "competitor_breakdown": competitor_counts,
                    "average_impact_score": round(float(avg_impact), 2),
                },
                "demand_impact": {
                    "estimated_impact_percentage": round(float(demand_impact), 2),
                    "threat_level": "high" if avg_impact > 1.5 else "medium" if avg_impact > 1.0 else "low",
                },
                "error": f"LLM analysis failed: {str(e)}",
                "recommendations": [
                    "Monitor competitor activities regularly",
                    "Adjust forecasts based on competitive actions",
                ],
            }
        }


async def adjust_forecast_for_competitors(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Adjust demand forecast based on competitor analysis.

    Args:
        state: Current state
        runtime: Runtime context

    Returns:
        Dictionary with adjusted forecast
    """
    seasonal_forecast = getattr(state, "seasonal_forecast", None)
    competitor_analysis = getattr(state, "competitor_analysis", None)

    if not seasonal_forecast or "forecast_values" not in seasonal_forecast:
        return {
            "competitor_adjusted_forecast": {
                "error": "Base forecast required",
            }
        }

    base_forecast = seasonal_forecast["forecast_values"]
    forecast_dates = seasonal_forecast.get("forecast_dates", [])

    # Get competitor impact
    impact_adjustment = 1.0
    if competitor_analysis and "demand_impact" in competitor_analysis:
        impact_pct = competitor_analysis["demand_impact"].get("estimated_impact_percentage", 0)
        impact_adjustment = 1.0 + (impact_pct / 100.0)

    # Apply adjustment
    adjusted_forecast = [v * impact_adjustment for v in base_forecast]

    return {
        "competitor_adjusted_forecast": {
            "forecast_dates": forecast_dates,
            "base_forecast": base_forecast,
            "adjusted_forecast": [round(float(v), 2) for v in adjusted_forecast],
            "adjustment_factor": round(float(impact_adjustment), 4),
            "impact_percentage": round(float((impact_adjustment - 1.0) * 100), 2),
        }
    }

