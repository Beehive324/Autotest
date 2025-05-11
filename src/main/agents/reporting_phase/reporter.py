from datetime import datetime
from langchain_core.tools import tool
import requests
import nmap
from typing import Optional, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from ...agents.orchestrator.memory import PenTestState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain.tools import Tool
from .tools.reporting_tools import WriteReport


class Reporter:
    def __init__(self):
        self._tools: list = [
            WriteReport
        ]
        self.name = "reporter"
        self.prompt = "You are a pentesting report writer. You are given a list of vulnerabilities and a report template. You need to write a report based on the vulnerabilities and the report template."
    
    def get_tools(self) -> List[Tool]:
        return self._tools
    
    async def generate_report(self, state: PenTestState) -> str:
        """Generate a comprehensive pentest report based on findings"""
        report = f"""
        Penetration Testing Report
        Generated on: {datetime.now()}
        
        Target: {state.ip_port}
        
        Summary of Findings:
        {self._summarize_findings(state)}
        
        Detailed Vulnerabilities:
        {self._format_vulnerabilities(state)}
        
        Recommendations:
        {self._generate_recommendations(state)}
        """
        return report
    
    def _summarize_findings(self, state: PenTestState) -> str:
        """Summarize the key findings from the pentest"""
        total_vulns = len(state.vulnerabilities)
        critical = sum(1 for v in state.vulnerabilities if v.severity.lower() == 'critical')
        high = sum(1 for v in state.vulnerabilities if v.severity.lower() == 'high')
        medium = sum(1 for v in state.vulnerabilities if v.severity.lower() == 'medium')
        low = sum(1 for v in state.vulnerabilities if v.severity.lower() == 'low')
        
        return f"""
        Total Vulnerabilities Found: {total_vulns}
        Critical: {critical}
        High: {high}
        Medium: {medium}
        Low: {low}
        """
    
    def _format_vulnerabilities(self, state: PenTestState) -> str:
        """Format the detailed vulnerability information"""
        vuln_details = []
        for vuln in state.vulnerabilities:
            vuln_details.append(f"""
            Vulnerability: {vuln.name}
            Severity: {vuln.severity}
            CVSS Score: {vuln.cvss_score}
            Description: {vuln.description}
            Affected Components: {', '.join(vuln.affected_components)}
            """)
        return "\n".join(vuln_details)
    
    def _generate_recommendations(self, state: PenTestState) -> str:
        """Generate recommendations based on findings"""
        recommendations = []
        for vuln in state.vulnerabilities:
            if vuln.severity.lower() in ['critical', 'high']:
                recommendations.append(f"Immediate action required for {vuln.name}: {vuln.description}")
        return "\n".join(recommendations)
    
    async def _start_reporting_(self, state: PenTestState) -> PenTestState:
        """Start the reporting phase"""
        report = await self.generate_report(state)
        state.messages.append(AIMessage(content=f"Starting report generation: {report}"))
        return state
    
    async def _finalize_report_(self, state: PenTestState) -> PenTestState:
        """Finalize the report and save it"""
        final_report = await self.generate_report(state)
        state.messages.append(AIMessage(content=f"Final report generated: {final_report}"))
        return state
    
    def _create_graph_(self) -> StateGraph:
        """Create the reporting workflow graph"""
        graph = StateGraph(PenTestState)
        graph.add_node("start", self._start_reporting_)
        graph.add_node("end", END)
        return graph
    
    def add_graph_edges(self, graph):
        """Add edges to the reporting workflow graph"""
        graph.add_edge("start", "end")

if __name__ == "__main__":
    reporter = Reporter()
        
        
        







