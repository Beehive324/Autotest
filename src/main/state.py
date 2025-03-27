"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AnyMessage
from typing_extensions import TypedDict, Annotated, Sequence, List, Literal, Optional, Dict
import operator


#storage for the MAS System, data that the MAS System will hold
@dataclass
class State:
   domains_scanned : list
   scan_results : str
   analysis : str
   
   

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]