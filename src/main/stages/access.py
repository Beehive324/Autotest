from typing_extensions import TypedDict 
from langgraph.graph import StateGraph, START, END
from ..agents.memory.state import PenTestState
from typing import List
from ..agents import Attacker


class AccessState(TypedDict):
    vulnerabilities: List[str]
    messages: List[str]
    


def _start_attack(state: PenTestState):
    
    return {
        
        "begin_attack": state.ports
    }


def _attack_agent(state: PenTestState):
    ip_port = state.ports
    attacker = Attacker(model="ollama3x3")
    attacker._run_attack # runs the attack agent


workflow = StateGraph(PenTestState)

workflow.add_node("begin_plan", _start_attack )
workflow.add_node("attack_agent", _attack_agent)


workflow.add_edge(START, "begin_plan")
workflow.add_edge("begin_plan", END)

graph = workflow.compile()


state = graph.invoke({"ulr": "localhost"})

