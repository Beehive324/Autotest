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
class CRSFState:
    vulnerabilities: List[str]
    finding: List[str]
    
    
@dataclass
class XSSState:
    vulnerabilities: List[str]
    url: str
    payloads: List[str]
    url_contents: str
    
 
@dataclass
class PenTestState:
    vulnerabilities: List[str]
    domains: List[str]
    emails: List[str]
    passwords: List[str]
    services: List[str]
    report: List[str]
    ports: List[str]
    binary_contents: List[str] #these can be stored in a hashmap e.g {ELF_HEADERS: binary_contents}


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]