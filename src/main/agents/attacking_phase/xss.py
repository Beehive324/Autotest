import requests
from memory.state impport XSSState
from urlib.parse import urlparse
from palywright.sync_api import sync_playwright


class XSS:
    """
    Module for scanning web applications for XSS vulnerabilities
    Scans the pages and uses it to find and scout for XSS vulnerabilities and submits a payload
    """
    def __init__(self, domain, model):
        self.domain = domain
        self.model = model

    async def format_domain(domain):
        """
        Converts https://example.com -> "example.com"
        """
        parsed_url = urlparse(domain)
        
        netloc = parsed_url.netloc
        
        if netloc.startswith('www.'):
            netloc = netloc[4:]
            
        return netloc
    
    #update the XSS State
    async def scan_contents(state: XSSState):
        response = requests.get(response = requests.get(f'https://r.jina.ai/https://{format_domain(self.domain)}'))
        content = response.content
        
        state['url_contents'] = content
        
        return content
    
    
    
    async def generate_payloads(state: XSSSState):
        curr_payloads = state['payloads']
        
    
    async def insert_payloads(state: XSSState):
        pa

    async def find_vulnerabilities(state: XSSState):
        content = state['url_contents']
        
        prompt = f"""
        Act as a professional vulnerability assessor given the websites content
        find vulnerable sections in which XSS payload can be inserted into
        """
        
        pass
        
#local testing
if __name__ == "__main__":
    domain = "example.com"
    xss_agent = XSS(domain)
    content_results = xss_agent.scan_contents
    
    print(content_results) 
    