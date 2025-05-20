from typing import Any, Dict, List, Optional, Type
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from datetime import datetime
from ...agents.orchestrator.memory import PenTestState



class Planner(Runnable):
    def __init__(self, model):
        """Initialize the Planner with a language model.
        
        Args:
            model: The language model to use for planning and analysis
        """
        self.model = model
        self.name = "Planner"
        self.tools = []  # Add your planning tools here
        
        # Create the base prompt template for the ReAct agent
        self.prompt = PromptTemplate.from_template(
            """You are a pentest expert. You are responsible for planning the pentest.
            You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}
            Thought:{agent_scratchpad}"""
        )
        
        # Create the agent using create_react_agent
        self.agent = create_react_agent(
            llm=self.model,
            tools=self.tools,
            prompt=self.prompt,
            stop_sequence=True
        )
        
        # Create the agent executor
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools)
        
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
        """Synchronously invoke the planner agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after planning phase
        """
        try:
            # Initialize messages if not present
            if not hasattr(state, 'messages'):
                state.messages = []
                
            # Use the stored workflow
            state = self.workflow.invoke(state)
            
            # Then run the ReAct agent for any additional planning
            input_data = {
                "input": state.messages[-1].content if state.messages else "Start planning phase",
                "agent_scratchpad": ""
            }
            
            result = self.executor.invoke(input_data)
            state.messages.append(AIMessage(content=result["output"]))
            
            return state
            
        except Exception as e:
            error_message = f"Error in planning phase: {str(e)}"
            if not hasattr(state, 'messages'):
                state.messages = []
            state.messages.append(AIMessage(content=error_message))
            return state

    async def ainvoke(self, state: PenTestState, config: Optional[RunnableConfig] = None, **kwargs) -> PenTestState:
        """Asynchronously invoke the planner agent.
        
        Args:
            state: The current state of the pentest
            config: Optional configuration dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Updated state after planning phase
        """
        try:
            # Initialize messages if not present
            if not hasattr(state, 'messages'):
                state.messages = []
                
            # Use the stored workflow
            state = await self.workflow.ainvoke(state)
            
            # Then run the ReAct agent for any additional planning
            input_data = {
                "input": state.messages[-1].content if state.messages else "Start planning phase",
                "agent_scratchpad": ""
            }
            
            result = await self.executor.ainvoke(input_data)
            state.messages.append(AIMessage(content=result["output"]))
            
            return state
            
        except Exception as e:
            error_message = f"Error in planning phase: {str(e)}"
            if not hasattr(state, 'messages'):
                state.messages = []
            state.messages.append(AIMessage(content=error_message))
            return state

    def _planning_phase(self, state: PenTestState):
        planner_instructions = f"""You are tasked with creating a plan based on the findings of {state.open_ports}
        Conduct the best way to carry out penetration testing based on these open ports.
        Consider:
        1. Common vulnerabilities for these services
        2. Recommended testing methodologies
        3. Priority of testing based on service criticality
        """
        plan = self.model.invoke([
            SystemMessage(content=planner_instructions),
            HumanMessage(content=f"Analyze the following nmap results and create a detailed testing plan: {state.open_ports}")
        ])
        return {
            "messages": state.messages + [AIMessage(content=str(plan))],
            "planning_results": {
                "start_time": datetime.now(),
                "scope": "Initial scope defined",
                "objectives": ["Identify vulnerabilities", "Assess security posture"],
                "planning_results": plan,
                "last_updated": datetime.now()
            }
        }
    
    async def _risk_assessment(self, state: PenTestState):
        """Perform initial risk assessment.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with risk assessment results
        """
        if not state.planning_results:
            state.planning_results = {}
            
        risk_instructions = f"""Based on the open ports {state.open_ports}, assess the following:
        1. Critical assets that might be exposed
        2. Potential threat actors
        3. Possible attack vectors
        4. Overall risk level
        """
        
        risk_assessment = self.model.invoke([
            SystemMessage(content=risk_instructions),
            HumanMessage(content="Provide a detailed risk assessment")
        ])
            
        return {
            "messages": state.messages + [AIMessage(content=str(risk_assessment))],
            "planning_results": {
                "critical_assets": [],
                "threat_actors": [],
                "attack_vectors": [],
                "risk_level": "medium",
                "risk_assessment": risk_assessment,
                "last_updated": datetime.now()
            }
        }
    
    async def _define_scope(self, state: PenTestState):
        """Define the scope of the pentest.
        
        Args:
            state: Current state of the penetration test
            
        Returns:
            Updated state with defined scope
        """
        if not state.planning_results:
            state.planning_results = {}
            
        scope_instructions = f"""Based on the target {state.ip_port}, define a clear scope including:
        1. Specific targets to test
        2. Any exclusions or limitations
        3. Testing methodologies to be used
        """
        
        scope_definition = self.model.invoke([
            SystemMessage(content=scope_instructions),
            HumanMessage(content="Define the testing scope")
        ])
            
        return {
            "messages": state.messages + [AIMessage(content=str(scope_definition))],
            "planning_results": {
                "scope": {
                    "targets": state.ip_port,
                    "exclusions": [],
                    "testing_methods": ["automated", "manual"],
                    "scope_definition": scope_definition
                },
                "last_updated": datetime.now()
            },
            "current_phase": "planning"
        }
    
    def _create_graph(self) -> StateGraph:
        """Create the planning workflow graph.
        
        Returns:
            StateGraph: The configured planning workflow
        """
        graph = StateGraph(PenTestState)
        graph.add_node("planning_phase", self._planning_phase)
        graph.add_node("risk_assessment", self._risk_assessment)
        graph.add_node("scope_definition", self._define_scope)
        return graph
    
    def add_graph_edges(self, graph: StateGraph) -> None:
        """Add edges to the planning workflow graph.
        
        Args:
            graph: The StateGraph to add edges to
        """
        graph.add_edge(START, "planning_phase")
        graph.add_edge("planning_phase", "risk_assessment")
        graph.add_edge("risk_assessment", "scope_definition")
        graph.add_edge("scope_definition", END)
    
    def get_agent(self) -> Runnable:
        """Get the agent runnable for use in the workflow.
        
        Returns:
            The agent runnable
        """
        return self.executor

# For local testing
if __name__ == "__main__":
    from langchain_ollama import ChatOllama
    
    # Initialize with Ollama model
    model = ChatOllama(model="llama2", temperature=1)
    planner = Planner(model)
    
    # Create a test state with all required fields
    test_state = PenTestState(
        ip_port="192.168.1.1:80,443",
        open_ports=[80, 443],
        input_message="Start pentesting on 192.168.1.1",
        remaining_steps=5,
        planning_results={},
        vulnerabilities=[],
        services=[],
        subdomains=[],
        successful_exploits=[],
        failed_exploits=[],
        risk_score=0.0,
        messages=[]  # Initialize messages list
    )
    
    # Run planning (in async context)
    import asyncio
    result = asyncio.run(planner.ainvoke(test_state))
    print("Planning Results:", result.planning_results) 