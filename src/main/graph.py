"""Define a simple chatbot agent.

This agent returns a predefined response without using an actual LLM.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from agent.configuration import Configuration
from agent.state import State


async def my_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """Each node does work."""
    configuration = Configuration.from_runnable_config(config)
    # configuration = Configuration.from_runnable_config(config)
    # You can use runtime configuration to alter the behavior of your
    # graph.
    return {
        "changeme": "output from my_node. "
        f"Configured with {configuration.my_configurable_param}"
    }


async def recon_phase(state: State, config: RunnableConfig):
    # Define recon_phase logic
    pass


async def planning_phase(state: State, config: RunnableConfig):
    
    #Define planning_phase logic
    
    pass


async def access_phase(state: State, config: RunnableConfig):
    
    #access phase logic

    pass


async def reporting_phase(state: State, config: RunnableConfig):

    pass

# Define a new graph
workflow = StateGraph(State, config_schema=Configuration)
# Add the node to the graph
workflow.add_node("reccon_phase", recon_phase)
workflow.add_node("planning_phase", planning_phase)
workflow.add_node("access_phase", access_phase)
workflow.add_node("reporting_phase", reporting_phase)

# Add edges to graph
workflow.set_entry_point("planning_phase")
workflow.add_edge("planning_phase", "reccon_phase")
workflow.add_edge("reccon_phase", "access_phase")
workflow.add_edge("access_phase", "reporting_phase")

# Compile the workflow into an executable graph
graph = workflow.compile()
graph.name = "New Graph"  # This defines the custom name in LangSmith
