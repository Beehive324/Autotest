import pytest
from src.main.state import PentestState, PentestStage

def test_state_initialization():
    """Test that state can be initialized with a target."""
    state = PentestState(target="example.com")
    assert state.target == "example.com"
    assert state.current_stage == PentestStage.INITIALIZATION
    assert state.findings == []
    assert state.vulnerabilities == []

def test_state_stage_transition():
    """Test state transitions between different stages."""
    state = PentestState(target="example.com")
    
    # Test valid transitions
    state.current_stage = PentestStage.RECONNAISSANCE
    assert state.current_stage == PentestStage.RECONNAISSANCE
    
    state.current_stage = PentestStage.VULNERABILITY_SCAN
    assert state.current_stage == PentestStage.VULNERABILITY_SCAN

def test_state_findings_management():
    """Test adding and managing findings."""
    state = PentestState(target="example.com")
    
    # Add a finding
    finding = {"type": "port", "details": "Port 80 open"}
    state.add_finding(finding)
    assert len(state.findings) == 1
    assert state.findings[0] == finding

def test_state_vulnerability_management():
    """Test adding and managing vulnerabilities."""
    state = PentestState(target="example.com")
    
    # Add a vulnerability
    vuln = {"type": "xss", "severity": "high", "details": "Reflected XSS found"}
    state.add_vulnerability(vuln)
    assert len(state.vulnerabilities) == 1
    assert state.vulnerabilities[0] == vuln

def test_state_validation():
    """Test state validation."""
    with pytest.raises(ValueError):
        PentestState(target="")  # Empty target should raise error

def test_state_serialization():
    """Test state serialization and deserialization."""
    state = PentestState(target="example.com")
    state.add_finding({"type": "port", "details": "Port 80 open"})
    
    # Convert to dict
    state_dict = state.dict()
    assert state_dict["target"] == "example.com"
    assert len(state_dict["findings"]) == 1
    
    # Create new state from dict
    new_state = PentestState(**state_dict)
    assert new_state.target == state.target
    assert len(new_state.findings) == len(state.findings) 