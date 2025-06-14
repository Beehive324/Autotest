from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import sublist3r
import nmap


class EnumerationInput(BaseModel):
    domain: str = Field(description="Domain to be Enumerated")
    no_threads: int = Field(description="Number of threads")
    save_file: str = Field(description="save the output into text file")
    ports: str = Field(descripion="specify a comma-separated list of the tcp ports to scan")
    silent: str = Field(description="set sublist3r to work in silent mode during execution")
    verbose: str = Field(description="display the found subdomains in real time")
    enable_bruteforce: bool = Field(description="display the found subdomains in real time.")


class NmapInput(BaseModel):
    Ip_port: str = Field(description="IP Port to be scanned")


class DomainEnumerationTool(BaseModel):
    name: str = "DomainEnumerationTool"
    description: str = (
        
        """
        Enumerate the give domain
        and list all of the subdomains
        """
    )
    
    args_schema: Type[BaseModel] = EnumerationInput
    
    def _run(self, domain):
        subdomains = sublist3r.main(domain, no_threads, savefile, ports, silent, verbose, enable_bruteforce, engines)
        return subdomains 

class Nmap(BaseModel):
    name: str = "NmapTool"
    description: str = (
        
        """
        Discover open ports using
        nmap
        """       
    )
    
    args_schema: Type[BaseModel] = NmapInput
    
    def _run(self, ip_port):
        nm = nmap.PortScanner()
        scanner_res = nm.scan(f"{port}")
        hosts = nm.all_hosts()
        
        json_output = {
            
            "scan results": scanner_res,
            "hosts": hosts
        }
        
        return json_output
        
    
        
        
        


