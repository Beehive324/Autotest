"""Define a simple chatbot agent.

This agent returns a predefined response without using an actual LLM.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from main.configuration import Configuration
from main.state import State

from .agents import Attacker, Planner, Recon, Reporter


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
    
    pass


async def access_phase(state: State, config: RunnableConfig):
   
    pass


async def reporting_phase(state: State, config: RunnableConfig):
    
    pass

initalized_agents = {
    "attacker": Attacker(), 
    "planner": Planner(),
    "recon": Recon(),
    "reporter": Reporter()
}



# Define a new graph
workflow = StateGraph(State, config_schema=Configuration)

workflow.add_node("plannig_phase", initalized_agents["planner"]._planning_phase)
# Add the node to the graph
#every single node to be added for the recon phase
workflow.add_node("reccon_phase", recon_phase)
workflow.add_node("dns_resolution", initalized_agents["recon"]._dns_resolution)
workflow.add_node("subdomain_enum", initalized_agents["recon"]._subdomain_enumeration)
workflow.add_node("nmap+port_scan", initalized_agents["recon"]._port_scanning)
workflow.add_node("google_dorks", initalized_agents["recon"]._google_dorks)
workflow.add_node("github_dorks", initalized_agents["recon"]._github_dorks)
workflow.add_node("shodan_dorks", initalized_agents["recon"]._shodan_dorks)

workflow.add_node("planning_phase", planning_phase)
#every single node to be added for the planning phase

workflow.add_node("access_phase", access_phase)
workflow.add_node("sql_injection", initalized_agents["attacker"]._sql_injection)
workflow.add_node("xss_attack", initalized_agents["attacker"]._xss_attack)
workflow.add_node("csrf_attack", initalized_agents["attacker"]._csrf_attack)
workflow.add_node("shell_shock", initalized_agents["attacker"]._shell_shock)
workflow.add_node("binary_analysis", initalized_agents["attacker"]._binary_analysis)
#every single node to be added for the access phase
workflow.add_node("reporting_phase", reporting_phase)
workflow.add_node("write_report", initalized_agents["reporter"]._write_report)
workflow.add_node("generate_report", initalized_agents["reporter"]._generate_report)    

# Add edges to graph
workflow.set_entry_point("planning_phase")
workflow.add_edge("planning_phase", "plannig_phase")
workflow.add_edge("planning_phase", "reccon_phase")
workflow.add_edge("reccon_phase", "access_phase")
workflow.add_edge("reccon_phase", "dns_resolution") 
workflow.add_edge("reccon_phase", "subdomain_enum")
workflow.add_edge("reccon_phase", "nmap+port_scan")
workflow.add_edge("reccon_phase", "google_dorks")
workflow.add_edge("reccon_phase", "github_dorks")
workflow.add_edge("reccon_phase", "shodan_dorks")
workflow.add_edge("access_phase", "sql_injection")  
workflow.add_edge("access_phase", "xss_attack")
workflow.add_edge("access_phase", "csrf_attack")
workflow.add_edge("access_phase", "shell_shock")
workflow.add_edge("access_phase", "binary_analysis")
workflow.add_edge("access_phase", "reporting_phase")
workflow.add_edge("reporting_phase", "write_report")
workflow.add_edge("write_report", "generate_report")    

# Compile the workflow into an executable graph
graph = workflow.compile()
graph.name = "AutoTest"  # This defines the custom name in LangSmith
