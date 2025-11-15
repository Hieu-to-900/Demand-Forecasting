"""Subgraph for Data Collection - fetches internal, supply chain, and external data.

This subgraph combines three data sources:
1. Internal Data: Orders, inventory, production capacity (mock for now)
2. Supply Chain Risk: Supplier status, logistics delays (mock for now)
3. External Factors: Market data, trends (using existing external data nodes)
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from agent.nodes_external_data import clean_and_tag, ingest_external_data, store_in_chromadb
from agent.types_new import Context, State


async def fetch_internal_data(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Fetch internal data: orders, inventory, production capacity.
    
    Phase 1: Mock data
    Phase 2: Real API calls to ERP, WMS, MES systems
    """
    # Mock internal data
    internal_data = {
        "orders": [
            {"order_id": "ORD-001", "product_code": "INV-001", "quantity": 500, "delivery_date": "2025-02-15"},
            {"order_id": "ORD-002", "product_code": "INV-002", "quantity": 300, "delivery_date": "2025-02-20"},
            {"order_id": "ORD-003", "product_code": "INV-003", "quantity": 800, "delivery_date": "2025-03-01"},
        ],
        "inventory": {
            "INV-001": {"current_stock": 3200, "safety_stock": 1500, "warehouse": "Tokyo"},
            "INV-002": {"current_stock": 2400, "safety_stock": 1200, "warehouse": "Tokyo"},
            "INV-003": {"current_stock": 4800, "safety_stock": 2000, "warehouse": "Bangkok"},
        },
        "production_capacity": {
            "Line-A": {"max_monthly": 2500, "current_utilization": 0.76},
            "Line-B": {"max_monthly": 2000, "current_utilization": 0.82},
            "Line-C": {"max_monthly": 3000, "current_utilization": 0.80},
        },
        "fetch_timestamp": "2025-01-15T10:00:00"
    }
    
    return {
        "internal_data": internal_data,
    }


async def fetch_supply_chain_risk(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Fetch supply chain risk data: supplier status, logistics delays.
    
    Phase 1: Mock data
    Phase 2: Real API calls to supply chain monitoring systems
    """
    # Mock supply chain risk data
    supply_chain_risks = {
        "supplier_status": [
            {"supplier_id": "SUP-001", "name": "Battery Supplier A", "risk_level": "low", "on_time_delivery": 0.95},
            {"supplier_id": "SUP-002", "name": "Semiconductor Supplier B", "risk_level": "medium", "on_time_delivery": 0.82},
            {"supplier_id": "SUP-003", "name": "Metal Parts Supplier C", "risk_level": "low", "on_time_delivery": 0.97},
        ],
        "logistics_delays": {
            "sea_freight": {"avg_delay_days": 3, "risk_level": "low"},
            "air_freight": {"avg_delay_days": 1, "risk_level": "low"},
            "land_transport": {"avg_delay_days": 2, "risk_level": "medium"},
        },
        "overall_risk_score": 0.25,  # 0-1 scale, lower is better
        "fetch_timestamp": "2025-01-15T10:00:00"
    }
    
    return {
        "supply_chain_risks": supply_chain_risks,
    }


async def aggregate_all_data(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Aggregate all collected data into unified format.
    
    Combines internal data, supply chain risks, and external factors
    into a single data structure ready for forecasting.
    """
    aggregated = {
        "internal": state.internal_data or {},
        "supply_chain": state.supply_chain_risks or {},
        "external": {
            "cleaned_data": state.cleaned_external_data or [],
            "chromadb_collection": state.chromadb_collection,
            "total_stored": state.total_stored,
        },
        "aggregation_timestamp": "2025-01-15T10:05:00",
        "data_sources_count": 3,
    }
    
    return {
        "aggregated_data": aggregated,
    }


# Create Subgraph_DataCollection
def create_data_collection_subgraph() -> StateGraph:
    """Create the data collection subgraph.
    
    Workflow:
    1. Fetch internal data (parallel)
    2. Fetch supply chain risk (parallel)
    3. Fetch external factors (parallel - uses existing nodes)
    4. Aggregate all data sources
    """
    subgraph = StateGraph(State, context_schema=Context)
    
    # Add nodes
    subgraph.add_node("fetch_internal", fetch_internal_data)
    subgraph.add_node("fetch_supply_chain", fetch_supply_chain_risk)
    subgraph.add_node("ingest_external", ingest_external_data)
    subgraph.add_node("clean_external", clean_and_tag)
    subgraph.add_node("store_external", store_in_chromadb)
    subgraph.add_node("aggregate_data", aggregate_all_data)
    
    # Parallel data fetching from start
    subgraph.add_edge("__start__", "fetch_internal")
    subgraph.add_edge("__start__", "fetch_supply_chain")
    subgraph.add_edge("__start__", "ingest_external")
    
    # External data pipeline (sequential)
    subgraph.add_edge("ingest_external", "clean_external")
    subgraph.add_edge("clean_external", "store_external")
    
    # All sources flow to aggregation
    subgraph.add_edge("fetch_internal", "aggregate_data")
    subgraph.add_edge("fetch_supply_chain", "aggregate_data")
    subgraph.add_edge("store_external", "aggregate_data")
    
    return subgraph.compile(name="Subgraph_DataCollection")


# Main function to run subgraph as a node
async def run_data_collection(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Run the data collection subgraph as a single node."""
    subgraph = create_data_collection_subgraph()
    result = await subgraph.ainvoke(state)
    return result
