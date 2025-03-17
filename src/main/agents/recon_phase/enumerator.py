from datetime import datetime
from langchain_core.tools import tool
import requests
import sublist3r

from prompts import enum_prompt


class ExtractionSchema:
    primary_domain: str
    sub_domains : []


#subdomain enumerator agent
class EnumeratorAgent:
    def __init__(self, domain):
        self.domain = domain
    
    
    def enumerate():
        url = "crt.sh//{self.domain}"
        response = requests.get(url)
        
        return response
        