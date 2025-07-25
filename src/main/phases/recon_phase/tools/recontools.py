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
from typing import Optional, Type, List, Dict
from tavily import TavilyClient
import logging
import os
import masscan
from dotenv import load_dotenv
import conf
import subprocess

load_dotenv()

logger = logging.getLogger(__name__)

#Tools for Reconnaisance Phase, in order ot perform a full scan of the target and identify all open ports and services
tavily_api_key = os.getenv('TAVILY_API_KEY')
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable is not set. Please set it to your Tavily API key.")
tavily_client = TavilyClient(api_key=tavily_api_key)

#Nmap Input takes the ip address
class NmapInput(BaseModel):
    ip_address: str = Field(..., description="The IP address or hostname to scan")
    scan_options: str = Field(default="-sV -sC -O -p-", description="Nmap scan options")

    class Config:
        json_schema_extra = {
            "example": {
                "ip_address": "192.168.1.1",
                "scan_options": "-sV -sC -O -p-"
            }
        }

#Resolver Input takes the domain name
class DomainInput(BaseModel):
    domain_name: str = Field(description="Target's Domain")


class DorksInput(BaseModel):
    dorks: List[str] = Field(description="Dorks to carry out web search")
    

#carrying out web search using tavily
class WebSearch(BaseTool):
    name: str = Field(default="web search", description="web search")
    description: str = Field(default="web search", description="web search")
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
        
    async def _arun(self, dorks: List[str]) -> str:
        logging.info(f"Running web search asynchronously on the following {dorks}....")
        output = []
        for dork in dorks:
            response = tavily_client.search(dork)
            content = response.content
            output.append(content)
        
        for res in output:
            logging.info("Search details found are the following: {res}")
        
        return output


#subprocess tools
class UrlInput(BaseModel):
    url: str = Field("Input for curl")

class Curl(BaseTool):
    name: str = Field(default="curl command", description="curl")
    description: str = Field(default="curl", description="send curl to url")
    args_schema: Type[BaseModel] = UrlInput
    
    
    def _run(self, url: str) -> str:
        out = subprocess.check_output(["curl", "-X", "POST", "-u", "opt:gggguywqydfydwfh"], url)
        subprocess.run(out)
        
    
    async def _arun(self, url: str) -> str:
        command = ["curl", url]
        out = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        output = out.stdout
        
        return {
            
            "result": output
        }
                                      

class Wget(BaseTool):
    name: str = Field(default="wedget command", description="wedget")
    description: str = Field(default="wedget", description="wedget command to focus on file downloading")
    arg_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def _run(self, url: str) -> str:
        pass

class Tcpdump(BaseTool):
    name: str = Field(default="tcpdump command", description="tcpdump")
    description: str = Field(default="tcpdump", description="tcpdump command")
    args_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def a_run(self, url: str) -> str:
        pass

class Whois(BaseTool):
    name: str = Field(default="whois command", description="whois")
    description: str = Field(default="whois", description="whois command")
    args_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def a_run(self, url: str) -> str:
        pass

class Dmitry(BaseTool):
    name: str = Field(default="dmitry command", description="dmitry")
    description: str = Field(default="dmitry", description="dmitir command")
    args_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def a_run(self, url: str) -> str:
        pass

class Dnsenum(BaseTool):
    name: str = Field(default="dnsenum", description="dnsenum")
    description: str = Field(default="dnsenum", description="dnseunm command")
    args_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def _arun(self, url: str) -> str:
        pass

class Netdiscover(BaseTool):
    name: str = Field(default="Netdiscover", description="netdiscover")
    description: str = Field(default="netdiscover", description="netdiscover command")
    args_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def _arun(self, url: str) -> str:
        pass
    
    

class Amap(BaseTool):
    name: str = Field(default="Amap", description="amap")
    description: str = Field(default="amap", description="amap command")
    args_schema: Type[BaseModel] = UrlInput
    
    def _run(self, url: str) -> str:
        pass
    
    async def _arun(self, url: str) -> str:
        pass

class Enum4linux(BaseTool):
    name: str = Field(default="Enum4Linux", description="Enum4Linux")
    description: str = Field(default="enum4linux", description="enum4linux command")

class Smbclient(BaseTool):
    pass

class SSLscan(BaseTool):
    pass

class Amass(BaseTool):
    pass

class SSLscan(BaseTool):
    pass

class SpiderFoot(BaseTool):
    pass

class Fierce(BaseTool):
    pass



class Niktoscan(BaseTool):
    name: str = Field(default="niktoscan", description="uses niktoscan to scan the ports")
    description: str = Field(default="uses niktoscan to scan the ports")
    args_schema: Type[BaseModel] = NmapInput
    
    def _run(self, ip_address: str) -> str:
        pass 
        
class Masscan(BaseTool):
    name: str = Field(default="masscan", description="uses masscan to scan the ports")
    description: str = Field(default="uses masscan to scan the ports")
    args_schema: Type[BaseModel] = NmapInput
    
    def _run(self, ip_address: str) -> str:
        mas = masscan.PortScanner().masscan(ip_address, ports, arguments='--max-rate 1000')
        print(mas.scan_result)
        return mas.scan_result 
    
    async def _arun(self, ip_address: str) -> str:
        return await self._run(ip_address)


#tool to use nmap
class Nmap(BaseTool):
    name: str = Field(default="nmap", description="uses nmap to deliver a security scan")
    description: str = Field(default="uses nmap to discover the target's IP address based on a network segment")
    args_schema: Type[BaseModel] = NmapInput
    
    def _run(self, ip_address: str) -> str:
        try:
            nm = nmap.PortScanner()
            nm.scan(ip_address,'8020, 8022, 8025, 8050, 8443, 9306',arguments='-sV')
            results = []
            for host in nm.all_hosts():
                results.append(f"Host: {host}")
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        state = nm[host][proto][port]['state']
                        service = nm[host][proto][port]['name']
                        results.append(f"Port: {port}/{proto}\tState: {state}\tService: {service}")
            return "\n".join(results)
        except Exception as e:
            logging.error(f"Error during Nmap scan: {str(e)}")
            return f"Nmap scan failed: {str(e)}"
    
    async def _arun(self, ip_address: str) -> str:
        results = []
        try:
            nm = nmap.PortScanner()
            nm.scan(ip_address)
            for host in nm.all_hosts():
                results.append(f"Host: {host}")
            
            return ''.join(results)
        except Exception as e:
            logging.error(f"An error has occured")
        
                  
class Resolve(BaseTool):
    name: str = Field(default="resolver", description="resolves domains")
    description: str = Field(default="resolves domains")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        return f"Resolving {domain_name}...."
    
    async def _arun(self, domain_name: str) -> str:
        return f"Resolving {domain_name}...."

class Subdomain_Enum_CRT(BaseTool):
    name: str = Field(default="domain_enumerator_crt", description="domain enumeration tool to find all subdomains give a domain using crt")
    description: str = Field(default="domain enumeration tool to find all subdomains give a domain using crt")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        subdomains = set()
        
        logging.info(f"Finding and enumerating subdomains for {domain_name}")
        
        try:
            response = requests.get(f"https://crt.sh/?q=%.{domain_name}&output=json")
            if response.status_code == 200:
                json_data = response.json()
                if json_data:
                    for entry in json_data:
                        subdomain = entry["name_value"].lower()
                        if not subdomain.startswith("www.") and not subdomain.startswith("*.") and subdomain.endswith(f".{domain_name}"):
                            subdomains.add(subdomain)
                            logging.info(f"Successfully discovered {subdomain}")
            return list(subdomains)
        except Exception as e:
            logging.error(f"Error in enumeration using CRT: {str(e)}")
            return []

class Subdomain_Enum_gobuster(BaseTool):
    name: str = Field(default="domain_enumerator_gobuster", description="domain enumeration tool using gobuster")
    description: str = Field(default="domain enumeration tool using gobuster")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        gobuster_command = f"gobuster dns -d {domain_name}"
        return f"Running gobuster on {domain_name}..."


class Subdomain_Enum_findomain(BaseTool):
    name: str = Field(default="domain_enumerator_findomain", description="domain enumeration tool using findomain")
    description: str = Field(default="domain enumeration tool using findomain")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        logging.info(f"Running subdomain enumeration on {domain_name}...")
        return f"Running findomain on {domain_name}..."
    
    async def _arun(self, domain_name: str) -> str:
        return await self._run(domain_name)


class Subdomain_Enum_amass(BaseTool):
    name: str = Field(default="domain_enumerator_amass", description="domain enumeration tool using amass")
    description: str = Field(default="domain enumeration tool using amass")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        return f"Running amass on {domain_name}..."
    
    async def _arun(self, domain_name: str) -> str:
        return await self._run(domain_name)


class Subdomain_Enum_wayback(BaseTool):
    name: str = Field(default="domain_enumerator_wayback", description="domain enumeration tool using wayback urls")
    description: str = Field(default="domain enumeration tool using wayback urls")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> str:
        return f"Running wayback search on {domain_name}..."
    
    async def _arun(self, domain_name: str) -> str:
        return await self._run(domain_name)
    
   
class Subdomain_Enum_sublist3r(BaseTool):
    name: str = Field(default="domain_enumerator_3listr", description="domain enumeration using sublist3r")
    description: str = Field(default="domain enumeration using sublist3r")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        subdomains = set()
        logging.info(f"Enumerating domain: {domain_name} using sublist3r")
        subdomains = sublist3r.main(f'{domain_name}')
        return list(subdomains)
    
    async def _arun(self, domain_name: str) -> List[str]:
        return await self._run(domain_name)

class GoogleDorks(BaseTool):
    name: str = Field(default="google dorks", description="forms google dorks in order to find out specific information")
    description: str = Field(default="forms google dorks in order to find out specific information")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        dorks = [
            f"site:{domain_name}",
            f"site:{domain_name} inurl:admin",
            f"site:{domain_name} inurl:login",
            f"site:{domain_name} filetype:pdf",
            f"site:{domain_name} intitle:\"index of\"",
            f"site:{domain_name} intext:password",
            f"site:{domain_name} inurl:wp-content",
            f"site:{domain_name} inurl:wp-admin",
        ]
        return dorks
    
    async def _arun(self, domain_name: str) -> List[str]:
        return await self._run(domain_name)


class GitHubDorks(BaseTool):
    name: str = Field(default="Github dorks", description="forms github dorks in order to find out repo information, codebases")
    description: str = Field(default="forms github dorks in order to find out repo information, codebases")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        github_dorks = [
            f'"{domain_name}" password',
            f'"{domain_name}" secret',
            f'"{domain_name}" api_key',
            f'"{domain_name}" apikey',
            f'"{domain_name}" token',
            f'"{domain_name}" config',
            f'"{domain_name}" credentials',
            f'org:{domain_name}',
        ]
        return github_dorks
    
    async def _arun(self, domain_name: str) -> List[str]:
        return await self._run(domain_name)


class ShodanDorks(BaseTool):
    name: str = Field(default="Shodan Dorks", description="forms shodan dorks given a domain input")
    description: str = Field(default="forms shodan dorks given a domain input")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        shodan_dorks = [
            f'hostname:"{domain_name}"',
            f'ssl:"{domain_name}"',
            f'org:"{domain_name}"',
            f'http.title:"{domain_name}"',
            f'net:"{domain_name}"',
        ]
        return shodan_dorks
    
    async def _arun(self, domain_name: str) -> List[str]:
        return await self._run(domain_name)


class APIDiscovery(BaseTool):
    name: str = Field(default="API Discovery", description="tools to discover apis given a domain as input")
    description: str = Field(default="tools to discover apis given a domain as input")
    args_schema: Type[BaseModel] = DomainInput
    
    def _run(self, domain_name: str) -> List[str]:
        return [f"Discovering APIs for {domain_name}..."]
    
    async def _arun(self, domain_name: str) -> List[str]:
        return await self._run(domain_name)


