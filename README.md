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

## TODO
- Different model integration
- Buffer Overlfow Attack Integration
- Further security tools integration
- Expand on the 4-tier model approach
- Web UI Interface
- API
- Deploy CLI





