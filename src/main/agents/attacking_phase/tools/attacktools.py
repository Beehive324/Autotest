from langchain.agents import tool
from datetime import datetime
from langchain_core.tools import tool
import requests
import sublist3r
import nmap
import dns.resolver
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from tavily import TavilyClient
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import requests
import subprocess
import logging
logger = logging.getLogger(__name__)


class IP(BaseModel):
    ip: str = Field(description="IP of the target")

class URL(BaseModel):
    url: str = Field(description="url input")

class Path(BaseModel):
    path: str = Field(description="path to binary")
    

class SQL_Injection(BaseTool):
    name: str = Field(default="Sql Injection")
    description: str = "tool to carry out sql injection"
    args_schema: Type[BaseModel] = URL
    
    def get_sql_commands(target: str, command_index:int):
        sqlmap_commands = [f"sqlmap -u {target} --batch --banner",
                           f"sqlmap -u {target} --batch --passwords",
                           f"sqlmap -u {target} --batch --dbs",
                           f"sqlmap -u {target} --batch --tables -D database",
                           f"sqlmap -u {target} --batch --dump -T table -D database"
                           ]
    
        return sqlmap_commands[command_index]
    
    def _run_find_dbs(target:str):
        
        command = ""
        
        shell_output = subprocess.run(command)
        
        return {
            
            "output": shell_output
        }
    
    def _dbs_output(shell_output: str):
        pass
    
    def _dbs_findtables(target: str, db_name: str):
        command = get_sql_commands(target, 3)
        
        shell_ouput = subprocess.command()
        
        return {
            
            "output": shell_ouput
        }
    
    def _run_table_dump(target: str, table_name: str, db_name: str):
        pass
    
    
    def _run(self, url: str) -> str:
        pass
    
    async def _arun(self, url: str) -> str:
        pass

class XSS(BaseTool):
    name: str = Field(default="XSS_Tool")
    description: str= "tool to carry out xss attack"
    args_schema: Type[BaseModel] = URL
    
    async def format_url(self, url: str) -> str:
        parsed_url = urlparse(url)
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
    
    async def _arun(self, url: str) -> str:
        pass

class ShellShock(BaseTool):
    name: str =  Field(default="Shellshock")
    description: str = "Tool to carry out shellshock attack"
    args_schema: Type[BaseModel] = URL
    
    def _run(self, url: str) -> str:
        pass
    
    async def a_run(self, url: str) -> str:
        pass

class BinaryAnalysis(BaseTool):
    name: str = Field(default="Binary Analysis")
    description: str = "Tool to Carry out binary analysis"
    args_schema: Type[BaseModel] = URL
    
    def _run(self, url: str) -> str:
        return f"Running binary analysis for {url}..."
    
    async def a_run(self, url: str) -> str:
        return f"Running binary analysis for {url}..."


class BufferOverflowVulnerabilities(BaseTool):
    name: str = Field(default="Buffer Overflow")
    description: str = Field(description= """
    Tool to perform Buffer overflow attack, context:
    Buffer overflow vulnerabilities occur when a program
    writes more data into a buffer than it can hold,
    potentially allowing attackers to execute arbitrary code
    """) 
    args_schema: Type[BaseModel] 
     
    def _run(self, path_to_binary: str) -> str:
        static_analysis = ""
        dynamic_analysis = ""
    


 
        
        
    