"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass
from langgraph import add_messages
from langchain_core.messages import BaseMessage, AnyMessage
from typiing_extensions import TypedDict, Annotated, Sequence, List, Literal, Optional, Dict
import operator

@dataclass
class State:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    for more information.
    """

    changeme: str = "example"

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]