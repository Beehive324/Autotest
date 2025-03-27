from datetime import datetime
from langchain_core.tools import tool
import requests
import sublist3r
import nmap
import dns.resolver


from prompts import enum_prompt


"""1.identify subdomains, IP ranges, and hosted services
   2.discover web applications, APIs, and other exposed services
   3.discover potential entry points, outdated technologies, and misconfigurations"""


class ExtractionSchema:
    primary_domain: str
    sub_domains : []

#subdomain enumerator agent
class EnumeratorAgent:
    def __init__(
        self, 
        domain
        ):
        
        self.domain = domain
    
    #enumerate subdomains using crt.sh 
    def enumerate():
        url = "crt.sh//{self.domain}"
        response = requests.get(url)
        
        return response
    
    #enumerate subdomains using dns python
    def dns_enumeration():
        dns.resolver.Resolve()
    
    def nmap():
        nm = nmap.PortScanner()
        scanner_res = nm.scan(f'{port}')
        hosts = nm.all_hosts()
        
        json_output = {
            
            "scan results": scanner_res,
            "hosts": hosts
        }
        
        return json_output
    
    
    def api_discovery():
        pass
    
    def get_wayback_urls():
        #get wayback urls
        pass
    

    def what_web():
        pass
    
    def hidden_dirs():
        pass
    
    
    def google_dorks():
        pass
    
    def github_dorks():
        pass
    
    
    def shodan_dorks():
        pass
    
    async def _run(self):
        crtsh_domains = enumerate(self.domain)
        dns_enumeration = dns_enumeration(self.domain)
        api_discovery = apid_discovery(self.domain)
        
        results = {
            
            "crtsh_domains": crtsh_domains,
            "dns_domains": dns_enumeration,
            "api_discover": api_discovery
            
        }
        
        return results

 
        
  