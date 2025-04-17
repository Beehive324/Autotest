from datetime import datetime
from langchain_core.tools import tool
import requests
import nmap
from typing import Optional
from pydantic import BaseModel, Field


class ExtractionSchema(BaseModel):
    """Extraction Schema for scanning agent"""
    primary_domain: str
    sub_domains: Optional[list]
    
    
class ScanningAgent:
    def __init__(
        self
        ):
    
    def scanner():
        nmap.scan
        
    
    async def run():
        res = scanner()
        
        return res
        
        







