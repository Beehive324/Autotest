from typing import List, Dict, Optional
from pydantic import BaseModel

class PenTestState(BaseModel):
    """State for the pentesting process."""
    target_domain: str
    findings: List[Dict] = []
    report_sections: List[Dict] = []
    current_step: str = "initial"
    completed_steps: List[str] = []
    
    def add_finding(self, finding: Dict) -> None:
        """Add a finding to the list."""
        self.findings.append(finding)
        
    def add_report_section(self, section: Dict) -> None:
        """Add a section to the report."""
        self.report_sections.append(section)
        
    def mark_step_completed(self, step: str) -> None:
        """Mark a step as completed."""
        if step not in self.completed_steps:
            self.completed_steps.append(step)
            
    def update_current_step(self, step: str) -> None:
        """Update the current step."""
        self.current_step = step 