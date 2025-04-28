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
        # tool calling for starting recon phase given an IP port
        ip = state['ip']
        nmap_results = Nmap()._run(ip_address=ip)
        
        return {
            
            "nmap_results": nmap_results
        }
        
    async def _dns_resolution(self, state: ReconState):
        domain = state['domain']
        
        dns_resolution_result = Resolve._arun(domain_name=domain)
        
        return {
            "dns_resolution": dns_resolution_result
        }
        
    #domain enumeration
    async def _subdomain_enumeration(self, state: ReconState):
        domain = state['domain']
        
        return {
            
            "crt_enumeration": Subdomain_Enum_CRT._run(domain_name=domain),
            "gobuster": Subdomain_Enum_gobuster._run(domain_name=domain),
            "findomain": Subdomain_Enum_findomain._arun(domain_name=domain),
            "amass": Subdomain_Enum_amass._arun(domain_name=domain),
            "wayback": Subdomain_Enum_wayback._arun(domain_name=domain),
            "sublist3r": Subdomain_Enum_sublist3r._arun(domain_name=domain),
            
        }
        
    async def _github_dorks(self, state: ReconState):
        domain = state['domain']
        
        return {
            
            'github_dorks_results': GitHubDorks._arun(domain_name=domain)
        }
    
    async def _google_dorks(self, state: ReconState):
        
        domain = state['domain']
        
        return {
            
            'google_dorks': GoogleDorks._arun(domain_name=domain)
        }
        
    async def _port_scanning(self, state: ReconState):
        
        IP_PORT = state['ip']
        
        return {
            'IP_SCAN': Nmap._run(ip_address=IP_PORT)
        }
    
    async def _shodan_dorks(self, state: ReconState):
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