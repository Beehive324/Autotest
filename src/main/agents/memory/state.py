"""Define the state structures for the agent."""

from __future__ import annotations
import operator
from dataclasses import dataclass
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AnyMessage
from typing_extensions import TypedDict, Annotated, Sequence, List, Literal, Optional, Dict
import operator


#storage for the MAS System, data that the MAS System will hold
@dataclass
class State:
   IP_Port : str
  
 
@dataclass
class PenTestState:
    vulnerabilities: list
    domains: list
    emails: list
    passwords: list
    services: list
    report: str
    ports: list
    binary_contents: list #these can be stored in a hashmap e.g {ELF_HEADERS: binary_contents}


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]