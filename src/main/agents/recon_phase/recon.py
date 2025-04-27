from langchain_core.messages import AIMessage, HumanMessage
from tools import recontools
from langgraph.graph import StateGraph, END
from memory.state import ReconState
from tools.recontools import Nmap, Resolve, Enumerator, GoogleDorks, GitHubDorks, ShodanDroks, APIDiscovery, WebSearch

class ReconnaissanceAgent:
    def __init__(
        self, 
        
        self._tools: list = [
            Nmap,
            Resolver,
            Enumerator,
            GoogleDorks,
            GitHubDorks,
            ShodanDorks,
            APIDiscovery,
            WebSearch,    
        ]
        )
    
    async def get_tools(self) -> List[Tool]:
        return self._tools
   
    async def _start_recon_(self, state: ReconState):
        #tool calling for starting recon phase
        pass
    
    
    async def _dns_resolution_(self, state: ReconState):
        #tool callingn for starting dns resolution
        
        pass
    
    async def _subdomain_enumeration_(self, state: ReconState):
        #tool calling for subdomain enumeration
        pass
    
    async def _githhub_dorks(self, state: ReconState):
        #tool calling for github dorks
        pass
    
    async def _google_dorks(self, state: ReconState):
        # tool calling for google dorks
        pass
        
    async def _port_scanning_(self, state: ReconState):
        #tool calling for port scanning
        pass
    
    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(ReconState)
        graph.add_node("start", _start_recon)
        graph.add_node("dns_resolution", _dns_resolution_)
        graph.add_node("domain_enumeration", _subdomain_enumeration_)
        graph.add_node("port_scanning", _port_scanning_)
        graph.add_node("github_dorks", _github_dorks)
        graph.add_node("google_dorks", _google_dorks)
        
        self._add_graph_edge(graph)
        self._run_recon(graph)
        
    def add_graph_edges(self, graph):
        graph.add_edge("start", "dns_resolution")
        graph.add_edge("dns_resolution", "domain_enumeration")
        graph.add_edge("domain_enumeration", "github_dorks")
        graph.add_edege("github_dorks", "_google_dorks")
        graph.add_edge("port_scanner", END)
    
    async def _run_recon(self, graph):
        return graph.compile()
        
        
    
        
    
    