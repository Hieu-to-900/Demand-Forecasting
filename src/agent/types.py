"""Type definitions for the demand forecasting agent.

Contains State and Context definitions to avoid circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal

import pandas as pd
from typing_extensions import TypedDict


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    """

    forecast_mode: Literal["seasonal", "new_product", "promotional", "comprehensive"]
    forecast_horizon_days: int
    llm_model: str
    product_id: str
    new_product_id: str | None
    new_product_category: str | None


@dataclass
class State:
    """Input state for the demand forecasting agent.

    Defines the structure of incoming data and intermediate results.
    """

    # Input data
    product_id: str = ""
    historical_data: pd.DataFrame | None = None
    product_info: pd.DataFrame | None = None
    competitor_data: pd.DataFrame | None = None
    promotion_dates: List[str] = field(default_factory=list)

    # New product forecasting
    new_product_id: str = ""
    new_product_category: str = ""

    # Intermediate results
    pattern_analysis: Dict[str, Any] | None = None
    seasonal_forecast: Dict[str, Any] | None = None
    new_product_forecast: Dict[str, Any] | None = None
    promotional_analysis: Dict[str, Any] | None = None
    promotional_demand: Dict[str, Any] | None = None
    competitor_analysis: Dict[str, Any] | None = None
    competitor_adjusted_forecast: Dict[str, Any] | None = None
    supply_chain_optimization: Dict[str, Any] | None = None
    scenario_planning: Dict[str, Any] | None = None
    realtime_adjustment: Dict[str, Any] | None = None

    # Final output
    final_forecast: Dict[str, Any] | None = None
    forecast_mode: str = "comprehensive"

