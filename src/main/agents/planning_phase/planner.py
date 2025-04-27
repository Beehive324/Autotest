from langchain_core.messages import AIMessage, HumanMessage
from tools import recontools
from langgraph.graph import StateGraph, END
from memory.state import ReconState, PenTestState
from typing import List, Tool


class PlanningAgent:
    def __init__(self):
        self, 
        
        self._tools: list = [
            
        ]
     
    async def get_tools(self) -> List(Tool):
        return self._tools
    
    
    async def _start_planning_(self, state: ReconState):
        pass
    
    
    
    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(ReconState)
        graph.add_node("start", _start_planning_)
        graph.add_node("end", END)
        
        
    
    def add_graph_edges(self, graph):
        graph.add_edge("start", "end")
        
    async def _run_planning(self, graph):
        return graph.compile()
    
    
    
    

# local testing
if __name__ == "__main__":
    planner = PlanningAgent()
    print(planner.get_tools())
    
    

        