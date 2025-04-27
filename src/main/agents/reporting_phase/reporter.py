from datetime import datetime
from langchain_core.tools import tool
import requests
import nmap
from typing import Optional
from pydantic import BaseModel, Field

prompts =

class ExtractionSchema(BaseModel):
    """Extraction Schema for scanning agent"""
    primary_domain: str
    sub_domains: Optional[list]
    
    
class ReportingAgent:
    def __init__(
        self
        ):
    async def generate_report():
        pass
        







