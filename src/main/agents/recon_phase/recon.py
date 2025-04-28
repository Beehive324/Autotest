from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from typing import List
from langchain.tools import Tool
from .state import ReconState
from .tools.recontools import (
    Nmap, Resolve, 
    Subdomain_Enum_CRT, Subdomain_Enum_gobuster, Subdomain_Enum_findomain,
    Subdomain_Enum_amass, Subdomain_Enum_wayback, Subdomain_Enum_sublist3r,
    GoogleDorks, GitHubDorks, ShodanDorks, APIDiscovery, WebSearch
)

class Recon:
    def __init__(self, tools: List = None):
        self.tools = tools or [
            Nmap,
            Resolve,
            Subdomain_Enum_CRT,
            Subdomain_Enum_gobuster,
            Subdomain_Enum_findomain,
            Subdomain_Enum_amass,
            Subdomain_Enum_wayback,
            Subdomain_Enum_sublist3r,
            GoogleDorks,
            GitHubDorks,
            ShodanDorks,
            APIDiscovery,
            WebSearch
        ]
    
    async def get_tools(self) -> List[Tool]:
        return self.tools
   
    async def _start_recon(self, state: ReconState):
        # tool calling for starting recon phase
        pass
    
    async def _dns_resolution(self, state: ReconState):
        # tool calling for starting dns resolution
        pass
    
    async def _subdomain_enumeration(self, state: ReconState):
        # tool calling for subdomain enumeration
        pass
    
    async def _github_dorks(self, state: ReconState):
        # tool calling for github dorks
        pass
    
    async def _google_dorks(self, state: ReconState):
        # tool calling for google dorks
        pass
        
    async def _port_scanning(self, state: ReconState):
        # tool calling for port scanning
        pass
    
    async def _shodan_dorks(self, state: ReconState):
        # tool calling for shodan dorks
        pass
    
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