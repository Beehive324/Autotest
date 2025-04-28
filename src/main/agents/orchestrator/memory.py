from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

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
    planning_results: Dict = {}
    vulnerabilities: List[Vulnerability] = []
    services: List[Service] = []
    subdomains: List[Subdomain] = []
    open_ports: List[int] = []
    successful_exploits: List[str] = []
    failed_exploits: List[str] = []
    risk_score: float = 0.0
    start_time: datetime = Field(default_factory=datetime.now)
    
    def calculate_risk_score(self) -> float:
        """Calculate overall risk score based on vulnerabilities"""
        if not self.vulnerabilities:
            return 0.0
            
        severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        
        total_score = sum(
            severity_weights.get(v.severity.lower(), 0.0) * v.cvss_score
            for v in self.vulnerabilities
        )
        
        self.risk_score = total_score / len(self.vulnerabilities)
        return self.risk_score 