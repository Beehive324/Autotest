from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from typing import List
from langchain.tools import Tool
from .state import ReconState
from .tools.recontools import (
    Nmap, Resolve, 
    Subdomain_Enum_CRT, Subdomain_Enum_gobuster, Subdomain_Enum_findomain,
    Subdomain_Enum_amass, Subdomain_Enum_wayback, Subdomain_Enum_sublist3r,
    GoogleDorks, GitHubDorks, ShodanDorks, APIDiscovery, WebSearch, Masscan
)
from IPython.display import Image, display
from ...agents.orchestrator.memory import PenTestState
import socket
import datetime
import nmap
from ...agents.orchestrator.memory import Messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import logging

logger = logging.getLogger(__name__)

class Recon:
    def __init__(self, model, tools: List = None):
        self.model = model
        self.tools = tools or [
            
            Nmap(),
            Resolve(),
            Subdomain_Enum_CRT(),
            Subdomain_Enum_gobuster(),
            Subdomain_Enum_findomain(),
            Subdomain_Enum_amass(),
            Subdomain_Enum_wayback(),
            Subdomain_Enum_sublist3r(),
            GoogleDorks(),
            GitHubDorks(),
            ShodanDorks(),
            APIDiscovery(),
            WebSearch(),
            Masscan(),
        ]
        self.name = "Recon"
        self.prompt = "You are a penetration tester your task is to determine the open ports and services on the target machine as well as the version of the service the operating system, host discovery, port information, service detection, network information, service information, and other relevant information using the provided nmap tool using the provided host {ip}."
        
        self.model_with_tools = self.model.bind_tools(self.tools)
    
    def get_tools(self) -> List[Tool]:
        return self.tools

    def _start_recon(self, state: PenTestState):
        ip = state.ip_port
        nmap_result = Nmap()._run(ip_address=ip)
        #masscan_result = Masscan()._run(ip_address=ip)
        prompt = f"""
        You are a penetration tester your task is to determine the open ports and services on the target machine as 
        well as the version of the service the operating system, host discovery, port information, service detection, 
        network information, service information, and other relevant information using the provided nmap tool using the provided host {ip}.
        """
        ai_msg = self.model_with_tools.invoke(prompt)
        
        print(ai_msg.tool_calls)
        ip_address = ai_msg.tools_calls['Args']['ip_address']
        scan_options = ai_msg.tools.calls['Args']['Scan Options']
        state.open_ports = {
        "nmap_results": nmap_result,
        #"masscan_results": masscan_result,
        "message": ai_msg.tool_calls
        }
    
        return state
    
    def _analyze_ports(self, state: PenTestState):
        analyze_instructions = f"""
        You are a professional vulnerability assesser your task is to analyze the following ports
        {state.open_ports} and provide an analysis for the purposes of penetration testing
        """
        
        # Direct invocation without structured output
        findings = self.model.invoke([
            SystemMessage(content=analyze_instructions),
            HumanMessage(content="Analyze the following nmap results")
        ])
        
        # Make sure findings is properly formatted before appending
        state.planning_results = {
            "message": findings
        }
       
        return state 
        
    async def _dns_resolution(self, state: PenTestState):
        domain = state['domain']
        
        dns_resolution_result = Resolve._arun(domain_name=domain)
        
        return {
            "dns_resolution": dns_resolution_result
        }
        
    #domain enumeration
    async def _subdomain_enumeration(self, state: PenTestState):
        domain = state['domain']
        
        return {
            
            "crt_enumeration": Subdomain_Enum_CRT._run(domain_name=domain),
            "gobuster": Subdomain_Enum_gobuster._run(domain_name=domain),
            "findomain": Subdomain_Enum_findomain._arun(domain_name=domain),
            "amass": Subdomain_Enum_amass._arun(domain_name=domain),
            "wayback": Subdomain_Enum_wayback._arun(domain_name=domain),
            "sublist3r": Subdomain_Enum_sublist3r._arun(domain_name=domain),
            
        }
        
    async def _github_dorks(self, state: PenTestState):
        domain = state['domain']
        
        return {
            
            'github_dorks_results': GitHubDorks._arun(domain_name=domain)
        }
    
    async def _google_dorks(self, state: PenTestState):
        
        domain = state['domain']
        
        return {
            
            'google_dorks': GoogleDorks._arun(domain_name=domain)
        }
        
    async def _port_scanning(self, state: PenTestState):
        
        IP_PORT = state['ip']
        
        return {
            'IP_SCAN': Nmap._run(ip_address=IP_PORT)
        }
    
    async def _shodan_dorks(self, state: PenTestState):
        domain = state['domain']
        
        return {
            
            'Shodan_dork_results': ShodanDorks._arun(domain_name=domain)
        }
        
    def _create_graph(self) -> StateGraph:
        graph = StateGraph(ReconState)
        graph.add_node("start", self._start_recon)
        graph.add_node("dns_resolution", self._dns_resolution)
        graph.add_node("domain_enumeration", self._subdomain_enumeration)
        graph.add_node("port_scanning", self._port_scanning)
        graph.add_node("github_dorks", self._github_dorks)
        graph.add_node("google_dorks", self._google_dorks)
        graph.add_node("shodan_dorks", self._shodan_dorks)
        
        self._add_graph_edges(graph)
        return graph
        
    def _add_graph_edges(self, graph):
        graph.add_edge("start", "dns_resolution")
        graph.add_edge("dns_resolution", "domain_enumeration")
        graph.add_edge("domain_enumeration", "github_dorks")
        graph.add_edge("github_dorks", "google_dorks")
        graph.add_edge("google_dorks", "shodan_dorks")
        graph.add_edge("shodan_dorks", "port_scanning")
        graph.add_edge("port_scanning", END)
         
    async def run_recon(self):
        graph = self._create_graph()
        compiled_graph = graph.compile()
        return compiled_graph
    
    #display image graph 
    async def display_graph(self):
        graph = self._create_graph()
        
        return display(Image(graph.get_graph().draw_png('recon.png')))
    
    
    if __name__ == "__main__":
        graph = _create_graph()
        display(Image(graph.get_graph().draw_png('recon.png')))