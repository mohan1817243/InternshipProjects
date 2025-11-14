import socket
import concurrent.futures
import sys

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def scan_port(target_ip, port):
    """Scan a single port and return results"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, port))
            
            if result == 0:
                # Port is open - get service name and banner
                try:
                    service = socket.getservbyport(port, 'tcp')
                except:
                    service = "unknown"
                
                # Try to get banner
                banner = ""
                try:
                    sock.settimeout(0.5)
                    banner = sock.recv(1024).decode(errors='ignore').strip()
                except:
                    pass
                
                return port, service, banner, True
            else:
                return port, "", "", False
                
    except Exception:
        return port, "", "", False

def format_results(results):
    """Format and display the scan results"""
    open_ports = [r for r in results if r[3]]  # Filter open ports
    
    if not open_ports:
        print(f"\n{YELLOW}No open ports found{RESET}")
        return
    
    print(f"\n{GREEN}🎯 OPEN PORTS FOUND:{RESET}")
    print("-" * 60)
    print(f"{'Port':<8} {'Service':<15} {'Status':<10}")
    print("-" * 60)
    
    for port, service, banner, status in open_ports:
        print(f"{GREEN}{port:<8}{service:<15}{'OPEN':<10}{RESET}")
        if banner:
            # Limit banner length and clean it up
            clean_banner = ' '.join(banner.split()[:10])  # First 10 words
            if len(clean_banner) > 50:
                clean_banner = clean_banner[:47] + "..."
            print(f"{YELLOW}         Banner: {clean_banner}{RESET}")

def port_scan(target_host, start_port, end_port):
    """Main port scanning function"""
    try:
        # Resolve hostname to IP
        target_ip = socket.gethostbyname(target_host)
        print(f"🎯 Scanning {target_host} ({target_ip})")
        print(f"📡 Port range: {start_port}-{end_port}")
        print("⏳ Scanning...")
        
        results = []
        total_ports = end_port - start_port + 1
        
        # Scan ports with threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            # Create futures for all ports
            future_to_port = {
                executor.submit(scan_port, target_ip, port): port 
                for port in range(start_port, end_port + 1)
            }
            
            # Process results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                results.append(result)
                completed += 1
                
                # Progress indicator
                sys.stdout.write(f"\r📊 Progress: {completed}/{total_ports} ports scanned")
                sys.stdout.flush()
        
        print("\n")  # New line after progress
        format_results(results)
        
        # Summary
        open_count = len([r for r in results if r[3]])
        print(f"\n📊 Summary: {open_count} open ports out of {total_ports} scanned")
        
    except socket.gaierror:
        print(f"{RED}❌ Error: Cannot resolve hostname '{target_host}'{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️ Scan interrupted by user{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")

def main():
    """Main function with user input"""
    print(f"{GREEN}🔍 Python Port Scanner{RESET}")
    print("=" * 30)
    
    try:
        target_host = input("Enter target hostname or IP: ").strip()
        start_port = int(input("Enter start port: "))
        end_port = int(input("Enter end port: "))
        
        # Validate port range
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            print(f"{RED}❌ Invalid port range. Use 1-65535{RESET}")
            return
        
        port_scan(target_host, start_port, end_port)
        
    except ValueError:
        print(f"{RED}❌ Error: Please enter valid numbers for ports{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Goodbye!{RESET}")

if __name__ == '__main__':
    main()