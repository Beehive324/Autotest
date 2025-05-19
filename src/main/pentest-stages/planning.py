from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from ..agents.memory.state import PenTestState
from typing import List
from ..agents import Planner


def initialize():
    
    return {
        
        "planner": Planner(model="ollama3.2")
    }

def create_plan(state: PenTestState):
    planner = Planner()
    planner.run_planning(state)


def finalise_plan(state: PenTestState):
    pass

    
workflow = StateGraph(PenTestState)
workflow.add_node("create_plan", create_plan)
workflow.add_edge(START, "create_plan")
workflow.add_edge("create_plan", "finalise_plan")
workflow.add_edge("finalise_plan", END)

graph = workflow.compile()


    
    
    
    