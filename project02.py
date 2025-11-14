import requests
import argparse
import time
from typing import List, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SubdomainEnumerator:
    def __init__(self, domain: str, threads: int = 50, timeout: int = 5):
        self.domain = domain
        self.threads = threads
        self.timeout = timeout
        self.discovered_subdomains: Set[str] = set()
        self.session = requests.Session()
        self.session.verify = False
        # Set a realistic user-agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def check_subdomain(self, subdomain: str) -> str:
        """Check if a subdomain exists"""
        url_http = f"http://{subdomain}.{self.domain}"
        url_https = f"https://{subdomain}.{self.domain}"
        
        for url in [url_https, url_http]:
            try:
                response = self.session.get(
                    url, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                if response.status_code < 400:  # Consider 2xx and 3xx as valid
                    return url
            except (requests.ConnectionError, requests.Timeout, requests.RequestException):
                continue
        
        return None

    def enumerate(self, wordlist_file: str) -> List[str]:
        """Perform subdomain enumeration"""
        try:
            with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as file:
                subdomains = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"❌ Wordlist file '{wordlist_file}' not found")
            return []
        
        print(f"🎯 Starting subdomain enumeration for: {self.domain}")
        print(f"📁 Using wordlist: {wordlist_file}")
        print(f"🔧 Threads: {self.threads}")
        print("=" * 50)
        
        start_time = time.time()
        discovered_count = 0
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit all tasks
            future_to_subdomain = {
                executor.submit(self.check_subdomain, subdomain): subdomain 
                for subdomain in subdomains
            }
            
            # Process completed tasks
            for future in as_completed(future_to_subdomain):
                subdomain = future_to_subdomain[future]
                try:
                    result = future.result()
                    if result:
                        self.discovered_subdomains.add(result)
                        discovered_count += 1
                        print(f"✅ [{discovered_count}] Discovered: {result}")
                except Exception as e:
                    print(f"❌ Error checking {subdomain}: {e}")
        
        elapsed_time = time.time() - start_time
        print(f"\n📊 Enumeration completed in {elapsed_time:.2f} seconds")
        print(f"🎉 Found {len(self.discovered_subdomains)} unique subdomains")
        
        return list(self.discovered_subdomains)

    def save_results(self, output_file: str):
        """Save discovered subdomains to file"""
        with open(output_file, 'w') as f:
            for subdomain in sorted(self.discovered_subdomains):
                f.write(subdomain + '\n')
        print(f"💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Subdomain Enumeration Tool')
    parser.add_argument('domain', help='Target domain to enumerate')
    parser.add_argument('wordlist', help='Path to subdomain wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=50, 
                       help='Number of threads (default: 50)')
    parser.add_argument('--timeout', type=int, default=5,
                       help='Request timeout in seconds (default: 5)')
    parser.add_argument('-o', '--output', default='discovered_subdomains.txt',
                       help='Output file (default: discovered_subdomains.txt)')
    
    args = parser.parse_args()
    
    enumerator = SubdomainEnumerator(args.domain, args.threads, args.timeout)
    discovered = enumerator.enumerate(args.wordlist)
    
    if discovered:
        enumerator.save_results(args.output)
    else:
        print("❌ No subdomains discovered")

if __name__ == "__main__":
    main()