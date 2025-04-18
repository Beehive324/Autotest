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
from urlib.parse import urlparse
from playwright.sync_api import sync_playwright
import requests




class URL(BaseModel):
    url: str = Field(description="url input")


class SQL_Injection(BaseTool):
    name = "sql injection tool"
    description = "tool to carry out sql injection"
    args_schema: Type[BaseModel] = URL
    
    
    def _run(self, url: str) -> str:
        pass
    
    async def_run(self, url: str) -> str:
        pass


class XSS(BaseTool):
    name = "XSS tool"
    description = "tool to carry out xss attack"
    args_schema: Type[BaseModel] = URL
    
    async def format_url(self, url: str) -> str:
        
        parsed_url = urlparse(domain)
        
        netloc = parsed_url.netloc
        
        if netloc.startswith('wwww.'):
            netloc = netloc[4:]
        
        return netloc
    
    
    async def scan_contents(self, url: str) -> str:
        url = format_url(url)
        response = requests.get(f'https://r.jina.ai/https://{format_domain(self.domain)}')
        content = response.content
        
        return content
    
    async def generate_payloads(self, url: str) -> str:
        return f"Generating payloads for {url}...."
    
    async def insert_payloads(self, url: str) -> str:
        return f"Inserting payloads for {url}...."
    
    async def find_vulnerabilities(self, url: str) -> str:
        
        return f"Finding vulnerabilities for {url}...."
    
    def _run(self, url: str) -> str:
        pass
    
    async def_run(self, url: str) -> str:
        pass

class ShellShock(BaseTool):
    name = "Shellshock"
    description = "Tool to carry out shellshock attack"
    args_schema: Type[BaseModel] = URL
    
    def _run(self, url: str) -> str:
        pass
    
    async def_run(self, url: str) -> str:
        pass

class BinaryAnalysis(BaseTool):
    name = "Binary Analysis"
    description = "Tool to Carry out binary analysis"
    args_schema: Type[BaseModel] = URL
    
    def _run(self, url: str) -> str:
        return f"Running binary analysis for {url}..."
    
    async def_run(self, url: str) -> str:
        return f"Running binary analysis for {url}..."
    
