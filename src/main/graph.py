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
from .agents.orchestrator.memory import PenTestState, Vulnerability, Service, Subdomain
from .agents.recon_phase.recon import Recon
from .agents.planning_phase.planner import Planner
from .agents.attacking_phase.attacker import Attacker
from .agents.reporting_phase.reporter import Reporter
from IPython.display import Image, display
from langchain_ollama import ChatOllama
from .agents.orchestrator.orchestrator import create_supervisor
from langgraph.prebuilt import create_react_agent
from .agents.recon_phase.tools.recontools import Nmap
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor
from langchain_community.tools import ShellTool

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
    
    # Create agents with proper prompt templates and tool instances
    explorer = create_react_agent(
        model=model,
        tools=[nmap_tool, shell_tool],
        prompt="You are a pentest expert. You are responsible for exploring the target and gathering information about the target. You have access to the following tools: {tools}",
        name="explorer"
    )
    
    planner = create_react_agent(
        model=model,
        tools=[nmap_tool, shell_tool],
        prompt="You are a pentest expert. You are responsible for planning the pentest. You have access to the following tools: {tools}",
        name="planner"
    )
    
    attacker = create_react_agent(
        model=model,
        tools=[nmap_tool, shell_tool],
        prompt="You are a pentest expert. You are responsible for attacking the target. You have access to the following tools: {tools}",
        name="attacker"
    )
    
    reporter = create_react_agent(
        model=model,
        tools=[nmap_tool, shell_tool],
        prompt="You are a pentest expert. You are responsible for reporting the results of the pentest. You have access to the following tools: {tools}",
        name="reporter"
    )
    
    return {
        "explorer": explorer,
        "planner": planner,
        "attacker": attacker,
        "reporter": reporter
    }

def create_workflow() -> StateGraph:
    """Create the main pentesting workflow graph"""
    agents = create_agents()
    workflow = create_supervisor(
        [
            agents["planner"],
            agents["explorer"], 
            agents["attacker"],
            agents["reporter"]
        ],
        model=model,
        prompt=(
            """You are a Pentest orchestrator overseeing and managing a team of pentest experts \n
            You are responsible for the overall direction of the pentest and the coordination of the team \n
            And you must go through the following phases for pentesting: \n 
            Planning \n
            Reconnaissance \n
            Attacking \n
            Reporting \n    
            Use Planner to create a plan for the pentest \n
            Use Recon to gather information about the target \n
            Use Attacker to attack the target \n
            Use Reporter to report the results of the pentest"""
        ),
        add_handoff_messages=True,
        supervisor_name="Orchestrator",
    )
    return workflow

# Create and compile the workflow
workflow = create_workflow()
graph = workflow.compile()

# Initialize state with required messages field
"""
initial_state = {
    "messages": [HumanMessage(content="Start pentesting on localhost")],
    "ip_port": "localhost:"
}


initial_state = {
    "messages": ["Start pentesting on localhost"],  # List of strings
    "ip_port": "localhost:",
    "input_message": "Start pentesting on localhost",  # Required string
    "remaining_steps": 5,  # Required integer
    "planning_results": {},
    "vulnerabilities": [],
    "services": [],
    "subdomains": [],
    "open_ports": [],
    "successful_exploits": [],
    "failed_exploits": [],
    "risk_score": 0.0
}


#streaming to the terminal in real time

for chunk in graph.stream(
    initial_state,
    subgraphs=True,
    stream_mode="updates"
):
    print(chunk)
"""
# Save the graph visualization
graph_path = 'pentest.png'
graph.get_graph().draw_png(graph_path)
print(f"Graph visualization saved to: {graph_path}")

# Display the graph
display(Image(graph_path))

# Export the graph
__all__ = ["graph"]
