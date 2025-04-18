from langchain.agents import tool
from typing import list
from datetime import datetime
from langchain_core.tools import tool
import requests
import sublist3r
import nmap
import dns.resolver
from memory.state import ReconState
from langchain_ollama import ChatOllama
from prompts import enum_prompt
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from tavily import TavilyClient



tavily_client = TavilyClient(api_key=api_key)


#Defining tools using a subclass BaseTool Approach

#Nmap Input takes the ip address
class NmapInput(BaseModel):
    ip_address: str = Field(description="Target's IP address")

#Resolver Input takes the domain name
class DomainInput(BaseModel):
    domain_name: str = Field(description="Target's Domain")


class DorksInput(BaseModel):
    dorks: List[str] = Field(description="Dorks to carry out web search")
    
    
#carrying out web search using tavily
class WebSearch(BaseTool):
    name = "web search"
    description ="web search"
    args_schema: Type[BaseModel] = DorksInput
    
    def _run(self, dorks: List[str]) -> str:
        
        return f"Running web search on the following {dorks}...."
    
    async def _run(self, dorls: List[str]) -> str:
    
        return f"Running web search on the following {dorks}..."

#tool to use nmap
class Nmap(BaseTool):
    name = "nmap"
    description = "uses nmap to discover ip ports"
    args_schema: Type[BaseModel] = NmapInput
    
    def _run(self, ip_address: str) -> str:
        print(f"{ip_address = }")
        return f"Scanning {ip_address}..."
    
    async def _run(
        self, ip_address: str
    ) -> str:
        return "Running Tool asynchronously"
    
class Resolve(BaseTool):
    name = "resolver"
    description = "resolves domains"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        return f"Resolving {domain_name.....}"
    
    async def_run(self, domain_name: str) -> str: #run the tool asynchronously
        return f"Resolving {domain_name}...."

class Enumerator(BaseTool):
    name = "domain_enumerator"
    description = "enumerates domain names"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        domains = []
        
        return f"Enumerating domains for {domain_name}....."
    
    async def_run(self, domain_name: str) -> str:
        return f"Enumerating {domain_name}...."


class GoogleDorks(BaseTool):
    name = "google dorks"
    description = "forms google dorks in order to find out specific information"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        dorks = [
            
        ]
        
        return f"Forming google dorks for {domain_name}"
    
    async def_run(self, domain_name: str) -> str:
        return f"Forming google dorks for {domain_name}"



class GitHubDorks(BaseTool):
    name = "Github dorks"
    description = "forms github dorks in order to find out repo information, codebases"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        github_dorks = [
            
        ]
        
        return f"Forming Github dorks for {domain_name}..."
    
    async def_run(self, domain_name: str) -> str:
        return f"Forming Github dorks for {domain_name}..."


class ShodanDorks(BaseTool):
    name = "Shodan Dorks"
    description = "forms shodan dorks given a domain input"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        shodan_dorks = [
            
        ]
        
        return f"Forming shodan dorks for {domain_name}..."
    
    async def_run(self, domain_name: str) -> str:
        
        return f"Formind shodan dorks for {domain_nmae}"


class APIDiscovery(BaseTool):
    name = "API Discovery"
    description = "tools to discover apis given a domain as input"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        
        return f"Discovering apis for {domain_name}"
    
    async def_run(self, domain_name: str) -> List[str]:
        
        return f"Discovering apis for {domain_name}"


