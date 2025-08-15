# Multi-Agent Framework for Automated Pentesting

<p align="center">
<img alt="Framework in Action" src="https://github.com/user-attachments/assets/2318639d-6877-421f-84be-b265430f96d9" width="700">
</p>

A proof-of-concept multi-agent system for automated penetration testing. This framework utilizes the ReAct paradigm to enable reasoning-driven coordination and execution at each stage of a penetration test. It employs a hierarchical architecture with specialized agents working under the supervision of a central orchestrator to perform security analysis and vulnerability assessments.

---

### Disclaimer

This project is a **proof of concept** intended for educational and research purposes only. It is **not** to be used for conducting penetration tests on real-world applications or any systems you do not have explicit, written permission to test. The authors are not responsible for any misuse or damage caused by this software.

---

### Key Features

* **Hierarchical Agent Architecture:** A central orchestrator manages a team of specialized agents for a clear division of tasks.
* **Autonomous Operation:** Agents can reason and make decisions to progress through the pentesting lifecycle from reconnaissance to reporting.
* **Stateful Workflow:** The system maintains a comprehensive state, allowing for intelligent transitions and conditional logic between phases.
* **Modular Design:** Easily extendable to include new agents, tools, and attack vectors.
* **Powered by LangGraph:** Built on a reliable framework for creating stateful, multi-agent applications.

---

### System Architecture

The framework is composed of a central **Orchestrator** and several **Specialized Agents**, each with a distinct role in the penetration testing process.

![System Architecture Diagram](https://github.com/user-attachments/assets/bdf57f28-b3a9-48c4-804f-926f73cb6708)

#### Core Components

1.  **Orchestrator Agent:**
    * The central control unit that manages the entire workflow.
    * Coordinates interactions and handoffs between specialized agents.
    * Maintains the overall state of the penetration test.
    * Controls the execution flow based on the results from other agents.

2.  **Specialized Agents:**
    * **Reconnaissance Agent:** Gathers initial information about the target, performing scans for open ports, services, and potential entry points.
    * **Planner Agent:** Analyzes reconnaissance data to identify potential vulnerabilities and formulates a strategic plan of attack.
    * **Attack Agent:** Executes attacks based on the plan, attempting to exploit identified vulnerabilities.
    * **Reporting Agent:** Documents all findings, including successful and failed exploits, to generate a comprehensive security assessment report.

---

### Getting Started

Follow these steps to set up and run the framework locally.

#### Prerequisites
* Python 3.8+
* Git

#### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/A-Multi-Agent-Framework-for-Automated-Pentesting.git](https://github.com/yourusername/A-Multi-Agent-Framework-for-Automated-Pentesting.git)
cd A-Multi-Agent-Framework-for-Automated-Pentesting
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run LangGraph Studio
This allows you to visualize and debug the agent interactions in real-time.
```bash
langgraph dev
```
You can access the studio at [http://localhost:1984](http://localhost:1984).

---

### Usage

To start the penetration testing workflow, run the main application script and provide a target.
```bash
# Example of how to run the framework (update with your actual run command)
python main.py --target example.com
```

---

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

### Roadmap

This project is actively evolving. Future plans include:

- [ ] Integration with additional language models (e.g., local models).
- [ ] Implementation of more complex attack vectors, such as Buffer Overflows.
- [ ] Integration with more industry-standard security tools (Metasploit, Nmap scripts).
- [ ] Expansion of the current 4-agent model to handle more specialized tasks.
- [ ] Development of a user-friendly Web UI and API.
- [ ] Creation of a deployable Command-Line Interface (CLI).

---

### Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---
