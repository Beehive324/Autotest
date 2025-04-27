from datetime import datetime
from langchain_core.tools import tool
import requests
import nmap
from typing import Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from memory.state import PenTestState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from typing import List, Tool
from agents.reporting_phase.tools.reporting_tools import WriteReport


class Reporter:
    def __init__(self):
        self._tools: list = [
            WriteReport
        ]
    
    
    async def get_tools(self) -> List[Tool]:
        pass
    
    async def generate_report():
        pass
    
    
    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(PenTestState)
        graph.add_node("start", _start_reporting_)
        graph.add_node("end", END)
    
    
    def add_graph_edges(self, graph):
        graph.add_edge("start", "end")



if __name__ == "__main__":
    reporter = Reporter()
        
        
        







