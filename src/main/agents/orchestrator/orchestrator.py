from ..attacking_phase.attacker import Attacker
from ..planning_phase.planner import Planner
from ..recon_phase.recon import Recon
from ..reporting_phase.reporter import Reporter
from .memory import PenTestState
from langgraph.graph import StateGraph

class PenTestOrchestrator:
    def __init__(self, ip_port):
        self.ip_port = ip_port
        
    def _initalize_agents(self, agents):
        #return hashamp of each initalized agent
        return {
            'planner': Planner(),
            'attacker': Attacker(),
            'recon': Recon(),
            'reporter': Reporter()
        }
    
    def _create_graph(self, agents):
        graph = StateGraph(PenTestState)
        
        graph.add_node("nmap+port_scan", agents['recon'].port_scanner) 
        graph.add_node("subdomain_enum", agents['recon'].subdomain_enum)
        graph.add_node("google_dorks", agents['recon'].google_dorks)
        graph.add_node("github_dorks", agents['recon'].github_dorks)
        graph.add_node("shodan_dorks", agents['recon'].shodan_dorks)
    
    
    def add_graph_edges(self, graph):
        graph.add_edge("nmap+port_scan", "subdomain_enum")
        graph.add_edge("subdomain_enum", "google_dorks")
        graph.add_edge("google_dorks", "github_dorks")
        graph.add_edge("github_dorks", "shodan_dorks")
        
    async def _log_pentest(self):
        pass
    
    async def _run_pentest(self):
        pass
    


        
        
    
    
    
    
     
     

    
    
    