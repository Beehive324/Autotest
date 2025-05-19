from datetime import datetime
from langchain_core.tools import tool
import requests
from pydantic import BaseModel, Field
import sublist3r
from ...state import PenTestState
from typing import List, Optional, Dict, Annotated, Sequence, TypedDict, Any
from langchain.tools import Tool
from langgraph.graph import StateGraph, END, START
from .tools.attacktools import (SQL_Injection, XSS, ShellShock, BinaryAnalysis)
import logging
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from IPython.display import Image, display
from langchain_core.callbacks import BaseCallbackManager
import json
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)

class URL(BaseModel):
    url: str = Field(description="The URL to target")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "http://example.com"
            }
        }

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    vulnerabilities: List[Dict]
    ip_port: str
    open_ports: List[int]

class Attacker(Runnable):
    def __init__(self, model, tools: List = None):
        self.model = model
        self.tools = [
            Tool(
                name="sql_injection",
                func=SQL_Injection._run,
                description="Performs SQL injection attacks",
                args_schema=URL
            ),
            Tool(
                name="xss",
                func=XSS._run,
                description="Performs XSS attacks",
                args_schema=URL
            ),
            Tool(
                name="shell_shock",
                func=ShellShock._run,
                description="Performs ShellShock attacks",
                args_schema=URL
            ),
            Tool(
                name="binary_analysis",
                func=BinaryAnalysis._run,
                description="Performs binary analysis",
                args_schema=URL
            )
        ]
        self.name = "Attacker"
        
        # Create handoff tools
        self.handoff_tools = [
            create_handoff_tool(agent_name="sql_injection_agent", description="Transfer to SQL Injection expert for SQL injection attacks"),
            create_handoff_tool(agent_name="xss_agent", description="Transfer to XSS expert for cross-site scripting attacks"),
            create_handoff_tool(agent_name="shell_shock_agent", description="Transfer to ShellShock expert for shell shock exploits"),
            create_handoff_tool(agent_name="binary_analysis_agent", description="Transfer to Binary Analysis expert for binary analysis")
        ]
        
        # Create the graph
        self.workflow = self._create_graph()
        self.app = self.workflow.compile()
    
    def _create_graph(self) -> StateGraph:
        """Create the workflow graph using swarm with specialized attack nodes."""
        # Create specialized agents for each attack type
        sql_injection_tools = [self.tools[0]] + [tool for tool in self.handoff_tools if tool.name != "transfer_to_sql_injection_agent"]
        sql_injection_model = self.model.bind_tools(sql_injection_tools)
        sql_injection_agent = create_react_agent(
            sql_injection_model,
            sql_injection_tools,
            prompt="""You are a SQL injection expert. Your task is to identify and exploit SQL injection vulnerabilities.
            Think step by step about:
            1. Identifying potential SQL injection points
            2. Testing for SQL injection vulnerabilities
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="sql_injection_agent"
        )
        
        xss_tools = [self.tools[1]] + [tool for tool in self.handoff_tools if tool.name != "transfer_to_xss_agent"]
        xss_model = self.model.bind_tools(xss_tools)
        xss_agent = create_react_agent(
            xss_model,
            xss_tools,
            prompt="""You are an XSS expert. Your task is to identify and exploit cross-site scripting vulnerabilities.
            Think step by step about:
            1. Finding input fields that might be vulnerable to XSS
            2. Testing different XSS payloads
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="xss_agent"
        )
        
        shell_shock_tools = [self.tools[2]] + [tool for tool in self.handoff_tools if tool.name != "transfer_to_shell_shock_agent"]
        shell_shock_model = self.model.bind_tools(shell_shock_tools)
        shell_shock_agent = create_react_agent(
            shell_shock_model,
            shell_shock_tools,
            prompt="""You are a ShellShock expert. Your task is to identify and exploit ShellShock vulnerabilities.
            Think step by step about:
            1. Identifying potential ShellShock vulnerabilities
            2. Testing for ShellShock exploits
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="shell_shock_agent"
        )
        
        binary_analysis_tools = [self.tools[3]] + [tool for tool in self.handoff_tools if tool.name != "transfer_to_binary_analysis_agent"]
        binary_analysis_model = self.model.bind_tools(binary_analysis_tools)
        binary_analysis_agent = create_react_agent(
            binary_analysis_model,
            binary_analysis_tools,
            prompt="""You are a binary analysis expert. Your task is to analyze and exploit binary vulnerabilities.
            Think step by step about:
            1. Identifying potential binary vulnerabilities
            2. Analyzing binary files and executables
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="binary_analysis_agent"
        )
        
        # Create the swarm with all agents
        workflow = create_swarm(
            [
                sql_injection_agent,
                xss_agent,
                shell_shock_agent,
                binary_analysis_agent
            ],
            default_active_agent="sql_injection_agent"
        )
        
        return workflow
    
    def invoke(self, input: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        """Invoke the attacker workflow."""
        return self.app.invoke(input, config)
    
    async def ainvoke(self, input: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        """Asynchronously invoke the attacker workflow."""
        return await self.app.ainvoke(input, config)
    
    def get_tools(self) -> List[Tool]:
        return self.tools
    
    def display_graph(self):
        """Display the workflow graph."""
        graph_path = 'attack_workflow.png'
        self.workflow.get_graph().draw_png(graph_path)
        print(f"Graph visualization saved to: {graph_path}")
        return display(Image(graph_path))

# Local testing
if __name__ == "__main__":
    from langchain_ollama import ChatOllama
    model = ChatOllama(model="llama2")
    attacker = Attacker(model=model)
    
    # Create a test state
    test_state = PenTestState(
        ip_port="192.168.1.1:80,443",
        open_ports=[80, 443],
        input_message="Start attack phase on 192.168.1.1",
        remaining_steps=5,
        planning_results={},
        vulnerabilities=[],
        services=[],
        subdomains=[],
        successful_exploits=[],
        failed_exploits=[],
        risk_score=0.0
    )
    
    # Run attack phase (in async context)
    import asyncio
    result = asyncio.run(attacker.ainvoke(test_state))
    print("Attack Results:", result.vulnerabilities) 