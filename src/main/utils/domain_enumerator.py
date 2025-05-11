from concurrent.futures import ThreadPoolExecutor
import dns.resolver
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubdomainMapper:
    def __init__(self, domain):
        self.domain = domain
        self.subdomains = set()
        self.resolvers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
    
    def check_subdomain(self, subdomain):
        """Check if a subdomain exists by making HTTP requests"""
        full_domain = f"{subdomain}.{self.domain}"
        
        try:
            # Try HTTP
            response = requests.get(f"http://{full_domain}", timeout=5)
            if response.status_code < 400:
                logger.info(f"Found active subdomain (HTTP): {full_domain}")
                self.subdomains.add(full_domain)
                return full_domain
        except:
            pass

        try:
            # Try HTTPS
            response = requests.get(f"https://{full_domain}", timeout=5, verify=False)
            if response.status_code < 400:
                logger.info(f"Found active subdomain (HTTPS): {full_domain}")
                self.subdomains.add(full_domain)
                return full_domain
        except:
            pass
            
        return None
    
    def check_known_acunetix_subdomains(self):
        acunetix_subdomains = [
            'testhtml5',
            'testphp',
            'testasp',
            'testaspnet',
            'rest',  
            'demo',
            'test',
            'scan'
        ]
        
        logger.info(f"Checking known Acunetix subdomains for {self.domain}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.check_subdomain, acunetix_subdomains))
        
        return [r for r in results if r]
    
    def check_common_subdomains(self):
        """Check common subdomains"""
        common_subdomains = [
            'www', 'mail', 'blog', 'api', 'dev', 'test', 'app',
            'admin', 'portal', 'stage', 'beta', 'secure', 'shop',
            'support', 'help', 'store', 'web', 'docs', 'static',
            'media', 'ftp', 'file', 'files', 'm', 'mobile'
        ]
        
        logger.info(f"Checking common subdomains for {self.domain}")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(self.check_subdomain, common_subdomains))
        
        return [r for r in results if r]

def scan_domain(domain):
    try:
        mapper = SubdomainMapper(domain)
        
        # First check known Acunetix subdomains
        mapper.check_known_acunetix_subdomains()
        
        # Then check common subdomains
        mapper.check_common_subdomains()
        
        return mapper.subdomains
        
    except Exception as e:
        logger.error(f"Exception in scanning: {e}")
        return set()

if __name__ == '__main__':
    # Target the vulnweb.com domain
    domain = "vulnweb.com"
    
    # Disable SSL warnings for HTTPS requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    discovered_domains = scan_domain(domain)
    
    print(f"\nFound {len(discovered_domains)} subdomains for {domain}:")
    for subdomain in sorted(discovered_domains):
        print(f"  {subdomain}")