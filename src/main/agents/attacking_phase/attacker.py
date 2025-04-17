from datetime import datetime
from langchain_core.tools import tool
import requests
from pydantic import BaseModel, Field
import sublist3r
from .memory import PenTestState
from prompts import enum_prompt


class Attacker:
    def __init__(self, 
                 domain,
                 attack_type
                 ):
        self.type = domain
        self.attack_type = attack_type
    
    def SQL_injection(state: PenTestState): #different agents for each?
        """
        Logic to Carry out SQL Injection attack
        """
        pass
    
    def XSS_attack(state: PenTestState):
        """
        Logic to Carry out XSS_attack
        """
        pass
    
    def CSRF_attack(state: PenTestState):
        """
        Logic to carry out XSS attack
        """
    
    def shell_shock(state: PenTestState):
        """
        Logic to carry out Shell Shock attack
        """
    
    def binary_analysis(state: PenTestState):
        pass
    
    

#local testing
if __name__ == "__main__":
    attack = Attacker()
    print(attack.SQL_injection(domain))
    
    
    