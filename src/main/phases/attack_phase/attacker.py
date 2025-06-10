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
from langchain_core.runnables import Runnable
from langchain_community.tools import ShellTool

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
        self.tools = [
            shell_tool
        ]
        self.name = "Attacker"
        
        # Create specialized sub-agents
        self.sql_injection_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a SQL injection expert. Your task is to identify and exploit SQL injection vulnerabilities.
            Think step by step about:
            1. Identifying potential SQL injection points
            2. Testing for SQL injection vulnerabilities
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="sql_injection_agent"
        )
        
        self.xss_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are an XSS expert. Your task is to identify and exploit cross-site scripting vulnerabilities.
            Think step by step about:
            1. Finding input fields that might be vulnerable to XSS
            2. Testing different XSS payloads
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="xss_agent"
        )
        
        self.shell_shock_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a ShellShock expert. Your task is to identify and exploit ShellShock vulnerabilities.
            Think step by step about:
            1. Identifying potential ShellShock vulnerabilities
            2. Testing for ShellShock exploits
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="shell_shock_agent"
        )
        
        self.binary_analysis_agent = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a binary analysis expert. Your task is to analyze and exploit binary vulnerabilities.
            Think step by step about:
            1. Identifying potential binary vulnerabilities
            2. Analyzing binary files and executables
            3. Exploiting any found vulnerabilities
            4. Documenting your findings""",
            name="binary_analysis_agent"
        )

    @property
    def input_schema(self) -> Type[PenTestState]:
        """Return the input schema type."""
        return PenTestState

    @property
    def output_schema(self) -> Type[PenTestState]:
        """Return the output schema type."""
        return PenTestState

    def invoke(self, state: PenTestState, config: Optional[RunnableConfig] = None, **kwargs) -> PenTestState:
        """Synchronously invoke the attacker agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after attack phase
        """
        try:
            # Initialize messages if not present
            if not hasattr(state, 'messages'):
                state.messages = []
                
            # Create and run the attack workflow
            graph = self._create_graph()
            self.add_graph_edges(graph)
            compiled_graph = graph.compile()
            state = compiled_graph.invoke(state)
            
            return state
            
        except Exception as e:
            error_message = f"Error in attack phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state

    async def ainvoke(self, state: PenTestState, config: Optional[RunnableConfig] = None, **kwargs) -> PenTestState:
        """Asynchronously invoke the attacker agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after attack phase
        """
        try:
            # Initialize messages if not present
            if not hasattr(state, 'messages'):
                state.messages = []
                
            # Create and run the attack workflow
            graph = self._create_graph()
            self.add_graph_edges(graph)
            compiled_graph = graph.compile()
            state = await compiled_graph.ainvoke(state)
            
            return state
            
        except Exception as e:
            error_message = f"Error in attack phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state

    def _sql_injection_phase(self, state: PenTestState) -> PenTestState:
        """Perform SQL injection attacks.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with SQL injection results
        """
        logger.info("Starting SQL injection phase...")
        
        sql_result = self.sql_injection_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Test for SQL injection vulnerabilities on {state.ip_port}"
                    }
                ]
            }
        )
        
        # Process SQL injection results
        if sql_result.get("vulnerabilities"):
            state.vulnerabilities.extend(sql_result["vulnerabilities"])
            state.messages.append(AIMessage(content=f"SQL injection testing completed. Found {len(sql_result['vulnerabilities'])} vulnerabilities."))
        
        return state
    
    def _xss_phase(self, state: PenTestState) -> PenTestState:
        """Perform XSS attacks.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with XSS results
        """
        logger.info("Starting XSS phase...")
        
        xss_result = self.xss_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Test for XSS vulnerabilities on {state.ip_port}"
                    }
                ]
            }
        )
        
        # Process XSS results
        if xss_result.get("vulnerabilities"):
            state.vulnerabilities.extend(xss_result["vulnerabilities"])
            state.messages.append(AIMessage(content=f"XSS testing completed. Found {len(xss_result['vulnerabilities'])} vulnerabilities."))
        
        return state
    
    def _shell_shock_phase(self, state: PenTestState) -> PenTestState:
        """Perform ShellShock attacks.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with ShellShock results
        """
        logger.info("Starting ShellShock phase...")
        
        shell_shock_result = self.shell_shock_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Test for ShellShock vulnerabilities on {state.ip_port}"
                    }
                ]
            }
        )
        
        # Process ShellShock results
        if shell_shock_result.get("vulnerabilities"):
            state.vulnerabilities.extend(shell_shock_result["vulnerabilities"])
            state.messages.append(AIMessage(content=f"ShellShock testing completed. Found {len(shell_shock_result['vulnerabilities'])} vulnerabilities."))
        
        return state
    
    def _binary_analysis_phase(self, state: PenTestState) -> PenTestState:
        """Perform binary analysis.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with binary analysis results
        """
        logger.info("Starting binary analysis phase...")
        
        binary_result = self.binary_analysis_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Analyze binary files on {state.ip_port}"
                    }
                ]
            }
        )
        
        # Process binary analysis results
        if binary_result.get("vulnerabilities"):
            state.vulnerabilities.extend(binary_result["vulnerabilities"])
            state.messages.append(AIMessage(content=f"Binary analysis completed. Found {len(binary_result['vulnerabilities'])} vulnerabilities."))
        
        return state
    
    def _create_graph(self) -> StateGraph:
        """Create the attack workflow graph.
        
        Returns:
            StateGraph: The configured attack workflow
        """
        graph = StateGraph(PenTestState)
        graph.add_node("sql_injection", self._sql_injection_phase)
        graph.add_node("xss", self._xss_phase)
        graph.add_node("shell_shock", self._shell_shock_phase)
        graph.add_node("binary_analysis", self._binary_analysis_phase)
        return graph
    
    def add_graph_edges(self, graph: StateGraph) -> None:
        """Add edges to the attack workflow graph.
        
        Args:
            graph: The StateGraph to add edges to
        """
        graph.add_edge(START, "sql_injection")
        graph.add_edge("sql_injection", "xss")
        graph.add_edge("xss", "shell_shock")
        graph.add_edge("shell_shock", "binary_analysis")
        graph.add_edge("binary_analysis", END)
    
    def get_agent(self) -> Runnable:
        """Get the agent runnable for use in the workflow.
        
        Returns:
            The agent runnable
        """
        return self.sql_injection_agent  # Return the primary agent

if __name__ == "__main__":
    from langchain_ollama import ChatOllama
    
    # Initialize with Ollama model
    model = ChatOllama(model="llama2", temperature=1)
    attacker = Attacker(model)
    
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
    print("Attack Results:")
    print("Vulnerabilities:", result.vulnerabilities) 