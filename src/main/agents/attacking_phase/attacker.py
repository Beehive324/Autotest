from datetime import datetime
from langchain_core.tools import tool
import requests
from pydantic import BaseModel, Field
import sublist3r
from ...state import PenTestState
from typing import List
from langchain.tools import Tool
from langgraph.graph import StateGraph, END
#from attacking_phase.tools.attacktools import SQL_Injection, XSS_attack, CSRF_attack, ShellShock, BinaryAnalysis


class Attacker:
    def __init__(self):
        self._tools: list[Tool] = []
        #self._tools: list = [
         #   SQL_Injection,
           # XSS_attack,
          #  CSRF_attack,
         #   ShellShock,
           # BinaryAnalysis
        #]
    
   # async def get_tools(self) -> List[Tool]:
        #return self._tools
    
    async def _plan_attack_(self, state: PenTestState):
        pass
    
    
    async def _sql_injection_(self, state: PenTestState):
        pass
    
    async def _xss_attack_(self, state: PenTestState):
        pass
    
    async def _csrf_attack_(self, state: PenTestState):
        pass

    async def _shell_shock_(self, state: PenTestState):
        pass
    
    async def _binary_analysis_(self, state: PenTestState):
        pass

    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(PenTestState)
        graph.add_node("start", _plan_attack_ )
        graph.add_node("attack", _start_attacking_)
        graph.add_node("end", END)
    
    
    def add_graph_edges(self, graph):
        graph.add_edge("start", "attack")
    
    
    async def _run_attack(self, graph):
        return graph.compile
    
    

#local testing
if __name__ == "__main__":
    attack = Attacker()

    
    
    