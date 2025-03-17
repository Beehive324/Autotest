from datetime import datetime
from langchain_core.tools import tool
import requests
import sublist3r

from prompts import enum_prompt


class ExtractionSchema:
    primary_domain: str
    sub_domains : []


#subdomain enumerator agent
class PlannerAgent:
    def __init__(
        self, 
        domain
        ):
        
        self.domain = domain
    
    
    def create_plan():
        prompt="""
        
        You are an experienced Pentester your task is to create a Plan of Attack give the give vulnerabilties
        
        """
        
        
        