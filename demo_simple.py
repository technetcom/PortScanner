#!/usr/bin/env python3
"""
MaScanner Simple Demo - Demonstration without external dependencies
Shows core functionality using only Python standard library
"""

import socket
import threading
import time
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class SimpleMaScanner:
    """Simplified scanner using only standard library"""

    def __init__(self):
        self.results = []
        self.is_scanning = False

    def validate_ip(self, ip_str):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    def expand_ip_range(self, target):
        """Expand IP range to list of IPs"""
        if '/' in target:
            # CIDR notation
            try:
                network = ipaddress.ip_network(target, strict=False)
                return [str(ip) for ip in list(network.hosts())[:10]]  # Limit for demo
            except ValueError:
                return []
        elif '-' in target:
            # Range notation
            try:
                start_ip, end_part = target.split('-')
                start_parts = start_ip.strip().split('.')
                end_num = int(end_part.strip())
                start_num = int(start_parts[3])
                base = '.'.join(start_parts[:3])

                ips = []
                for i in range(start_num, min(end_num + 1, start_num + 10)):  # Limit for demo
                    ips.append(f"{base}.{i}")
                return ips
            except (ValueError, IndexError):
                return []
        else:
            return [target]

    def parse_ports(self, port_str):
        """Parse port specification"""
        ports = []
        if not port_str.strip():
            return [22, 80, 443]  # Default ports

        for part in port_str.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    ports.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    ports.append(int(part))
                except ValueError:
                    continue

        return sorted(list(set(ports)))

    def scan_port(self, host, port, timeout=1.0):
        """Scan single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return {
                    'host': host,
                    'port': port,
                    'state': 'open',
                    'service': self.get_service_name(port)
                }
        except Exception:
            pass
        return None

    def get_service_name(self, port):
        """Get service name for port"""
        services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
            53: 'dns', 80: 'http', 110: 'pop3', 143: 'imap',
            443: 'https', 993: 'imaps', 995: 'pop3s',
            3389: 'rdp', 3306: 'mysql', 5432: 'postgresql'
        }
        return services.get(port, 'unknown')

    def fast_scan(self, targets, ports, max_workers=50, timeout=1.0, callback=None):
        """Fast concurrent port scan"""
        self.results = []
        self.is_scanning = True

        total_scans = len(targets) * len(ports)
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_scan = {}

            for target in targets:
                for port in ports:
                    if not self.is_scanning:
                        break
                    future = executor.submit(self.scan_port, target, port, timeout)
                    future_to_scan[future] = (target, port)

            for future in as_completed(future_to_scan):
                if not self.is_scanning:
                    break

                result = future.result()
                completed += 1

                if result:
                    self.results.append(result)
                    if callback:
                        callback('result', result)

                progress = (completed / total_scans) * 100
                if callback:
                    callback('progress', progress)

        return self.results

    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False

def print_banner():
    """Print demo banner"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║              MaScanner Simple Demo                         ║
    ║         High-Performance Port Scanner Demo                 ║
    ╚════════════════════════════════════════════════════════════╝

    This demo shows MaScanner's core functionality using only
    Python standard library (no nmap dependency required).
    """)

def demo_validation():
    """Demonstrate input validation"""
    print("📋 Demo 1: Input Validation")
    print("=" * 40)

    scanner = SimpleMaScanner()

    test_ips = [
        "127.0.0.1",
        "192.168.1.1",
        "8.8.8.8",
        "256.1.1.1",
        "invalid.ip"
    ]

    print("Testing IP validation:")
    for ip in test_ips:
        valid = scanner.validate_ip(ip)
        status = "✓ Valid" if valid else "✗ Invalid"
        print(f"  {ip:<15} - {status}")

    print("\nTesting port parsing:")
    port_specs = ["80", "22,80,443", "80-85", "22,80-85,443"]

    for spec in port_specs:
        ports = scanner.parse_ports(spec)
        if len(ports) <= 6:
            print(f"  {spec:<15} → {ports}")
        else:
            print(f"  {spec:<15} → {len(ports)} ports ({ports[0]}-{ports[-1]})")

def demo_target_expansion():
    """Demonstrate target expansion"""
    print("\n🌐 Demo 2: Target Expansion")
    print("=" * 40)

    scanner = SimpleMaScanner()

    targets = [
        "127.0.0.1",
        "192.168.1.1-5",
        "10.0.0.0/29"
    ]

    for target in targets:
        expanded = scanner.expand_ip_range(target)
        print(f"  {target:<15} → {len(expanded)} IPs")
        if len(expanded) <= 5:
            print(f"    {expanded}")
        else:
            print(f"    {expanded[:3]}... (+{len(expanded)-3} more)")

def demo_service_detection():
    """Demonstrate service detection"""
    print("\n🔧 Demo 3: Service Detection")
    print("=" * 40)

    scanner = SimpleMaScanner()

    common_ports = [21, 22, 25, 53, 80, 110, 143, 443, 3389]

    print("Port → Service mapping:")
    for port in common_ports:
        service = scanner.get_service_name(port)
        print(f"  {port:<6} → {service}")

def demo_live_scan():
    """Demonstrate live scanning"""
    print("\n🚀 Demo 4: Live Port Scan")
    print("=" * 40)

    scanner = SimpleMaScanner()

    print("Scanning localhost (127.0.0.1) on common ports...")
    print("This demonstrates the actual scanning engine.\n")

    # Progress tracking
    progress_data = {'last_progress': 0}

    def scan_callback(callback_type, data):
        if callback_type == 'result':
            print(f"  🎯 OPEN PORT: {data['host']}:{data['port']} ({data['service']})")
        elif callback_type == 'progress':
            # Only show progress every 20%
            if data - progress_data['last_progress'] >= 20:
                print(f"  Progress: {data:.0f}%")
                progress_data['last_progress'] = data

    target = "127.0.0.1"
    ports = [22, 23, 80, 443, 8080, 8888, 3389]

    print(f"Target: {target}")
    print(f"Ports: {ports}")
    print(f"Method: TCP Connect")
    print()

    start_time = time.time()

    results = scanner.fast_scan([target], ports, max_workers=10, timeout=0.5, callback=scan_callback)

    elapsed = time.time() - start_time

    print(f"\n✅ Scan Complete!")
    print(f"   Duration: {elapsed:.2f} seconds")
    print(f"   Ports checked: {len(ports)}")
    print(f"   Open ports: {len(results)}")
    print(f"   Scan rate: {len(ports) / elapsed:.0f} ports/second")

    if results:
        print(f"\n📊 Results Summary:")
        for result in results:
            print(f"   {result['port']}/tcp - {result['service']} - {result['state']}")
    else:
        print(f"\n💡 No open ports found (normal for most systems)")

def demo_concurrent_performance():
    """Demonstrate concurrent scanning performance"""
    print("\n⚡ Demo 5: Performance Test")
    print("=" * 40)

    scanner = SimpleMaScanner()

    # Test different thread counts
    thread_counts = [1, 5, 10, 20]
    test_ports = list(range(99990, 99996))  # 6 closed ports for consistent timing

    print("Testing scan performance with different thread counts...")
    print("(Scanning closed ports for consistent timing)\n")

    for threads in thread_counts:
        print(f"  Testing {threads} threads...")

        start_time = time.time()
        scanner.fast_scan(["127.0.0.1"], test_ports, max_workers=threads, timeout=0.1)
        elapsed = time.time() - start_time

        rate = len(test_ports) / elapsed
        print(f"    Time: {elapsed:.3f}s, Rate: {rate:.0f} ports/sec")

    print(f"\n💡 More threads generally improve performance up to a point")

def demo_export_functionality():
    """Demonstrate export capabilities"""
    print("\n💾 Demo 6: Export Functionality")
    print("=" * 40)

    # Create sample results
    sample_results = [
        {'host': '192.168.1.1', 'port': 22, 'state': 'open', 'service': 'ssh'},
        {'host': '192.168.1.1', 'port': 80, 'state': 'open', 'service': 'http'},
        {'host': '192.168.1.5', 'port': 443, 'state': 'open', 'service': 'https'}
    ]

    print("Sample results for export demo:")
    for result in sample_results:
        print(f"  {result['host']}:{result['port']} - {result['service']} - {result['state']}")

    # Export to JSON
    try:
        export_data = {
            'scan_info': {
                'tool': 'MaScanner Simple Demo',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_results': len(sample_results)
            },
            'results': sample_results
        }

        with open('demo_results.json', 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n✅ Exported to demo_results.json")

        # Show preview
        print(f"Preview:")
        with open('demo_results.json', 'r') as f:
            lines = f.readlines()[:8]
            for line in lines:
                print(f"  {line.rstrip()}")

    except Exception as e:
        print(f"❌ Export failed: {e}")

def demo_security_features():
    """Demonstrate security considerations"""
    print("\n🔒 Demo 7: Security Features")
    print("=" * 40)

    scanner = SimpleMaScanner()

    print("Target safety validation:")

    test_targets = [
        ("127.0.0.1", "Localhost - Safe"),
        ("192.168.1.1", "Private IP - Safe for internal use"),
        ("10.0.0.1", "Private IP - Safe for internal use"),
        ("8.8.8.8", "Public IP - Requires permission!")
    ]

    for target, description in test_targets:
        is_private = ipaddress.ip_address(target).is_private if scanner.validate_ip(target) else False
        is_loopback = ipaddress.ip_address(target).is_loopback if scanner.validate_ip(target) else False

        if is_loopback or is_private:
            status = "✅ Safe"
        else:
            status = "⚠️  Requires Permission"

        print(f"  {target:<15} - {status} - {description}")

    print(f"\n💡 Security Reminders:")
    print(f"   • Only scan networks you own")
    print(f"   • Get written permission for penetration testing")
    print(f"   • Follow responsible disclosure for vulnerabilities")
    print(f"   • Respect rate limits and network capacity")

def interactive_scan():
    """Interactive scan demonstration"""
    print("\n🎮 Interactive Scan Demo")
    print("=" * 40)

    scanner = SimpleMaScanner()

    print("Let's do a real scan! You can customize the parameters.")
    print()

    try:
        # Get user input
        target_input = input("Enter target (default: 127.0.0.1): ").strip()
        target = target_input if target_input else "127.0.0.1"

        port_input = input("Enter ports (default: 22,80,443): ").strip()
        ports_str = port_input if port_input else "22,80,443"

        threads_input = input("Enter thread count (default: 20): ").strip()
        threads = int(threads_input) if threads_input.isdigit() else 20

        # Validate and expand
        if not scanner.validate_ip(target) and '/' not in target and '-' not in target:
            print(f"❌ Invalid target: {target}")
            return

        targets = scanner.expand_ip_range(target)
        ports = scanner.parse_ports(ports_str)

        print(f"\n🎯 Scan Configuration:")
        print(f"   Targets: {len(targets)} ({targets[0]}" + (f"...+{len(targets)-1}" if len(targets) > 1 else "") + ")")
        print(f"   Ports: {len(ports)} ({ports[0]}" + (f"...{ports[-1]}" if len(ports) > 1 else "") + ")")
        print(f"   Threads: {threads}")
        print(f"   Total checks: {len(targets) * len(ports)}")

        input("\nPress Enter to start scan...")

        # Progress callback
        def scan_callback(callback_type, data):
            if callback_type == 'result':
                print(f"  🎯 FOUND: {data['host']}:{data['port']} ({data['service']}) - {data['state']}")
            elif callback_type == 'progress':
                print(f"  Progress: {data:.1f}%", end='\r')

        print(f"\n🚀 Scanning...")
        start_time = time.time()

        results = scanner.fast_scan(targets, ports, max_workers=threads, timeout=1.0, callback=scan_callback)

        elapsed = time.time() - start_time

        print(f"\n")
        print(f"✅ Scan Results:")
        print(f"   Duration: {elapsed:.2f} seconds")
        print(f"   Rate: {(len(targets) * len(ports)) / elapsed:.0f} checks/second")
        print(f"   Open ports: {len(results)}")

        if results:
            print(f"\n📋 Open Ports:")
            for result in results:
                print(f"   {result['host']}:{result['port']} - {result['service']}")

            # Offer to export
            export = input(f"\nExport results to file? (y/N): ").lower()
            if export == 'y':
                filename = f"scan_results_{int(time.time())}.json"
                export_data = {
                    'scan_info': {
                        'target': target,
                        'ports': ports_str,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'duration': elapsed,
                        'total_results': len(results)
                    },
                    'results': results
                }

                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)

                print(f"✅ Results exported to {filename}")
        else:
            print(f"   No open ports found")

    except KeyboardInterrupt:
        print(f"\n❌ Scan interrupted")
        scanner.stop_scan()
    except Exception as e:
        print(f"\n❌ Scan error: {e}")

def show_features_overview():
    """Show complete feature overview"""
    print("\n🎉 MaScanner Feature Overview")
    print("=" * 40)

    features = [
        ("🎯 Target Support", [
            "Single IPs (192.168.1.1)",
            "IP ranges (192.168.1.1-254)",
            "CIDR notation (192.168.1.0/24)",
            "Hostnames (example.com)",
            "Multiple targets (comma-separated)"
        ]),
        ("🔌 Port Specification", [
            "Single ports (80)",
            "Port ranges (1-1000)",
            "Multiple ports (22,80,443)",
            "Mixed format (22,80-90,443)",
            "Port presets (web, database, etc.)"
        ]),
        ("⚡ Scan Types", [
            "Fast TCP Connect (no privileges required)",
            "TCP SYN scan (requires admin privileges)",
            "UDP scan (requires admin privileges)",
            "Ping sweep (host discovery)",
            "Service detection with banner grabbing"
        ]),
        ("🖥️  User Interfaces", [
            "Basic GUI - Simple, clean interface",
            "Advanced GUI - Tabs, statistics, logging",
            "Command Line - Full CLI for automation",
            "GUI Launcher - Choose your interface"
        ]),
        ("📊 Advanced Features", [
            "Real-time progress tracking",
            "Concurrent multi-threaded scanning",
            "Results filtering and grouping",
            "Performance statistics",
            "Export to multiple formats (TXT, CSV, JSON, XML)"
        ]),
        ("🔒 Security", [
            "Target safety validation",
            "Privilege checking",
            "Rate limiting",
            "Ethical use guidelines",
            "Permission reminders"
        ])
    ]

    for category, items in features:
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

def main():
    """Main demo function"""
    print_banner()

    print("This interactive demo showcases MaScanner's capabilities.")
    print("No external dependencies required for this demo.\n")

    demos = [
        ("Input Validation", demo_validation),
        ("Target Expansion", demo_target_expansion),
        ("Service Detection", demo_service_detection),
        ("Live Scanning", demo_live_scan),
        ("Performance Test", demo_concurrent_performance),
        ("Export Features", demo_export_functionality),
        ("Security Features", demo_security_features),
        ("Interactive Scan", interactive_scan),
        ("Feature Overview", show_features_overview)
    ]

    try:
        print("📋 Available Demos:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i}. {name}")
        print(f"  0. Run All Demos")

        choice = input(f"\nSelect demo (0-{len(demos)}): ").strip()

        if choice == '0':
            # Run all demos
            for name, demo_func in demos:
                print(f"\n{'='*60}")
                demo_func()
                if name != demos[-1][0]:  # Not the last demo
                    input("\nPress Enter for next demo...")
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            # Run selected demo
            demo_index = int(choice) - 1
            name, demo_func = demos[demo_index]
            print(f"\n{'='*60}")
            demo_func()
        else:
            print("❌ Invalid choice")
            return

        print(f"\n🎉 Demo Complete!")
        print(f"\nNext Steps:")
        print(f"  1. Install full dependencies: python3 run.py --install")
        print(f"  2. Start GUI: python3 run.py gui")
        print(f"  3. Try CLI: python3 run.py cli --help")
        print(f"  4. Read documentation: README.md")

    except KeyboardInterrupt:
        print(f"\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        # Cleanup demo files
        try:
            import os
            for file in ['demo_results.json']:
                if os.path.exists(file):
                    os.remove(file)
        except:
            pass

if __name__ == "__main__":
    main()
