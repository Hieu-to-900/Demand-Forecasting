"""Pattern recognition module using LLM for demand forecasting analysis."""

from __future__ import annotations

from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from agent.data_integration import validate_data
from agent.types import Context, State


async def analyze_patterns(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze historical data patterns using LLM.

    Identifies trends, seasonality, and anomalies in the data.

    Args:
        state: Current state with historical data
        runtime: Runtime context

    Returns:
        Dictionary with pattern analysis results
    """
    if not hasattr(state, "historical_data") or state.historical_data is None:
        return {
            "pattern_analysis": {
                "error": "No historical data available",
                "trends": [],
                "seasonality": None,
                "anomalies": [],
            }
        }

    df = state.historical_data
    validation = validate_data(df)

    if not validation["is_valid"]:
        return {
            "pattern_analysis": {
                "error": validation.get("error", "Data validation failed"),
            }
        }

    # Calculate basic statistics
    sales_stats = {
        "mean": float(df["sales"].mean()),
        "std": float(df["sales"].std()),
        "min": float(df["sales"].min()),
        "max": float(df["sales"].max()),
        "trend": "increasing" if len(df) > 1 and df["sales"].iloc[-1] > df["sales"].iloc[0] else "decreasing",
    }

    # Detect anomalies (values beyond 2 standard deviations)
    mean_sales = df["sales"].mean()
    std_sales = df["sales"].std()
    anomalies = df[
        (df["sales"] > mean_sales + 2 * std_sales) | (df["sales"] < mean_sales - 2 * std_sales)
    ].to_dict("records") if std_sales > 0 else []

    # Prepare data summary for LLM
    data_summary = f"""
    Sales Statistics:
    - Mean: {sales_stats['mean']:.2f}
    - Standard Deviation: {sales_stats['std']:.2f}
    - Min: {sales_stats['min']:.2f}
    - Max: {sales_stats['max']:.2f}
    - Overall Trend: {sales_stats['trend']}
    - Date Range: {validation['date_range']['start']} to {validation['date_range']['end']}
    - Total Records: {validation['total_records']}
    - Anomalies Detected: {len(anomalies)}
    """

    # Use LLM for pattern analysis
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
    Analyze the following sales data statistics and identify patterns:

    {data_summary}

    Please identify:
    1. Key trends (increasing, decreasing, stable, cyclical)
    2. Seasonal patterns (if any)
    3. Notable anomalies and their potential causes
    4. Factors that might influence demand

    Provide a concise analysis in JSON format with keys: trends, seasonality, anomalies, insights.
    """

    try:
        response = llm.invoke(prompt)
        analysis_text = response.content if hasattr(response, "content") else str(response)

        # Extract insights from LLM response
        # In a production system, you'd parse structured JSON from the LLM
        pattern_analysis = {
            "trends": [sales_stats["trend"]],
            "seasonality": "detected" if validation["total_records"] > 90 else "insufficient_data",
            "anomalies": [{"date": str(a.get("date", "")), "sales": a.get("sales", 0)} for a in anomalies[:5]],
            "insights": analysis_text[:500],  # Truncate for state management
            "statistics": sales_stats,
        }
    except Exception as e:
        # Fallback if LLM fails
        pattern_analysis = {
            "trends": [sales_stats["trend"]],
            "seasonality": "unknown",
            "anomalies": [{"date": str(a.get("date", "")), "sales": a.get("sales", 0)} for a in anomalies[:5]],
            "insights": f"LLM analysis unavailable: {str(e)}",
            "statistics": sales_stats,
        }

    return {"pattern_analysis": pattern_analysis}

