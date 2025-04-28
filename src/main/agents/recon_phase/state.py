from typing import List, Dict, Optional
from pydantic import BaseModel

class ReconState(BaseModel):
    """State for the reconnaissance phase."""
    target_domain: str
    subdomains: List[str] = []
    open_ports: Dict[str, List[int]] = {}
    services: Dict[str, Dict[int, str]] = {}
    vulnerabilities: List[Dict] = []
    notes: List[str] = []
    current_step: str = "initial"
    completed_steps: List[str] = []
    
    def add_subdomain(self, subdomain: str) -> None:
        """Add a subdomain to the list if it's not already present."""
        if subdomain not in self.subdomains:
            self.subdomains.append(subdomain)
            
    def add_port(self, subdomain: str, port: int) -> None:
        """Add an open port for a subdomain."""
        if subdomain not in self.open_ports:
            self.open_ports[subdomain] = []
        if port not in self.open_ports[subdomain]:
            self.open_ports[subdomain].append(port)
            
    def add_service(self, subdomain: str, port: int, service: str) -> None:
        """Add a service for a port on a subdomain."""
        if subdomain not in self.services:
            self.services[subdomain] = {}
        self.services[subdomain][port] = service
        
    def add_vulnerability(self, vulnerability: Dict) -> None:
        """Add a vulnerability to the list."""
        self.vulnerabilities.append(vulnerability)
        
    def add_note(self, note: str) -> None:
        """Add a note to the list."""
        self.notes.append(note)
        
    def mark_step_completed(self, step: str) -> None:
        """Mark a step as completed."""
        if step not in self.completed_steps:
            self.completed_steps.append(step)
            
    def update_current_step(self, step: str) -> None:
        """Update the current step."""
        self.current_step = step 