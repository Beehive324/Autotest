from datetime import datetime
from langchain_core.tools import tool
import requests
import nmap
from typing import Optional, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from ...agents.orchestrator.memory import PenTestState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain.tools import Tool
from .tools.reporting_tools import WriteReport


class Reporter:
    def __init__(self):
        self._tools: list = [
            WriteReport
        ]
    
    async def get_tools(self) -> List[Tool]:
        return self._tools
    
    async def generate_report(self):
        pass
    
    async def _start_reporting_(self, state: PenTestState):
        pass
    
    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(PenTestState)
        graph.add_node("start", self._start_reporting_)
        graph.add_node("end", END)
    
    def add_graph_edges(self, graph):
        graph.add_edge("start", "end")

if __name__ == "__main__":
    reporter = Reporter()
        
        
        







