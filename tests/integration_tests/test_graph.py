import pytest
from langsmith import unit
from src.main.graph import create_pentest_graph
from src.main.state import PentestState, PentestStage

from agent import graph


@pytest.mark.asyncio
@unit
async def test_agent_simple_passthrough() -> None:
    res = await graph.ainvoke({"changeme": "some_val"})
    assert res is not None

def test_graph_creation():
    """Test that the pentest graph can be created."""
    graph = create_pentest_graph()
    assert graph is not None

def test_graph_execution():
    """Test the complete execution of the pentest graph."""
    graph = create_pentest_graph()
    state = PentestState(target="example.com")
    
    # Run the graph
    result = graph.run(state)
    
    # Verify the final state
    assert result.final_state is not None
    assert isinstance(result.final_state, PentestState)
    assert result.final_state.current_stage == PentestStage.COMPLETED

def test_graph_state_transitions():
    """Test that the graph properly transitions through all stages."""
    graph = create_pentest_graph()
    state = PentestState(target="example.com")
    
    # Run the graph
    result = graph.run(state)
    final_state = result.final_state
    
    # Verify that all stages were visited
    assert final_state.stage_history is not None
    assert PentestStage.INITIALIZATION in final_state.stage_history
    assert PentestStage.RECONNAISSANCE in final_state.stage_history
    assert PentestStage.VULNERABILITY_SCAN in final_state.stage_history
    assert PentestStage.EXPLOITATION in final_state.stage_history
    assert PentestStage.REPORTING in final_state.stage_history

def test_graph_error_handling():
    """Test that the graph properly handles errors."""
    graph = create_pentest_graph()
    state = PentestState(target="invalid-target")
    
    # Run the graph
    result = graph.run(state)
    
    # Verify error handling
    assert result.final_state is not None
    assert result.final_state.errors is not None
    assert len(result.final_state.errors) > 0

def test_graph_findings_accumulation():
    """Test that findings are properly accumulated throughout the graph execution."""
    graph = create_pentest_graph()
    state = PentestState(target="example.com")
    
    # Run the graph
    result = graph.run(state)
    
    # Verify findings
    assert result.final_state.findings is not None
    assert isinstance(result.final_state.findings, list)

def test_graph_vulnerability_accumulation():
    """Test that vulnerabilities are properly accumulated throughout the graph execution."""
    graph = create_pentest_graph()
    state = PentestState(target="example.com")
    
    # Run the graph
    result = graph.run(state)
    
    # Verify vulnerabilities
    assert result.final_state.vulnerabilities is not None
    assert isinstance(result.final_state.vulnerabilities, list)

def test_graph_parallel_execution():
    """Test that the graph can handle parallel execution of tasks."""
    graph = create_pentest_graph()
    state = PentestState(target="example.com")
    
    # Run the graph with parallel execution
    result = graph.run(state, parallel=True)
    
    # Verify parallel execution
    assert result.final_state is not None
    assert result.final_state.parallel_tasks_completed is not None
    assert len(result.final_state.parallel_tasks_completed) > 0
