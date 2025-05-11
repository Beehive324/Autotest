from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime



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
    ip_port: str
    input_message: str
    planning_results: Dict = {}
    vulnerabilities: List[Vulnerability] = []
    services: List[Service] = []
    subdomains: List[Subdomain] = []
    open_ports: List[int] = []
    successful_exploits: List[str] = []
    failed_exploits: List[str] = []
    risk_score: float = 0.0
    remaining_steps: int
    messages: List[str] = []
    start_time: datetime = Field(default_factory=datetime.now)
    