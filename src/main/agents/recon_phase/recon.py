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
from langgraph_swarm import create_handoff_tool, create_swarm
from typing import List, Optional, Dict
from langchain_core.runnables import Runnable

import logging

logger = logging.getLogger(__name__)

class Recon:
    def __init__(self, model):
        self.model = model
        self.tools = [
            Nmap(),
            Resolve(),
            Subdomain_Enum_CRT(),
            Subdomain_Enum_gobuster(),
            Subdomain_Enum_findomain(),
            Subdomain_Enum_amass(),
            Subdomain_Enum_wayback(),
            Subdomain_Enum_sublist3r(),
            APIDiscovery(),
            WebSearch(),
            Masscan(),
        ]
        self.name = "Recon"
        
        # Create specialized sub-agents
        self.port_scanner = create_react_agent(
            model,
            [Nmap(), Masscan(), create_handoff_tool(agent_name="vulnerability_analyzer")],
            prompt="You are a port scanning expert. Your task is to identify open ports and services on target systems.",
            name="port_scanner"
        )
        
        self.vulnerability_analyzer = create_react_agent(
            model,
            [create_handoff_tool(agent_name="port_scanner"), create_handoff_tool(agent_name="subdomain_enum")],
            prompt="You are a vulnerability analysis expert. Your task is to analyze scan results and identify potential security issues.",
            name="vulnerability_analyzer"
        )
        
        self.subdomain_enum = create_react_agent(
            model,
            [
                Subdomain_Enum_CRT(),
                Subdomain_Enum_gobuster(),
                Subdomain_Enum_findomain(),
                Subdomain_Enum_amass(),
                Subdomain_Enum_wayback(),
                Subdomain_Enum_sublist3r(),
                create_handoff_tool(agent_name="port_scanner")
            ],
            prompt="You are a subdomain enumeration expert. Your task is to discover subdomains and related infrastructure.",
            name="subdomain_enum"
        )
        
        # Create the swarm
        self.checkpointer = InMemorySaver()
        self.workflow = create_swarm(
            [self.port_scanner, self.vulnerability_analyzer, self.subdomain_enum],
            default_active_agent="port_scanner"
        )
        self.app = self.workflow.compile(checkpointer=self.checkpointer)
    
    def get_tools(self):
        return self.tools

    async def ainvoke(self, state: PenTestState, config: Optional[Dict] = None, **kwargs) -> PenTestState:
        """Asynchronously invoke the recon agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after recon phase
        """
        try:
            config = config or {"configurable": {"thread_id": state.ip_port}}
            
            # Initial port scan
            turn_1 = await self.app.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Scan the target {state.ip_port} for open ports and services"
                        }
                    ]
                },
                config
            )
            
            # Analyze results
            turn_2 = await self.app.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Analyze the scan results for {state.ip_port}"
                        }
                    ]
                },
                config
            )
            
            # If it's a domain, perform subdomain enumeration
            if any(c.isalpha() for c in state.ip_port):
                turn_3 = await self.app.ainvoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Enumerate subdomains for {state.ip_port}"
                            }
                        ]
                    },
                    config
                )
                
                # Update state with subdomain results
                state.subdomains = turn_3.get("subdomains", [])
            
            # Update state with scan results
            state.open_ports = turn_1.get("open_ports", [])
            state.vulnerabilities = turn_2.get("vulnerabilities", [])
            
            # Add messages to state
            state.messages.append(AIMessage(content=f"Recon phase completed. Found {len(state.open_ports)} open ports and {len(state.vulnerabilities)} vulnerabilities."))
            
            return state
            
        except Exception as e:
            error_message = f"Error in recon phase: {str(e)}"
            state.messages.append(AIMessage(content=error_message))
            return state
    
    def get_agent(self) -> Runnable:
        """Get the agent runnable for use in the workflow.
        
        Returns:
            The agent runnable
        """
        return self.app
    
    def display_graph(self):
        # Save the graph visualization
        graph_path = 'recon_workflow.png'
        # Compile the workflow first
        compiled_workflow = self.workflow.compile()
        # Use the compiled graph for visualization
        compiled_workflow.get_graph().draw_png(graph_path)
        print(f"Graph visualization saved to: {graph_path}")
        
        # Display the graph
        return display(Image(graph_path))

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