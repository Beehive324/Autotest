from datetime import datetime
from langchain_core.tools import tool
import requests
from pydantic import BaseModel, Field
import sublist3r
from ...state import PenTestState
from typing import List
from langchain.tools import Tool
#from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
#from attacking_phase.tools.attacktools import SQL_Injection, XSS_attack, CSRF_attack, ShellShock, BinaryAnalysis
from .tools.attacktools import (SQL_Injection, XSS, ShellShock, BinaryAnalysis)
import logging
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


logger = logging.getLogger(__name__)


class Attacker:
    def __init__(self, model, tools: List = None):
        self.model = model
        self.tools = [
    
            SQL_Injection,
            XSS,
            ShellShock,
            BinaryAnalysis,
             
        ]
        self.name = "Attacker"
        self.prompt = "You are a professional pentester your task is to carry out a plan with the given tools to attack the target system, knowing the following information: open ports: {state['open_ports']} ip_port: {state['ip_port']} vulnerabilities: {state['vulnerabilities']}"
    async def _plan_attack_(self, state: PenTestState):
        
        messages = state['messages']
        model_with_tools=self.model.bind_tools(self.tools)
        attack_prompt = f"""
        
        You are a professional pentester your task is to carry out a plan with the given tools
        to attack the target system, knowing the following information:
        open ports: {state['open_ports']}
        ip_port: {state['ip_port']}
        vulnerabilities: {state['vulnerabilities']}
        
        """
        
        output = model_with_tools.invoke([SystemMessage(content=attack_prompt),
                                          HumanMessage(content="Formulate an attack stategy/plan given the information given")])
        
        state.planning_results = {
            "attack_plan": output
        }
        
        return state
        
        
        
    async def _sql_injection_(self, state: PenTestState):
        ports = state['ports']
        details = []
        
        for port in ports:
            logging.info(f"Carrying out SQL injection on port:{port}")
            res = SQL_Injection._run(port)
            if res:
                details.append(res)
                logging.info(f"Saved {res} to agent memory")
        
        state['vulnerabilities'].append(details) #save to memory all vulnerabilties found
                
        return {
            
            "sql_injection_results": details
        }
            
    async def _xss_attack_(self, state: PenTestState):
        url = state['url']
        
        return {
            
            'res': XSS._run(url)
        }
    
    async def _csrf_attack_(self, state: PenTestState):
        pass

    async def _shell_shock_(self, state: PenTestState):
        pass
    
    async def _binary_analysis_(self, state: PenTestState):
        pass

    def _create_graph_(self) -> StateGraph:
        graph = StateGraph(PenTestState)
        graph.add_node("start", self._plan_attack_ )
        graph.add_node("attack", self._xss_attack_)
        graph.add_node("end", END)
    
    
    def add_graph_edges(self, graph):
        graph.add_edge("start", "attack")
    
    
    async def _run_attack(self, graph):
        return graph.compile
    
    

#local testing
if __name__ == "__main__":
    attack = Attacker()

    
    
    