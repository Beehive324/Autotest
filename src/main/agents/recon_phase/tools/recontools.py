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



@tool
def resolver(domain: str):
    res = dns.resolver.resolve(domain)
    return res

@tool
def domain_enumeration(domain: str):
    pass

@tool
def google_dorks():
    pass

@tool
def github_dorks():
    pass

@tool
def shodan_dorks():
    pass


@tool
def nmap(ip: str):
    nm = nmap.PortScanner()
    scanner_res = nm.scan(f'{port}')
    hosts = nm.all_hosts()
    
    output = {
        "scan results": scanner_res,
        "hosts": hosts
        
        
    }
    
    return output
    