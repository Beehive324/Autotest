# Multi-Agent Framework for Automated Pentesting


## Disclaimer
This is a proof of concept and not to be used to carry out pentests on real world applications

## Abstract

A proof of concept multi-agent system for automated penetration testing, utilizing the ReAct paradigm to enable reasoning driven coordination and execution at each stage of the penetration test.The system employs a hierarchical architecture with specialized agents working under the supervision of an orchestrator, for the purpose of enabling security analysis and vulnerability assessment.

## System Architecture

### Core Components

1. **Orchestrator**
   - Central control unit managing agent interactions
   - State management and workflow coordination
   - Handoff management between specialized agents
   - Execution flow control

2. **Specialized Agents**
   - Reconnaissance Agent: Target scanning and information gathering
   - Planner Agent: Security vulnerability analysis
   - Attack Agent: Vulnerability exploitation
   - Reporting Agent: Security assessment documentation in pdf format


![image](https://github.com/user-attachments/assets/bdf57f28-b3a9-48c4-804f-926f73cb6708)


## Running Instructions

https://github.com/user-attachments/assets/abd7ce70-a3b2-4b5f-8595-a8eead567d2c

<img width="630" height="200" alt="IMG_9952" src="https://github.com/user-attachments/assets/2318639d-6877-421f-84be-b265430f96d9" />

### 1. Setup
```bash
git clone https://github.com/yourusername/A-Multi-Agent-Framework-for-Automated-Pentesting.git
cd A-Multi-Agent-Framework-for-Automated-Pentesting
pip install -r requirements.txt
```
### 2. Run Langgraph Studio Locally
```bash
langgraph dev
```
### Workflow Orchestration

The core logic is managed by a `StateGraph` from LangGraph. A supervisor model routes tasks between agents based on the current state of the pentest. The graph includes conditional edges to handle transitions, feedback loops (e.g., perform more reconnaissance if an attack fails), and the final reporting stage.

Below is a snippet illustrating how the workflow graph and its routing logic are defined.
```python
def create_workflow():
    """Create the main pentesting workflow graph with conditional edges and supervisor"""
    
    # Create the workflow graph
    workflow = StateGraph(PenTestState)
    
    # Create supervisor as a runnable agent
    supervisor = create_supervisor(
        model=model,
        prompt="""You are a Pentest orchestrator overseeing and managing a team of pentest experts.
        You are responsible for the overall direction of the pentest and the coordination of the team.
        You must go through the following phases for pentesting autonomously make decisions based on the current state:
        1. Planning - Create a plan for the pentest
        2. Reconnaissance - Gather information about the target
        3. Attacking - Execute attacks based on findings
        4. Reporting - Document results and findings
        
        Based on the current state, determine which phase should be executed next.
        Return only the name of the next phase: 'planning', 'recon', 'attack', or 'reporting'.""",
        state_schema=PenTestState,
        add_handoff_messages=True,
        add_handoff_back_messages=True,
        supervisor_name="orchestrator",
        include_agent_name="inline"
    )
    
    compiled_supervisor = supervisor.compile()
    
    # Define conditional functions for edge routing
    def supervisor_routing(state: PenTestState) -> str:
        """Determine which phase to execute next based on state"""
        if not state.planning_results:
            return "planning"
        if not state.open_ports and not state.services:
            return "recon"
        if not state.successful_exploits and not state.failed_exploits:
            return "attack"
        if state.successful_exploits or state.failed_exploits:
            return "reporting"
        return "planning" # Default case
    
    # Add nodes to the graph
    workflow.add_node("supervisor", compiled_supervisor)
    workflow.add_node("planning", Planner(model=model))
    workflow.add_node("recon", Recon(model=model))
    workflow.add_node("attack", Attacker(model=model))
    workflow.add_node("reporting", Reporter(model=model))
    
    # Add supervisor edges
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_routing,
        {
            "planning": "planning",
            "recon": "recon",
            "attack": "attack",
            "reporting": "reporting"
        }
    )
    
    # Add edges back to supervisor from each worker node
    workflow.add_edge("planning", "supervisor")
    workflow.add_edge("recon", "supervisor")
    workflow.add_edge("attack", "supervisor")
    
    # The reporting step is the final one before ending
    workflow.add_edge("reporting", END)
    
    return workflow.compile()

# Create and compile the workflow
graph = create_workflow()
```
---

## References

1. **ReAct: Synergizing Reasoning and Acting in Language Models**  
   Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022)  
   [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)

2. **IEEE Study on Multi-Agent Systems in Autonomous Workflows**   
   [IEEE Xplore Link](https://ieeexplore.ieee.org/document/10885158/authors#authors)

3. **OWASP Web Security Testing Guide (WSTG)**  
   [OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/)

4. **LangGraph – Graph-based Orchestration for Multi-Agent LLM Workflows**  
   [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/graph-api)

## TODO
- Different model integration
- Buffer Overlfow Attack Integration
- Further security tools integration
- Expand on the 4-tier model approach
- Web UI Interface
- API
- Deploy CLI
