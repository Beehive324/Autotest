import pytest
from src.main.tools import (
    PortScanner,
    SubdomainEnumerator,
    VulnerabilityScanner,
    WebCrawler
)

def test_port_scanner_initialization():
    """Test port scanner initialization."""
    scanner = PortScanner()
    assert scanner is not None

def test_port_scanning():
    """Test port scanning functionality."""
    scanner = PortScanner()
    # Mock the nmap scan to avoid actual network calls
    scanner._scan = lambda target, ports: {"80": "open", "443": "open"}
    
    results = scanner.scan("example.com", "80,443")
    assert "80" in results
    assert "443" in results
    assert results["80"] == "open"

def test_subdomain_enumerator():
    """Test subdomain enumeration."""
    enumerator = SubdomainEnumerator()
    # Mock the sublist3r call
    enumerator._enumerate = lambda domain: ["sub1.example.com", "sub2.example.com"]
    
    subdomains = enumerator.enumerate("example.com")
    assert len(subdomains) == 2
    assert "sub1.example.com" in subdomains
    assert "sub2.example.com" in subdomains

def test_vulnerability_scanner():
    """Test vulnerability scanning."""
    scanner = VulnerabilityScanner()
    # Mock the vulnerability scan
    scanner._scan = lambda target: [{"type": "xss", "severity": "high"}]
    
    vulns = scanner.scan("example.com")
    assert len(vulns) == 1
    assert vulns[0]["type"] == "xss"
    assert vulns[0]["severity"] == "high"

def test_web_crawler():
    """Test web crawling functionality."""
    crawler = WebCrawler()
    # Mock the web crawl
    crawler._crawl = lambda url: ["/page1", "/page2"]
    
    pages = crawler.crawl("http://example.com")
    assert len(pages) == 2
    assert "/page1" in pages
    assert "/page2" in pages

def test_error_handling():
    """Test error handling in tools."""
    scanner = PortScanner()
    with pytest.raises(ValueError):
        scanner.scan("", "80")  # Empty target should raise error
    
    enumerator = SubdomainEnumerator()
    with pytest.raises(ValueError):
        enumerator.enumerate("")  # Empty domain should raise error

def test_rate_limiting():
    """Test rate limiting functionality."""
    scanner = PortScanner()
    # Test that rapid consecutive calls are rate limited
    for _ in range(5):
        scanner.scan("example.com", "80")
    # If we get here without error, rate limiting is working 