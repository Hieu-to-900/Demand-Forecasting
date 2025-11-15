"""AI Demand Forecasting Graph - Phase 1: Subgraph Architecture.

This module defines the LangGraph workflow for demand forecasting with:
- Subgraph_DataCollection: Fetches internal, supply chain, and external data
- Batch processing: Parallel forecasting for products
- Subgraph_Output: Generates recommendations, alerts, and notifications

Phase 1: Mock data with modular subgraph structure
Phase 2: Real API integrations (minimal code changes in subgraphs)
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from agent.nodes_category_processing import process_category_batch, split_by_category
from agent.nodes_output import aggregate_forecasts
from agent.subgraph_data_collection import run_data_collection
from agent.subgraph_output import run_output_subgraph
from agent.types_new import Context, State


# Create category batch processor functions
def create_batch_processor(batch_idx: int):
    """Create a category batch processor function for a specific category."""

    async def batch_processor(
        state: State,
        runtime: Runtime[Context],
    ) -> Dict[str, Any]:
        """Process a specific category batch of products."""
        return await process_category_batch(batch_idx, state, runtime)

    return batch_processor


# Define the graph
graph = StateGraph(State, context_schema=Context)

# Add nodes
# Phase 1: Data Collection Subgraph
graph.add_node("data_collection", run_data_collection)

# Phase 2: Category-Based Product Processing
graph.add_node("split_by_category", split_by_category)

# Add category batch processing nodes (2 categories for MVP)
# Category 0: Spark Plugs
# Category 1: AC System
for i in range(2):
    batch_node = f"process_category_{i}"
    graph.add_node(batch_node, create_batch_processor(i))

# Phase 3: Aggregation
graph.add_node("aggregate", aggregate_forecasts)

# Phase 4: Output Subgraph
graph.add_node("output_subgraph", run_output_subgraph)

# Sequential edges
graph.add_edge("__start__", "data_collection")
graph.add_edge("data_collection", "split_by_category")
graph.add_edge("aggregate", "output_subgraph")

# Parallel edges: split_by_category -> category processors -> aggregate
for i in range(2):
    batch_node = f"process_category_{i}"
    graph.add_edge("split_by_category", batch_node)
    graph.add_edge(batch_node, "aggregate")

# Compile the graph
graph = graph.compile(name="AI Demand Forecasting - Category-Based MVP")
