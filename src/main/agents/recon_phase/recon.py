from langchain_core.messages import AIMessage, HumanMessage
from tools import recontools
from langgraph.graph import StateGraph, END
from memory.state import ReconState


class ReconnaissanceAgent:
    def __init__(
        self, 
        
        self._tools: list = []
        )
    
    async def get_tools(self) -> List[Tool]:
        return self._tools
    
    async def _start_recon_(self, state: ReconState):
        
        pass
    
    async def _dns_resolution_(self, state: ReconState):
        pass
    
    async def _subdomain_enumeration_(self, state: ReconState):
        pass
        
    async def _port_scanning_(self, state: ReconState):
        pass
    
    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(ReconState)
        graph.add_node("start", _start_recon)
        graph.add_node("dns_resolution", _dns_resolution_)
        graph.add_node("domain_enumeration", _subdomain_enumeration_)
        graph.add_node("port_scanning", _port_scanning_)
        
        self._add_graph_edge(graph)
        self._run_recon(graph)
        
    def add_graph_edges(self, graph):
        graph.add_edge("start", "dns_resolution")
        graph.add_edge("dns_resolution", "domain_enumeration")
        graph.add_edge("port_scanner", END)
    
    async def _run_recon(self, graph):
        return graph.compile()
        
        
    
        
    
    