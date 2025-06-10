from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage
from typing import Annotated, Sequence
from langgraph.graph import add_messages
from langchain_core.messages import AIMessage


class Messages(BaseModel):
    summary: str

class Vulnerability(BaseModel):
    """Represents a discovered vulnerability"""
    name: str
    severity: str
    description: str
    cvss_score: float
    affected_components: List[str]
    discovered_at: datetime = Field(default_factory=datetime.now)
    verified: bool = False
    

class Service(BaseModel):
    """Represents a discovered service"""
    name: str
    version: str
    port: int
    protocol: str
    state: str
    discovered_at: datetime = Field(default_factory=datetime.now)

class Subdomain(BaseModel):
    """Represents a discovered subdomain"""
    name: str
    ip_address: str
    discovered_at: datetime = Field(default_factory=datetime.now)
    services: List[Service] = []


class PenTestState(BaseModel):
    """State for the pentesting workflow"""
    ip_port: str = "localhost"
    planning_results: Dict = {}
    vulnerabilities: List[Vulnerability] = []
    services: List[Service] = []
    subdomains: List[Subdomain] = []
    open_ports: List[int] = []
    successful_exploits: List[str] = []
    failed_exploits: List[str] = []
    risk_score: float = 0.0
    remaining_steps: int = 5
    messages: Annotated[Sequence[BaseMessage], add_messages] = []
    start_time: datetime = Field(default_factory=datetime.now)
    current_phase: str = "planning"
    
    def validate_state(self) -> bool:
        """Validate the current state"""
        if self.remaining_steps <= 0:
            return False
        return True

def validate_messages(state: PenTestState) -> bool:
    """Validate message state"""
    if not state.messages:
        return False
    # Check for empty messages
    if any(not msg.content for msg in state.messages):
        return False
    return True

def supervisor_routing(state: PenTestState) -> str:
    """Determine next phase based on state and current phase"""
    try:
        if not state.validate_state():
            return "reporting"  # End the workflow if no steps remaining
            
        if not validate_messages(state):
            state.messages = []  # Reset invalid messages
            return state.current_phase  # Stay in current phase
            
        # Track phase transitions
        if state.current_phase == "planning":
            if state.planning_results and is_phase_complete(state, "planning"):
                next_phase = "recon"
                if validate_phase_transition(state, next_phase):
                    state.current_phase = next_phase
                    return next_phase
            return "planning"
            
        elif state.current_phase == "recon":
            if (state.open_ports or state.services) and is_phase_complete(state, "recon"):
                next_phase = "attack"
                if validate_phase_transition(state, next_phase):
                    state.current_phase = next_phase
                    return next_phase
            return "recon"
            
        elif state.current_phase == "attack":
            if len(state.successful_exploits) > 0:
                next_phase = "reporting"
                if validate_phase_transition(state, next_phase):
                    state.current_phase = next_phase
                    return next_phase
            return "attack"
            
        elif state.current_phase == "reporting":
            return "reporting"
            
        return "planning"  # Default case
        
    except Exception as e:
        # Log the error and return to a safe state
        state.messages.append(AIMessage(content=f"Error in supervisor routing: {str(e)}"))
        return state.current_phase

def is_phase_complete(state: PenTestState, phase: str) -> bool:
    """Check if a phase is complete"""
    if phase == "planning":
        return bool(state.planning_results)
    elif phase == "recon":
        return bool(state.open_ports or state.services)
    elif phase == "attack":
        return bool(state.successful_exploits or state.failed_exploits)
    elif phase == "reporting":
        return True
    return False
    
def validate_phase_transition(state: PenTestState, next_phase: str) -> bool:
    """Validate if a phase transition is valid"""
    valid_transitions = {
        "planning": ["recon", "planning"],
        "recon": ["attack", "recon"],
        "attack": ["reporting", "attack", "recon"],
        "reporting": ["reporting"]
    }
    return next_phase in valid_transitions.get(state.current_phase, [])
    