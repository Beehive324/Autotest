import subprocess
import json





class XSSAgent:
    def __init__(self, model):
        self.model = model
        
 
    def _initialize_():
        
        return {
            
            "initialize": "XSS Attack Agent"
        }
        
    
    def generate_payload():
        
        res = [ ]
        xss_payload =  [
            "python3 -c 'import requests; requests.get(\"http://192.168.1.1:8000/xss\")'"   
            
        ]
         
        for payload in xss_payload:
            print(payload)
            output = subprocess.run(payload)
            res.append(output)
            
            
        
        return {
            "formatted_res": ' '.join(res)
        }
        

if __name__ == "__main__":
    test_obj2 = XSSAgent()