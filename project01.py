import dns.resolver
import dns.exception
import argparse
import sys
from typing import List, Dict, Any

def dns_enumeration(target_domain: str, records_type: List[str] = None, nameserver: str = None) -> Dict[str, Any]:
    """
    Perform DNS enumeration for various record types
    """
    if records_type is None:
        records_type = ["A", "AAAA", "TXT", "SOA", "MX", "CNAME", "NS", "SRV"]
    
    resolver = dns.resolver.Resolver()
    
    # Set custom nameserver if provided
    if nameserver:
        resolver.nameservers = [nameserver]
    
    results = {}
    
    for record_type in records_type:
        try:
            print(f"\n🔍 Querying {record_type} records for {target_domain}...")
            answer = resolver.resolve(target_domain, record_type)
            results[record_type] = [str(data) for data in answer]
            
            print(f"{record_type} records:")
            for data in answer:
                print(f"   {data}")
                
        except dns.resolver.NoAnswer:
            print(f" No {record_type} records found")
        except dns.resolver.NXDOMAIN:
            print(f" Domain {target_domain} does not exist")
            break
        except dns.resolver.Timeout:
            print(f" Timeout while querying {record_type} records")
        except dns.exception.DNSException as e:
            print(f" DNS error for {record_type}: {e}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='DNS Enumeration Tool')
    parser.add_argument('domain', help='Target domain to enumerate')
    parser.add_argument('--types', nargs='+', default=["A", "AAAA", "TXT", "SOA", "MX", "CNAME", "NS"],
                       help='DNS record types to query')
    parser.add_argument('--nameserver', help='Custom DNS nameserver to use')
    parser.add_argument('--output', help='Output file to save results')
    
    args = parser.parse_args()
    
    print(f"**** Starting DNS enumeration for: {args.domain} ****")
    print("=" * 50)
    
    results = dns_enumeration(args.domain, args.types, args.nameserver)
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            for record_type, data in results.items():
                f.write(f"{record_type} records:\n")
                for item in data:
                    f.write(f"  {item}\n")
                f.write("\n")
        print(f"\n💾 Results saved to: {args.output}")

if __name__ == "__main__":
    main()
