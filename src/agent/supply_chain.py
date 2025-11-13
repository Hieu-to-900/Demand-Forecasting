"""Supply chain optimization for demand forecasting."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from langgraph.runtime import Runtime
from scipy import stats

from agent.types import Context, State


async def optimize_supply_chain(
    state: State,
    runtime: Runtime[Context],
    lead_time_days: int = 7,
    service_level: float = 0.95,
    holding_cost_rate: float = 0.2,
) -> Dict[str, Any]:
    """Calculate optimal inventory levels and reorder points.

    Args:
        state: Current state with forecast data
        runtime: Runtime context
        lead_time_days: Supplier lead time in days
        service_level: Desired service level (0-1)
        holding_cost_rate: Annual holding cost as fraction of item value

    Returns:
        Dictionary with supply chain optimization results
    """
    # Get forecast data
    seasonal_forecast = getattr(state, "seasonal_forecast", None)
    if not seasonal_forecast or "forecast_values" not in seasonal_forecast:
        return {
            "supply_chain_optimization": {
                "error": "Forecast data required for supply chain optimization",
            }
        }

    forecast_values = seasonal_forecast["forecast_values"]
    if not forecast_values:
        return {
            "supply_chain_optimization": {
                "error": "Empty forecast data",
            }
        }

    # Calculate forecast statistics
    avg_daily_demand = np.mean(forecast_values)
    std_daily_demand = np.std(forecast_values)

    # Safety stock calculation (using service level)
    # Z-score for service level (95% = 1.645)
    z_score = stats.norm.ppf(service_level)

    # Lead time demand
    lead_time_demand = avg_daily_demand * lead_time_days
    lead_time_std = std_daily_demand * np.sqrt(lead_time_days)

    # Safety stock
    safety_stock = z_score * lead_time_std

    # Reorder point
    reorder_point = lead_time_demand + safety_stock

    # Economic Order Quantity (EOQ) calculation
    # Assuming annual demand and ordering cost
    annual_demand = avg_daily_demand * 365
    ordering_cost = 50.0  # Default ordering cost
    unit_cost = 10.0  # Default unit cost (can be from product info)

    if hasattr(state, "product_info") and state.product_info is not None:
        # Try to get actual unit cost
        product_id = getattr(state, "product_id", None)
        if product_id:
            product_data = state.product_info[state.product_info["product_id"] == product_id]
            if len(product_data) > 0 and "base_price" in product_data.columns:
                unit_cost = float(product_data["base_price"].iloc[0])

    eoq = np.sqrt((2 * annual_demand * ordering_cost) / (holding_cost_rate * unit_cost))

    # Optimal order quantity (use EOQ or minimum based on lead time)
    optimal_order_quantity = max(eoq, lead_time_demand)

    # Calculate inventory metrics
    avg_inventory = (optimal_order_quantity / 2) + safety_stock
    annual_holding_cost = avg_inventory * unit_cost * holding_cost_rate
    annual_ordering_cost = (annual_demand / optimal_order_quantity) * ordering_cost
    total_cost = annual_holding_cost + annual_ordering_cost

    # Stockout probability
    stockout_probability = 1 - service_level

    optimization_results = {
        "demand_statistics": {
            "average_daily_demand": round(float(avg_daily_demand), 2),
            "std_daily_demand": round(float(std_daily_demand), 2),
            "lead_time_demand": round(float(lead_time_demand), 2),
        },
        "inventory_parameters": {
            "reorder_point": round(float(reorder_point), 2),
            "safety_stock": round(float(safety_stock), 2),
            "optimal_order_quantity": round(float(optimal_order_quantity), 2),
            "economic_order_quantity": round(float(eoq), 2),
        },
        "cost_analysis": {
            "annual_holding_cost": round(float(annual_holding_cost), 2),
            "annual_ordering_cost": round(float(annual_ordering_cost), 2),
            "total_annual_cost": round(float(total_cost), 2),
            "unit_cost": round(float(unit_cost), 2),
        },
        "service_metrics": {
            "service_level": round(float(service_level * 100), 2),
            "stockout_probability": round(float(stockout_probability * 100), 2),
            "lead_time_days": lead_time_days,
        },
        "recommendations": [
            f"Maintain reorder point at {reorder_point:.0f} units",
            f"Order {optimal_order_quantity:.0f} units when inventory reaches reorder point",
            f"Safety stock of {safety_stock:.0f} units to maintain {service_level*100:.0f}% service level",
            "Monitor demand variability and adjust safety stock if patterns change",
        ],
    }

    return {"supply_chain_optimization": optimization_results}

