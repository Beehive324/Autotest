from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langchain.tools import Tool
from .state import ReconState
from .tools.recontools import (
    Nmap, Resolve, 
    Subdomain_Enum_CRT, Subdomain_Enum_gobuster, Subdomain_Enum_findomain,
    Subdomain_Enum_amass, Subdomain_Enum_wayback, Subdomain_Enum_sublist3r,
    APIDiscovery, WebSearch, Masscan
)
from IPython.display import Image, display
from ...agents.orchestrator.memory import PenTestState
import socket
import datetime
import nmap
from ...agents.orchestrator.memory import Messages
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from typing import List, Optional, Dict, Type
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langchain_community.tools import ShellTool

import logging

logger = logging.getLogger(__name__)

shell_tool = ShellTool()

class Recon(Runnable):
    def __init__(self, model):
        self.model = model
        self.tools = [
            shell_tool
        ]
        self.name = "Recon"
        
        # Create specialized sub-agents
        self.port_scanner = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a port scanning expert. Your task is to identify open ports and services on target systems.
            After scanning, return the results in a format that can be used by the vulnerability analyzer.""",
            name="port_scanner"
        )
        
        self.vulnerability_analyzer = create_react_agent(
            model,
            [shell_tool],
            prompt="""You are a vulnerability analysis expert. Your task is to analyze scan results and identify potential security issues.
            Use the shell tool to run vulnerability scans and analyze the results.""",
            name="vulnerability_analyzer"
        )
        
        self.subdomain_enum = create_react_agent(
            model,
            [shell_tool],
            prompt="You are a subdomain enumeration expert. Your task is to discover subdomains and related infrastructure.",
            name="subdomain_enum"
        )
        
        # Create and store the workflow graph
        self.workflow = self._create_graph()
        self.add_graph_edges(self.workflow)
        self.workflow = self.workflow.compile()  # Compile the workflow

    @property
    def input_schema(self) -> Type[PenTestState]:
        """Return the input schema type."""
        return PenTestState

    @property
    def output_schema(self) -> Type[PenTestState]:
        """Return the output schema type."""
        return PenTestState

    def invoke(self, state: PenTestState, config: Optional[RunnableConfig] = None, **kwargs) -> PenTestState:
        """Synchronously invoke the recon agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after recon phase
        """
        try:
            # Initialize messages if not present
            if not hasattr(state, 'messages'):
                state.messages = []
                
            # Use the stored workflow
            state = self.workflow.invoke(state)
            return state
            
        except Exception as e:
            error_message = f"Error in recon phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state

    async def ainvoke(self, state: PenTestState, config: Optional[RunnableConfig] = None, **kwargs) -> PenTestState:
        """Asynchronously invoke the recon agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after recon phase
        """
        try:
            # Initialize messages if not present
            if not hasattr(state, 'messages'):
                state.messages = []
                
            # Use the stored workflow
            state = await self.workflow.ainvoke(state)
            return state
            
        except Exception as e:
            error_message = f"Error in recon phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state


    def _port_scanning_phase(self, state: PenTestState):
        new_messages = []
        new_open_ports = []
        new_services = []
        input_message = {
            "role": "user",
            "content": f"Scan {state.ip_port} for open ports using nmap"
        }
        for step in self.port_scanner.stream(
            {"messages": [input_message]},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            new_messages.append(msg)
            new_open_ports.append(msg.content)
            new_services.append(msg.content)
        # Return only the updates!
        return {
            "messages": state.messages + new_messages,
            "open_ports": state.open_ports + new_open_ports,
            "services": state.services + new_services,
        }
    
    def _vulnerability_analysis_phase(self, state: PenTestState):
        new_messages = []
        new_vulnerabilities = []
        new_services = []
        new_open_ports = []
        input_message = {
            "role": "user",
            "content": f"Analyze the scan results for {state.ip_port}"
        }
        for step in self.vulnerability_analyzer.stream(
            {"messages": [input_message]},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            new_messages.append(msg)
            new_vulnerabilities.append(msg.content)
            new_services.append(msg.content)
            new_open_ports.append(msg.content)
        return {
            "messages": state.messages + new_messages,
            "vulnerabilities": state.vulnerabilities + new_vulnerabilities,
            "services": state.services + new_services,
            "open_ports": state.open_ports + new_open_ports,
        }
    
    def _subdomain_enumeration_phase(self, state: PenTestState) -> PenTestState:
        """Perform subdomain enumeration if target is a domain.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with subdomain enumeration results
        """
        if any(c.isalpha() for c in state.ip_port):
            logger.info("Starting subdomain enumeration phase...")
            
            subdomain_result = self.subdomain_enum.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Enumerate subdomains for {state.ip_port}"
                        }
                    ]
                }
            )
            
            state.subdomains = subdomain_result.get("subdomains", [])
            state.messages.append(AIMessage(content=f"Subdomain enumeration completed. Found {len(state.subdomains)} subdomains."))
        
        return state
    
    def _create_graph(self) -> StateGraph:
        """Create the recon workflow graph.
        
        Returns:
            StateGraph: The configured recon workflow
        """
        graph = StateGraph(PenTestState)
        graph.add_node("port_scanning", self._port_scanning_phase)
        graph.add_node("vulnerability_analysis", self._vulnerability_analysis_phase)
        #graph.add_node("subdomain_enumeration", self._subdomain_enumeration_phase)
        return graph
    
    def add_graph_edges(self, graph: StateGraph) -> None:
        """Add edges to the recon workflow graph.
        
        Args:
            graph: The StateGraph to add edges to
        """
        graph.add_edge(START, "port_scanning")
        graph.add_edge("port_scanning", "vulnerability_analysis")
        graph.add_edge("vulnerability_analysis", END)
        #graph.add_edge("subdomain_enumeration", END)
    
    def get_agent(self) -> Runnable:
        """Get the agent runnable for use in the workflow.
        
        Returns:
            The agent runnable
        """
        return self.port_scanner  # Return the primary agent

if __name__ == "__main__":
    from langchain_ollama import ChatOllama
    
    # Initialize with Ollama model
    model = ChatOllama(model="llama2", temperature=1)
    recon = Recon(model)
    
    # Create a test state
    test_state = PenTestState(
        ip_port="example.com:80,443",
        open_ports=[],
        input_message="Start recon phase on example.com",
        remaining_steps=5,
        planning_results={},
        vulnerabilities=[],
        services=[],
        subdomains=[],
        successful_exploits=[],
        failed_exploits=[],
        risk_score=0.0
    )
    
    # Run recon phase (in async context)
    import asyncio
    result = asyncio.run(recon.ainvoke(test_state))
    print("Recon Results:")
    print("Open Ports:", result.open_ports)
    print("Vulnerabilities:", result.vulnerabilities)
    print("Subdomains:", result.subdomains)