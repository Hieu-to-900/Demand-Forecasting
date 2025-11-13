import pytest
from langgraph_sdk import get_client

from agent import graph

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_agent_simple_passthrough() -> None:
    inputs = {"changeme": "some_val"}
    res = await graph.ainvoke(inputs)
    assert res is not None


@pytest.mark.langsmith
async def test_agent_stream_with_sdk() -> None:
    """Test streaming runs using langgraph_sdk client."""
    client = get_client(url="http://localhost:2024")
    
    events_received = []
    async for chunk in client.runs.stream(
        None,  # Threadless run
        "agent",  # Name of assistant. Defined in langgraph.json.
        input={
            "changeme": "What is LangGraph?", 
        },
    ):
        events_received.append(chunk.event)
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("\n\n")
    
    # Assert that we received some events
    assert len(events_received) > 0