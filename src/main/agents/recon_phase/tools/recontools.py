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
import logging
import mylib
import sublist3r
import nmap

logger = logging.getLogger(__name__)

tavily_client = TavilyClient(api_key=api_key)

#Defining tools using a subclass BaseTool Approach
#Nmap Input takes the ip address
class NmapInput(BaseModel):
    ip_address: str = Field(description="Target's IP address")
    scan_options: str = Field(description="Scan options to be used for nmap")
    

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
        logging.info(f"Running web search on the following {dorks}....")
        output = []
        for dork in dorks:
            response = tavily_client.search(dork)
            content = response.content
            output.append(content)
        
        for res in output:
            logging.info("Search details found are the following: {res}")
        
        return output
        
    async def _run(self, dorks: List[str]) -> str:
        logging.info(f"Running web search asynchronously on the following {dorks}....")
        output = []
        for dork in dorks:
            response = tavily_client.search(dork)
            content = response.content
            output.append(content)
        
        for res in output:
            logging.info("Search details found are the following: {res}")
        
        return output

#tool to use nmap
class Nmap(BaseTool):
    name = "nmap"
    description = "uses nmap to discover the target's IP address based on a network segment"
    args_schema: Type[BaseModel] = NmapInput
    
 
    
    def _run(self, ip_address: str) -> str:
        nm = nmap.PortCanner()
        
        nm.scan()
     
    
class Resolve(BaseTool):
    name = "resolver"
    description = "resolves domains"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        return f"Resolving {domain_name}...."
    
    async def _arun(self, domain_name: str) -> str:
        return f"Resolving {domain_name}...."

class Subdomain_Enum_CRT(BaseTool):
    name = "domain_enumerator_crt"
    description = "domain enumeration tool to find all subdomains give a domain using crt"
    args_schema: Type[BaseModel] = DomainInput
    
    
    def _run(self, domain_name: str) -> str:
        subdomains = set()
        
        logging.info(f"Finding and enumerating subdomains for {domain_name}")
        
        try:
            response = requests.get(f"https://crt.sh/?q=%.{url}&output=json")
            if response.status_code == 200:
                json_data = response.json()
                if json_data:
                    for entry in json_data:
                        subdomain = entr["name_value"].lower()
                        if not subdomain.startswith("www.") and not subdomain.starswith("*.") and subdomain.endswith(f".{url}"):
                            subdomains.add(subdomain)
                            logging.info(f"Successfully discovered {subdomain}")
        except Exception as e:
            logging.info("Error in enumeration using CRT")
                            
                
class Subdomain_Enum_gobuster(BaseTool):
    name = "domain_enumerator_gobuster"
    description = "domain enumeration tool using gobuster"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        gobuster_command = f"gobuster dns -d {domain_name}"
        pass


class Subdomain_Enum_findomain(BaseTool):
    name = "domain_enumerator_findomain"
    description = "domain enumeration tool using findomain"
    args_schema: Type[BaseModel] = DomainInput
    
    
    def _run(self, domain_name: str) -> str:
        logging.info(f"Running subdomain enmueration on {domain_name}...")
        pass
    
    async def _arun(self, domain_name: str) -> str:
        pass


class Subdomain_Enum_amass(BaseTool):
    nmae = "domain_enumerator_amass"
    description = "domain enumeration tool using amass"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        pass
    
    async def _arun(self, domain_name: str) -> str:
        pass


class Subdomain_Enum_wayback(BaseTool):
    name = "domain_enumerator_wayback"
    description = "domain enumeration tool using wayback urls"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        pass
    
    async def _arun(self, domain_name: str) -> str:
        pass
    
   
class Subdomain_Enum_sublist3r(BaseTool):
    name = "domain_enumerator_3listr"
    description = "domain enumeration using sublist3r"
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        subdomains = set()
        logging.info(f"Enumerating domain: {domain_name} using sublist3r")
        subdomains = sublist3r.main(f'{domain_name}')
        
        return subdomains
    
    async def _arun(self, domain_name: str) -> List[str]:
        subdomains = set()
        logging.info(f"Enumerating domain: {domain_name} asynchronously using sublist3r")
        subdomains = sublist3r.main(f'{domain_name}')
        
        return subdomains

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


