from typing import Any, Dict, List, Optional, Tuple, Callable
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
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
from .phases.orchestrator.memory import PenTestState, Vulnerability, Service, Subdomain
from .phases.recon_phase.recon import Recon
from .phases.planning_phase.planner import Planner
from .phases.attack_phase.modules.attacker import Attacker
from .phases.reporting_phase.reporter import Reporter
from IPython.display import Image, display
from .phases.orchestrator.orchestrator import create_supervisor
from langgraph.prebuilt import create_react_agent
from .phases.recon_phase.tools.recontools import Nmap
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor
from langchain_community.tools import ShellTool
from langchain_core.runnables.graph import MermaidDrawMethod
import nest_asyncio
from langchain_ollama import ChatOllama
from langchain_core.runnables import Runnable

local_model = "llama3.2"


model = ChatOllama(model=local_model, temperature=1)

def initialize_agents() -> Dict[str, Any]:
    """Initialize all agents for the pentesting workflow"""
    return {
        "planner": Planner(model=model),
        "recon": Recon(model=model),
        "attacker": Attacker(model=model),
        "reporter": Reporter(model=model)
    }

def create_agents() -> Dict[str, Any]:
    agents = initialize_agents()
    
    # Create base prompt template
    base_template = """Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}"""

    # Create prompt templates for each agent
    explorer_prompt = PromptTemplate.from_template(base_template)
    planner_prompt = PromptTemplate.from_template(base_template)
    attacker_prompt = PromptTemplate.from_template(base_template)
    reporter_prompt = PromptTemplate.from_template(base_template)
    
    # Create tool instances
    nmap_tool = Nmap()
    shell_tool = ShellTool()
    
    
def create_workflow():
    """Create the main pentesting workflow graph with conditional edges and supervisor"""
    agents = create_agents()
    
    # Create the workflow graph
    workflow = StateGraph(PenTestState)
    
    # Create supervisor as a runnable agent
    supervisor = create_supervisor(
        model=model,
        prompt="""You are a Pentest orchestrator overseeing and managing a team of pentest experts.
        You are responsible for the overall direction of the pentest and the coordination of the team.
        You must go through the following phases for pentesting autonomously make decisions based on the current state:
        1. Planning - Create a plan for the pentest
        2. Reconnaissance - Gather information about the target
        3. Attacking - Execute attacks based on findings
        4. Reporting - Document results and findings
        
        Based on the current state, determine which phase should be executed next.
        Return only the name of the next phase: 'planning', 'recon', 'attack', or 'reporting'.""",
        state_schema=PenTestState,
        add_handoff_messages=True,
        add_handoff_back_messages=True,
        supervisor_name="orchestrator",
        include_agent_name="inline"
    )
    
    compiled_supervisor = supervisor.compile()
    
    
    # Define conditional functions for edge routing
    def planning_complete(state: PenTestState) -> str:
        """Check if planning phase is complete"""
        if state.planning_results is not None and len(state.planning_results) > 0:
            return "recon"
        return "planning"
    
    def recon_complete(state: PenTestState) -> str:
        """Check if reconnaissance phase is complete"""
        if (len(state.open_ports) >= 0 
            and len(state.services) >= 0):
            return "attack"
        return "recon"
    
    def attack_complete(state: PenTestState) -> str:
        """Check if attack phase is complete"""
        if len(state.successful_exploits) > 0:
            return "reporting"
        return "attack"
    
    def need_more_recon(state: PenTestState) -> str:
        """Check if more reconnaissance is needed"""
        if (state.remaining_steps > 0 
            and len(state.open_ports) == 0):
            return "recon"
        return "attack"
    
    def need_plan_update(state: PenTestState) -> str:
        """Check if planning needs to be updated"""
        if (
            len(state.vulnerabilities) < 0 
            ):
            return "planning"
        return "attack"
    
    def supervisor_routing(state: PenTestState) -> str:
        """Determine which phase to execute next based on state"""
        # Check if we need to start with planning
        if not state.planning_results:
            return "planning"
        
        # Check if we need more reconnaissance
        if not state.open_ports and not state.services:
            return "recon"
        
        # Check if we need to attack
        if not state.successful_exploits and not state.failed_exploits:
            return "attack"
        
        # Check if we need to report
        if state.successful_exploits or state.failed_exploits:
            return "reporting"
        
        # Default to planning if no other conditions are met
        return "planning"
    
    # Add nodes to the graph
    workflow.add_node("supervisor", compiled_supervisor)
    workflow.add_node("planning", Planner(model=model))
    workflow.add_node("recon", Recon(model=model))
    workflow.add_node("attack", Attacker(model=model))
    workflow.add_node("reporting", Reporter(model=model))
    
    # Add supervisor edges
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_routing,
        {
            "planning": "planning",
            "recon": "recon",
            "attack": "attack",
            "reporting": "reporting"
        }
    )
    
    # Add conditional edges for phase transitions
    workflow.add_conditional_edges(
        "planning",
        planning_complete,
        {
            "planning": "planning",
            "recon": "recon"
        }
    )
    
    workflow.add_conditional_edges(
        "recon",
        recon_complete,
        {
            "recon": "recon",
            "attack": "attack"
        }
    )
    
    workflow.add_conditional_edges(
        "attack",
        attack_complete,
        {
            "attack": "attack",
            "reporting": "reporting"
        }
    )
    
    # Add feedback loops with conditional edges
    workflow.add_conditional_edges(
        "attack",
        need_more_recon,
        {
            "recon": "recon",
            "attack": "attack"
        }
    )
    
    workflow.add_conditional_edges(
        "attack",
        need_plan_update,
        {
            "planning": "planning",
            "attack": "attack"
        }
    )
    
    # Add edges back to supervisor
    workflow.add_edge("planning", "supervisor")
    workflow.add_edge("recon", "supervisor")
    workflow.add_edge("attack", "supervisor")
    workflow.add_edge("reporting", "supervisor")
    
    # Add end edge
    workflow.add_edge("supervisor", END)
    
    return workflow

# Create and compile the workflow
workflow = create_workflow()
graph = workflow.compile()

# Save the graph visualization
graph_path = 'workflow_graph.png'
graph.get_graph().draw_png(graph_path)
print(f"Graph visualization saved to: {graph_path}")

attacker = Attacker(model=model)
recon = Recon(model=model)
planner = Planner(model=model)
reporter = Reporter(model=model)

attacker_graph = attacker.workflow
recon_graph = recon.workflow
planning_graph = planner.workflow
reporting_graph = reporter.workflow


# Export the graph for Studio UI
__all__ = ["graph", "attacker_graph", "recon_graph", "planning_graph", "reporting_graph"]



"""
# Initialize state with proper PenTestState structure
initial_state = PenTestState(
    ip_port="localhost",
    planning_results={},
    vulnerabilities=[],
    services=[],
    subdomains=[],
    open_ports=[],
    successful_exploits=[],
    failed_exploits=[],
    risk_score=0.0,
    remaining_steps=5,
    messages=[HumanMessage(content="Start pentesting on localhost")],
    chat_history=[],
    start_time=datetime.now()
)

# Run the workflow
async def run_pentest():
    async for chunk in graph.astream(
        initial_state,
        subgraphs=True,
        stream_mode="updates"
    ):
        print(f"State update: {chunk}")

# Run the pentest
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_pentest())
"""
