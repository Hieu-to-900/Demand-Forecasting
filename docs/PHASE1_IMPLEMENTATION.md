# Phase 1 Subgraph Architecture - Implementation Guide

## Overview

Phase 1 implementation restructures the demand forecasting agent into a modular subgraph architecture for better scalability and maintainability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN GRAPH (Orchestrator)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  __start__                                                   │
│     ↓                                                        │
│  ┌──────────────────────────────────────────┐               │
│  │  Subgraph_DataCollection                 │               │
│  │  ├─ fetch_internal (parallel)            │               │
│  │  ├─ fetch_supply_chain (parallel)        │               │
│  │  ├─ ingest_external (parallel)           │               │
│  │       ↓                                   │               │
│  │     clean_external                        │               │
│  │       ↓                                   │               │
│  │     store_external                        │               │
│  │  ├───────  3 branches above               │               │
│  │  └─→ aggregate_data                       │               │
│  └──────────────────────────────────────────┘               │
│     ↓                                                        │
│  split_batches (5 batches for 50 products)                  │
│     ↓                                                        │
│  ┌────────────────────────────────────────┐                 │
│  │  Parallel Batch Processing (5 batches) │                 │
│  │  ├─ process_batch_0 (products 1-10)    │                 │
│  │  ├─ process_batch_1 (products 11-20)   │                 │
│  │  ├─ process_batch_2 (products 21-30)   │                 │
│  │  ├─ process_batch_3 (products 31-40)   │                 │
│  │  └─ process_batch_4 (products 41-50)   │                 │
│  └────────────────────────────────────────┘                 │
│     ↓                                                        │
│  aggregate_forecasts                                         │
│     ↓                                                        │
│  ┌──────────────────────────────────────────┐               │
│  │  Subgraph_Output                         │               │
│  │  ├─ analyze_capacity                     │               │
│  │  │    ↓                                   │               │
│  │  ├─ generate_suggestions (parallel)      │               │
│  │  ├─ generate_alerts (parallel)           │               │
│  │  │    ↓                                   │               │
│  │  ├─ build_message                        │               │
│  │  │    ↓                                   │               │
│  │  └─ send_notification                    │               │
│  └──────────────────────────────────────────┘               │
│     ↓                                                        │
│   END                                                        │
└─────────────────────────────────────────────────────────────┘
```

## New Files Created

### 1. `subgraph_data_collection.py`
**Purpose**: Fetches data from multiple sources in parallel

**Nodes**:
- `fetch_internal_data`: Orders, inventory, production capacity (mock → real ERP/WMS/MES APIs)
- `fetch_supply_chain_risk`: Supplier status, logistics delays (mock → real supply chain APIs)
- `ingest_external`: External market data (reuses existing node)
- `clean_external`: Clean and tag external data (reuses existing node)
- `store_external`: Store in ChromaDB (reuses existing node)
- `aggregate_all_data`: Combine all data sources

**Phase 1**: Mock data generation
**Phase 2**: Real API calls (just replace implementation, no architecture change)

### 2. `subgraph_output.py`
**Purpose**: Generates recommendations, alerts, and notifications

**Nodes**:
- `analyze_forecast_vs_capacity`: Compare demand vs production capacity
- `generate_production_suggestions`: Actionable production recommendations
- `generate_risk_alerts`: Identify and prioritize risks
- `build_notification_message`: Format messages for stakeholders
- `send_notification`: Send via email/Slack/Teams (mock → real integration)

**Phase 1**: Mock notifications (console output)
**Phase 2**: Real notification services

### 3. Updated `types_new.py`
**Changes**: Added new state fields for subgraph outputs:
- `internal_data`: Orders, inventory, capacity
- `supply_chain_risks`: Supplier and logistics data
- `aggregated_data`: Combined data from all sources
- `capacity_analysis`: Capacity vs demand analysis
- `production_suggestions`: List of recommendations
- `notification_message`: Formatted notification
- `notification_sent`: Status flag

### 4. Updated `graph.py`
**Changes**: 
- Replaced individual nodes (`ingest`, `clean_tag`, `store_index`) with `data_collection` subgraph
- Replaced `output_alert` with `output_subgraph`
- Cleaner, more modular structure

## Benefits of Phase 1 Design

### ✅ Modularity
- Each subgraph has clear responsibility
- Easy to test subgraphs independently
- Team can work on different subgraphs in parallel

### ✅ Scalability
- Add new data sources by adding nodes to `Subgraph_DataCollection`
- Extend recommendations by adding nodes to `Subgraph_Output`
- Parallel data fetching improves performance

### ✅ Maintainability
- Mock → Real transition only requires changing node implementations
- Clear separation of concerns
- Easy to debug individual components

### ✅ Future-Ready
- Ready for Phase 2 real API integrations
- Architecture supports adding:
  - More data sources
  - More recommendation types
  - Category-based processing (Phase 2+)

## Data Flow

### Input
```python
{
    "product_codes": ["INV-001", "INV-002", ..., "INV-050"],
    "chromadb_collection": "external_market_data"
}
```

### After Subgraph_DataCollection
```python
{
    "internal_data": {
        "orders": [...],
        "inventory": {...},
        "production_capacity": {...}
    },
    "supply_chain_risks": {
        "supplier_status": [...],
        "logistics_delays": {...},
        "overall_risk_score": 0.25
    },
    "cleaned_external_data": [...],
    "aggregated_data": {...}
}
```

### After Batch Processing
```python
{
    "aggregated_forecasts": {
        "total_forecast_units": 45000,
        "total_products": 50,
        "forecasts": [...]
    }
}
```

### After Subgraph_Output
```python
{
    "capacity_analysis": {...},
    "production_suggestions": [...],
    "alerts_triggered": [...],
    "notification_message": {...},
    "notification_sent": true
}
```

## Testing

### Test Individual Subgraphs
```python
# Test data collection subgraph
from agent.subgraph_data_collection import run_data_collection
from agent.types_new import State

state = State(product_codes=["INV-001", "INV-002"])
result = await run_data_collection(state, runtime)
print(result["internal_data"])
print(result["supply_chain_risks"])
```

### Test Full Graph
```python
from agent.graph import graph
from agent.types_new import State

state = State(product_codes=["INV-001", "INV-002", "INV-003"])
result = await graph.ainvoke(state)
print(result["notification_message"])
```

## Migration Path: Phase 1 → Phase 2

### Internal Data (ERP Integration)
```python
# Phase 1 (current)
async def fetch_internal_data(state, runtime):
    return {"orders": generate_mock_orders()}

# Phase 2 (future)
async def fetch_internal_data(state, runtime):
    erp_client = ERPClient(api_key=os.getenv("ERP_API_KEY"))
    return {"orders": await erp_client.get_orders()}
```

### Supply Chain Risk (API Integration)
```python
# Phase 1 (current)
async def fetch_supply_chain_risk(state, runtime):
    return {"supplier_status": generate_mock_suppliers()}

# Phase 2 (future)
async def fetch_supply_chain_risk(state, runtime):
    sc_client = SupplyChainClient(api_key=os.getenv("SC_API_KEY"))
    return {"supplier_status": await sc_client.get_supplier_status()}
```

### Notifications (Email/Slack)
```python
# Phase 1 (current)
async def send_notification(state, runtime):
    print(f"NOTIFICATION: {state.notification_message}")
    return {"notification_sent": True}

# Phase 2 (future)
async def send_notification(state, runtime):
    email_client = EmailClient(smtp_config)
    await email_client.send(state.notification_message)
    return {"notification_sent": True}
```

## Performance Characteristics

### Parallel Processing
- **Data Collection**: 3 sources fetched in parallel
- **Batch Processing**: 5 batches (10 products each) processed in parallel
- **Output Generation**: Suggestions and alerts generated in parallel

### Estimated Time (Phase 1 with mock data)
- Data Collection: ~2s (parallel fetch)
- Batch Processing: ~30s (Prophet forecasting for 50 products)
- Output Generation: ~1s
- **Total**: ~33 seconds for 50 products

### Estimated Time (Phase 2 with real APIs)
- Data Collection: ~5s (API latency)
- Batch Processing: ~30s (same)
- Output Generation: ~3s (email sending)
- **Total**: ~38 seconds for 50 products

## Next Steps

1. ✅ **Test Phase 1 implementation** with mock data
2. ✅ **Validate subgraph isolation** (test each subgraph independently)
3. 📋 **Document API requirements** for Phase 2 integrations
4. 📋 **Plan Phase 2 migration** (ERP, supply chain, notification APIs)
5. 📋 **Consider category-based processing** if scaling beyond 100 products

## Questions?

Contact: [Your team lead or architect name]
