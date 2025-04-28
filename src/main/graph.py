from typing import Any, Dict, List, Optional, Tuple, Callable
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
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

def initialize_agents() -> Dict[str, Any]:
    """Initialize all agents for the pentesting workflow"""
    return {
        "planner": Planner(), #Planner Agent
        "recon": Recon(), #Reconnaisance Agent
        "attacker": Attacker(), #Attacker Agent
        "reporter": Reporter() #Report Agent
    }

def create_workflow() -> StateGraph:
    """Create the main pentesting workflow graph"""
    workflow = StateGraph(PenTestState) #initialise our workflow
    initialized_agents = initialize_agents() #initalise our agents
    
    # Planning Phase Nodes
    workflow.add_node("planning_phase", initialized_agents["planner"]._planning_phase)
    workflow.add_node("risk_assessment", initialized_agents["planner"]._risk_assessment)
    workflow.add_node("scope_definition", initialized_agents["planner"]._define_scope)
    
    # Reconnaissance Phase Nodes
    workflow.add_node("start_recon", initialized_agents["recon"]._start_recon)
    workflow.add_node("dns_resolution", initialized_agents["recon"]._dns_resolution)
    workflow.add_node("domain_enumeration", initialized_agents["recon"]._subdomain_enumeration)
    workflow.add_node("github_dorks", initialized_agents["recon"]._github_dorks)
    workflow.add_node("google_dorks", initialized_agents["recon"]._google_dorks)
    workflow.add_node("shodan_dorks", initialized_agents["recon"]._shodan_dorks)
    workflow.add_node("port_scanning", initialized_agents["recon"]._port_scanning)
    
    # Attack Phase Nodes
    workflow.add_node("plan_attack", initialized_agents["attacker"]._plan_attack_)
    workflow.add_node("sql_injection", initialized_agents["attacker"]._sql_injection_)
    workflow.add_node("xss_attack", initialized_agents["attacker"]._xss_attack_)
    workflow.add_node("csrf_attack", initialized_agents["attacker"]._csrf_attack_)
    workflow.add_node("shell_shock", initialized_agents["attacker"]._shell_shock_)
    workflow.add_node("binary_analysis", initialized_agents["attacker"]._binary_analysis_)
    
    # Reporting Phase Nodes
    workflow.add_node("start_reporting", initialized_agents["reporter"]._start_reporting_)
    workflow.add_node("finalize_report", initialized_agents["reporter"]._finalize_report_)
    # Add edges between phases
    # Planning Phase edges - Parallel processing
    workflow.add_edge("planning_phase", "risk_assessment")
    workflow.add_edge("planning_phase", "scope_definition")
    
    # Conditional edges based on risk assessment
    workflow.add_conditional_edges(
        "risk_assessment",
        lambda x: "start_recon" if x.get("risk_level") == "high" else "scope_definition",
        ["start_recon", "scope_definition"]
    )
    
    # Planning to Recon edges
    workflow.add_edge("scope_definition", "start_recon")
    
    # Parallel Recon Phase edges
    workflow.add_edge("start_recon", "dns_resolution")
    workflow.add_edge("dns_resolution", "domain_enumeration")
    
    # Parallel dorking operations
    workflow.add_edge("domain_enumeration", "github_dorks")
    workflow.add_edge("domain_enumeration", "google_dorks")
    workflow.add_edge("domain_enumeration", "shodan_dorks")
    
    # Conditional edges for port scanning
    workflow.add_conditional_edges(
        "github_dorks",
        lambda x: "port_scanning" if x.get("github_findings") else "google_dorks",
        ["port_scanning", "google_dorks"]
    )
    workflow.add_conditional_edges(
        "google_dorks",
        lambda x: "port_scanning" if x.get("google_findings") else "shodan_dorks",
        ["port_scanning", "shodan_dorks"]
    )
    workflow.add_conditional_edges(
        "shodan_dorks",
        lambda x: "port_scanning" if x.get("shodan_findings") else "plan_attack",
        ["port_scanning", "plan_attack"]
    )
    
    # Recon to Attack edges
    workflow.add_edge("port_scanning", "plan_attack")
    
    # Parallel Attack Phase edges
    workflow.add_edge("plan_attack", "sql_injection")
    workflow.add_edge("plan_attack", "xss_attack")
    workflow.add_edge("plan_attack", "csrf_attack")
    workflow.add_edge("plan_attack", "shell_shock")
    workflow.add_edge("plan_attack", "binary_analysis")
    
    # Conditional edges for attack success
    workflow.add_conditional_edges(
        "sql_injection",
        lambda x: "start_reporting" if x.get("sql_success") else "xss_attack",
        ["start_reporting", "xss_attack"]
    )
    workflow.add_conditional_edges(
        "xss_attack",
        lambda x: "start_reporting" if x.get("xss_success") else "csrf_attack",
        ["start_reporting", "csrf_attack"]
    )
    workflow.add_conditional_edges(
        "csrf_attack",
        lambda x: "start_reporting" if x.get("csrf_success") else "shell_shock",
        ["start_reporting", "shell_shock"]
    )
    workflow.add_conditional_edges(
        "shell_shock",
        lambda x: "start_reporting" if x.get("shell_success") else "binary_analysis",
        ["start_reporting", "binary_analysis"]
    )
    workflow.add_conditional_edges(
        "binary_analysis",
        lambda x: "start_reporting" if x.get("binary_success") else "plan_attack",
        ["start_reporting", "plan_attack"]
    )
    
    # Attack to Reporting edges
    workflow.add_edge("binary_analysis", "start_reporting")
    
    # Reporting Phase edges
    workflow.add_edge("start_reporting", "finalize_report")
    
    workflow.add_edge("finalize_report", END)
    
    # Set entry point
    workflow.set_entry_point("planning_phase")
    
    return workflow

# Create and compile the workflow
workflow = create_workflow()
graph = workflow.compile()

#display(Image(graph.get_graph().draw_png('pentest.png')))


# Export the graph
__all__ = ["graph"]
