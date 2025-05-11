from typing import Any, Dict, List, Optional, Tuple, Callable
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain.tools import Tool
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns
import graphviz
from datetime import datetime
from IPython.display import Image
from .configuration import Configuration
from .agents.orchestrator.memory import PenTestState, Vulnerability, Service, Subdomain
from .agents.recon_phase.recon import Recon
from .agents.planning_phase.planner import Planner
from .agents.attacking_phase.attacker import Attacker
from .agents.reporting_phase.reporter import Reporter
from IPython.display import Image, display
from langchain_ollama import ChatOllama
from .agents.orchestrator.orchestrator import create_supervisor


local_model = "llama3.2"


model = ChatOllama(model=local_model, temperature=1)

#function to initialize all agents for pentesting
def initialize_agents() -> Dict[str, Any]:
    """Initialize all agents for the pentesting workflow"""
    return {
        "planner": Planner(model=model),
        "recon": Recon(model=model),
        "attacker": Attacker(model=model),
        "reporter": Reporter()
    }


def create_workflow() -> StateGraph:
    """Create the main pentesting workflow graph"""
    
    agents = initialize_agents()
    workflow = create_supervisor(
        [
            agents["planner"],
            agents["recon"],
            agents["attacker"],
            agents["reporter"]
         ],
        model=model,
        prompt=(
            "You are a Pentest orchestrator overseeing and managing a team of pentest experts"
        ),
        state_schema=PenTestState,
        add_handoff_messages=True,
        supervisor_name="Orchestrator"
    )
    
    
    return workflow

# Create and compile the workflow
workflow = create_workflow()
graph = workflow.compile()

# Save the graph visualization
graph_path = 'pentest.png'
graph.get_graph().draw_png(graph_path)
print(f"Graph visualization saved to: {graph_path}")

# Display the graph
display(Image(graph_path))

# Export the graph
__all__ = ["graph"]
