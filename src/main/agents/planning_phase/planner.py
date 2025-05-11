from langchain_core.messages import AIMessage, HumanMessage
#from tools import recontools
from langgraph.graph import StateGraph, END
from ...state import State
from typing import List, Dict, Optional, Type
from langchain.tools import Tool
from pydantic import BaseModel, Field
from datetime import datetime
from ...agents.orchestrator.memory import PenTestState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from ...agents.orchestrator.memory import Messages

class Planner:
    def __init__(self, model):
        self._tools: list = []
        self.model = model
        self.name = "Planner"
    
    
    def _planning_phase(self, state: PenTestState) -> PenTestState:
        """Initial planning phase to set up the pentest"""
        
        planner_instructions=f"""You are tasked with creating a plan based on the findings of {state.open_ports}
        Conduct the best way to carry out penetration testing based on these open ports
        """
        state.planning_results = {
            "start_time": datetime.now(),
            "scope": "Initial scope defined",
            "objectives": ["Identify vulnerabilities", "Assess security posture"]
        }
        
        system_message = planner_instructions
        
        plan = self.model.invoke([
            SystemMessage(content=planner_instructions),
            HumanMessage(content="Analyze the following nmap results")
        ])
        
        state.planning_results = {
            "planning_results": plan
        }
        
        return state
    
    async def _risk_assessment(self, state: PenTestState) -> PenTestState:
        """Perform initial risk assessment"""
        if not state.planning_results:
            state.planning_results = {}
            
        state.planning_results = {
            "critical_assets": [],
            "threat_actors": [],
            "attack_vectors": [],
            "risk_level": "medium"
        }
        return state
    
    async def _define_scope(self, state: PenTestState) -> PenTestState:
        """Define the scope of the pentest"""
        if not state.planning_results:
            state.planning_results = {}
            
        state.planning_results["scope"] = {
            "targets": state.ip_port,
            "exclusions": [],
            "testing_methods": ["automated", "manual"],
        }
        return state
    
    def _create_graph(self) -> StateGraph:
        graph = StateGraph(PenTestState)
        graph.add_node("planning_phase", self._planning_phase)
        graph.add_node("risk_assessment", self._risk_assessment)
        graph.add_node("scope_definition", self._define_scope)
        return graph
    
    def add_graph_edges(self, graph):
        graph.add_edge("planning_phase", "risk_assessment")
        graph.add_edge("risk_assessment", "scope_definition")
        graph.add_edge("scope_definition", END)
    
    async def run_planning(self, state: PenTestState) -> PenTestState:
        """Run the complete planning phase"""
        graph = self._create_graph()
        self.add_graph_edges(graph)
        compiled_graph = graph.compile()
        return await compiled_graph.ainvoke(state)
    
    
    
    async def _start_planning_(self, state: State):
        pass
    
    
    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(State)
        graph.add_node("start", _start_planning_)
        graph.add_node("end", END)
        
    async def _run_planning(self, graph):
        return graph.compile()
    
    
    
# local testing
if __name__ == "__main__":
    planner = Planner()
    print(planner.get_tools())
    
    

        