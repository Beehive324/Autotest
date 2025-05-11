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


local_model = "llama3.2"


model = ChatOllama(model=local_model, temperature=1)


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
    workflow = StateGraph(PenTestState)
    initialized_agents = initialize_agents()
    
    # Planning Phase Nodes
    workflow.add_node("planning_phase", initialized_agents["planner"]._planning_phase)
    workflow.add_node("analysis_phase", initialized_agents["recon"]._analyze_ports)
    workflow.add_node("port_discovery", initialized_agents["recon"]._start_recon)
    
    workflow.add_edge(START,"port_discovery")
    workflow.add_edge("port_discovery", "analysis_phase")
    workflow.add_edge("analysis_phase", "planning_phase")
    workflow.add_edge("planning_phase", END)
    
    
    return workflow

# Create and compile the workflow
workflow = create_workflow()
graph = workflow.compile()


#display(Image(graph.get_graph().draw_png('pentest.png')))


# Export the graph
__all__ = ["graph"]
