import subprocess
import json




class SQL_Injector:
    def __init__(self, url):
        self.url = url
    
    def commands(self):
        commands = {
            
           "DB": "python3 sqlmap.py -d",
           "Target URL": f"python sqlmap.py -u {self.url} -f --banner --dbs -\
-users"
            
              
        }
        
        return commands
    
    
    def execute_command(command):
        
        res = subprocess.run(command)
        
        return {
            
            "res": res
        }





#local testing
if __name__ == "__main__":
    injector = SQL_Injector()
    
    print(injector.commands)
            
            
            
        
        
