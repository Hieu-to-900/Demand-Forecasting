"""New product forecasting using LLM reasoning and similar product analysis."""

from __future__ import annotations

from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from agent.types import Context, State


async def forecast_new_product(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Forecast demand for a new product using similar product analysis.

    Args:
        state: Current state with product and historical data
        runtime: Runtime context

    Returns:
        Dictionary with new product forecast results
    """
    # Check if this is a new product request
    new_product_id = getattr(state, "new_product_id", None)
    if not new_product_id:
        return {
            "new_product_forecast": {
                "error": "No new product ID specified",
            }
        }

    # Get historical data for similar products
    historical_data = getattr(state, "historical_data", None)
    product_info = getattr(state, "product_info", None)

    if historical_data is None or product_info is None:
        return {
            "new_product_forecast": {
                "error": "Insufficient data for new product forecasting",
            }
        }

    # Find similar products based on category
    new_product_category = None
    if hasattr(state, "new_product_category"):
        new_product_category = state.new_product_category

    # Get products in same category
    similar_products = product_info[
        product_info["category"] == new_product_category
    ] if new_product_category else product_info

    if len(similar_products) == 0:
        similar_products = product_info  # Use all products if no category match

    # Get historical data for similar products
    similar_product_ids = similar_products["product_id"].tolist()
    similar_data = historical_data[historical_data["product_id"].isin(similar_product_ids)]

    if len(similar_data) == 0:
        return {
            "new_product_forecast": {
                "error": "No historical data available for similar products",
            }
        }

    # Calculate average sales for similar products
    avg_sales = similar_data["sales"].mean()
    std_sales = similar_data["sales"].std()

    # Prepare context for LLM
    context = f"""
    New Product Information:
    - Product ID: {new_product_id}
    - Category: {new_product_category or 'Unknown'}
    
    Similar Products Analysis:
    - Number of similar products: {len(similar_products)}
    - Average daily sales: {avg_sales:.2f}
    - Sales standard deviation: {std_sales:.2f}
    - Product categories analyzed: {', '.join(similar_products['category'].unique().tolist())}
    """

    # Use LLM for reasoning
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
    You are a demand forecasting expert. Analyze the following information about a new product launch:

    {context}

    Consider:
    1. Typical demand patterns for new products in this category
    2. Market penetration curves (slow start, growth, stabilization)
    3. Seasonality factors
    4. Initial demand uncertainty

    Provide a forecast estimate for the first 30 days:
    - Initial demand (first week): typically 20-40% of established product average
    - Growth phase (weeks 2-3): increasing demand
    - Stabilization (week 4+): approaching category average

    Provide your analysis and recommended forecast values.
    """

    try:
        response = llm.invoke(prompt)
        analysis = response.content if hasattr(response, "content") else str(response)

        # Generate forecast based on typical new product curve
        # Week 1: 30% of average
        # Week 2: 50% of average
        # Week 3: 70% of average
        # Week 4: 85% of average
        # Week 5+: 90% of average

        forecast_values = []
        for week in range(1, 5):
            week_multiplier = [0.3, 0.5, 0.7, 0.85][week - 1]
            for day in range(7):
                forecast_values.append(avg_sales * week_multiplier)

        # Remaining days at 90% of average
        remaining_days = max(0, 30 - len(forecast_values))
        for _ in range(remaining_days):
            forecast_values.append(avg_sales * 0.9)

        forecast_results = {
            "product_id": new_product_id,
            "forecast_period_days": 30,
            "forecast_values": [round(float(v), 2) for v in forecast_values],
            "confidence": "medium",  # New products have higher uncertainty
            "method": "similar_product_analysis",
            "similar_products_count": len(similar_products),
            "category_average": round(float(avg_sales), 2),
            "llm_analysis": analysis[:500],  # Truncate for state
            "recommendations": [
                "Monitor initial sales closely",
                "Adjust inventory based on first week performance",
                "Consider promotional campaigns to boost initial demand",
            ],
        }

        return {"new_product_forecast": forecast_results}

    except Exception as e:
        # Fallback to simple heuristic
        initial_demand = avg_sales * 0.3
        return {
            "new_product_forecast": {
                "product_id": new_product_id,
                "forecast_period_days": 30,
                "forecast_values": [round(float(initial_demand), 2)] * 30,
                "confidence": "low",
                "method": "heuristic_fallback",
                "error": f"LLM analysis failed: {str(e)}",
                "recommendations": [
                    "Use conservative initial inventory",
                    "Monitor sales closely and adjust quickly",
                ],
            }
        }

