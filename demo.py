#!/usr/bin/env python3
"""
MaScanner Demo - Interactive demonstration of scanner capabilities
"""

import sys
import time
import threading
from datetime import datetime
import json

try:
    from scanner import PortScanner
    from utils import NetworkUtils, PortUtils, FormatUtils, StatisticsCalculator, ValidationUtils
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the MaScanner directory")
    sys.exit(1)

class MaScannerDemo:
    def __init__(self):
        self.scanner = PortScanner()
        self.stats = StatisticsCalculator()

    def print_banner(self):
        """Print demo banner"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                     MaScanner Demo v1.0                     ║
    ║            Interactive Network Port Scanner Demo             ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print("Welcome to the MaScanner interactive demo!")
        print("This demonstration will showcase the scanning capabilities.\n")

    def demo_target_validation(self):
        """Demonstrate target validation"""
        print("🎯 Demo 1: Target Validation")
        print("=" * 40)

        test_targets = [
            "127.0.0.1",
            "192.168.1.0/24",
            "192.168.1.1-5",
            "localhost",
            "invalid.target.123456",
            "999.999.999.999"
        ]

        for target in test_targets:
            is_valid = self.scanner.validate_target(target)
            status = "✓ Valid" if is_valid else "✗ Invalid"
            print(f"  {target:<20} - {status}")

        input("\nPress Enter to continue...")

    def demo_port_parsing(self):
        """Demonstrate port parsing capabilities"""
        print("\n🔌 Demo 2: Port Range Parsing")
        print("=" * 40)

        test_ports = [
            "80",
            "22,80,443",
            "80-85",
            "22,80-85,443,8000-8080",
            "1-100",
            ""  # Default ports
        ]

        for port_spec in test_ports:
            try:
                ports = self.scanner.parse_port_range(port_spec)
                display_spec = port_spec if port_spec else "(default)"
                if len(ports) <= 10:
                    print(f"  {display_spec:<20} → {ports}")
                else:
                    print(f"  {display_spec:<20} → {len(ports)} ports ({ports[0]}-{ports[-1]})")
            except Exception as e:
                print(f"  {port_spec:<20} → Error: {e}")

        input("\nPress Enter to continue...")

    def demo_network_expansion(self):
        """Demonstrate network target expansion"""
        print("\n🌐 Demo 3: Network Target Expansion")
        print("=" * 40)

        test_networks = [
            "127.0.0.1",
            "192.168.1.1-3",
            "10.0.0.0/30"
        ]

        for network in test_networks:
            try:
                targets = self.scanner.expand_targets(network)
                print(f"  {network:<15} → {len(targets)} targets")
                if len(targets) <= 5:
                    print(f"    Targets: {', '.join(targets)}")
                else:
                    print(f"    Sample: {', '.join(targets[:3])}... (+{len(targets)-3} more)")
            except Exception as e:
                print(f"  {network:<15} → Error: {e}")

        input("\nPress Enter to continue...")

    def demo_service_detection(self):
        """Demonstrate service detection"""
        print("\n🔧 Demo 4: Service Detection")
        print("=" * 40)

        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389]

        print("Common port → service mappings:")
        for port in common_ports:
            service = self.scanner.get_service_name(port)
            description = PortUtils.get_port_description(port)
            print(f"  Port {port:<5} → {service:<12} ({description})")

        input("\nPress Enter to continue...")

    def demo_localhost_scan(self):
        """Demonstrate actual scanning on localhost"""
        print("\n🚀 Demo 5: Live Localhost Scan")
        print("=" * 40)

        print("Performing a quick scan on localhost (127.0.0.1)...")
        print("Scanning common ports: 22, 80, 443, 3389, 8080")
        print()

        # Progress callback for demo
        def demo_callback(callback_type, data=None):
            if callback_type == 'result':
                result = data
                print(f"  ✓ Found: {result['target']}:{result['port']} ({result['service']}) - {result['state']}")
            elif callback_type == 'progress':
                print(f"  Progress: {data:.1f}%", end='\r')

        start_time = time.time()

        # Start scan
        results = self.scanner.start_scan(
            ["127.0.0.1"],
            [22, 80, 443, 3389, 8080, 8888],
            "fast",
            10,
            0.5,
            demo_callback
        )

        elapsed = time.time() - start_time

        print(f"\n")
        print(f"Scan completed in {elapsed:.2f} seconds")
        print(f"Found {len(results)} open ports")

        if not results:
            print("No open ports found on localhost (this is normal for most systems)")

        input("\nPress Enter to continue...")

    def demo_ping_sweep(self):
        """Demonstrate ping sweep functionality"""
        print("\n📡 Demo 6: Ping Sweep")
        print("=" * 40)

        print("Performing ping sweep on local loopback range...")
        print("Testing: 127.0.0.1-127.0.0.3")
        print()

        def ping_callback(callback_type, data):
            if callback_type == 'ping_result':
                print(f"  ✓ Live host: {data['target']}")
            elif callback_type == 'error':
                print(f"  ✗ Error: {data}")

        start_time = time.time()
        live_hosts = self.scanner.ping_sweep(
            ["127.0.0.1", "127.0.0.2", "127.0.0.3"],
            ping_callback
        )
        elapsed = time.time() - start_time

        print(f"\nPing sweep completed in {elapsed:.2f} seconds")
        print(f"Live hosts found: {len(live_hosts)}")

        input("\nPress Enter to continue...")

    def demo_export_formats(self):
        """Demonstrate export capabilities"""
        print("\n💾 Demo 7: Export Formats")
        print("=" * 40)

        # Create sample results for demo
        sample_results = [
            {'target': '127.0.0.1', 'port': 80, 'state': 'open', 'service': 'http'},
            {'target': '127.0.0.1', 'port': 443, 'state': 'open', 'service': 'https'},
            {'target': '192.168.1.1', 'port': 22, 'state': 'open', 'service': 'ssh'}
        ]

        self.scanner.results = sample_results

        print("Sample scan results (for demonstration):")
        for result in sample_results:
            print(f"  {result['target']}:{result['port']} ({result['service']}) - {result['state']}")

        print("\nExporting to different formats...")

        # Export to different formats
        formats = [
            ('demo_results.txt', 'txt'),
            ('demo_results.csv', 'csv')
        ]

        for filename, format_type in formats:
            try:
                success = self.scanner.export_results(filename, format_type)
                if success:
                    print(f"  ✓ Exported to {filename} ({format_type.upper()} format)")

                    # Show a preview of the file
                    with open(filename, 'r') as f:
                        lines = f.readlines()[:5]  # First 5 lines
                        print(f"    Preview: {lines[0].strip()}")
                else:
                    print(f"  ✗ Failed to export to {filename}")
            except Exception as e:
                print(f"  ✗ Export error: {e}")

        input("\nPress Enter to continue...")

    def demo_performance_analysis(self):
        """Demonstrate performance analysis"""
        print("\n⚡ Demo 8: Performance Analysis")
        print("=" * 40)

        print("Analyzing scan performance with different configurations...")

        # Test different thread counts
        configs = [
            {'threads': 10, 'timeout': 0.5},
            {'threads': 50, 'timeout': 0.5},
            {'threads': 100, 'timeout': 0.5}
        ]

        print("\nTesting configurations on localhost ports 99990-99995:")

        for i, config in enumerate(configs, 1):
            print(f"\nConfiguration {i}: {config['threads']} threads, {config['timeout']}s timeout")

            start_time = time.time()

            results = self.scanner.start_scan(
                ["127.0.0.1"],
                list(range(99990, 99996)),  # 6 ports
                "fast",
                config['threads'],
                config['timeout']
            )

            elapsed = time.time() - start_time
            rate = 6 / max(elapsed, 0.1)  # 6 ports scanned

            print(f"  Time: {elapsed:.3f}s")
            print(f"  Rate: {rate:.0f} ports/sec")
            print(f"  Results: {len(results)} open ports")

        input("\nPress Enter to continue...")

    def demo_statistics(self):
        """Demonstrate statistics calculation"""
        print("\n📊 Demo 9: Scan Statistics")
        print("=" * 40)

        # Initialize statistics
        self.stats.reset()
        self.stats.start_scan(total_targets=5, total_ports=10)

        # Add some mock results
        mock_results = [
            {'target': '192.168.1.1', 'port': 80, 'state': 'open', 'service': 'http'},
            {'target': '192.168.1.1', 'port': 443, 'state': 'open', 'service': 'https'},
            {'target': '192.168.1.2', 'port': 22, 'state': 'open', 'service': 'ssh'},
            {'target': '192.168.1.3', 'port': 80, 'state': 'open', 'service': 'http'}
        ]

        for result in mock_results:
            self.stats.add_result(result)

        time.sleep(0.1)  # Small delay to show elapsed time
        self.stats.end_scan()

        # Get and display statistics
        statistics = self.stats.get_statistics()

        print("Scan Statistics (demo data):")
        print(f"  Total Targets: {statistics['targets']['total_targets']}")
        print(f"  Live Hosts: {statistics['targets']['live_hosts']}")
        print(f"  Open Ports: {statistics['ports']['open_ports_found']}")
        print(f"  Scan Time: {statistics['timing']['elapsed_formatted']}")
        print(f"  Scan Rate: {statistics['timing']['scan_rate_formatted']}")

        print(f"\nTop Services:")
        for service, count in statistics['services']['top_services'][:5]:
            print(f"  {service}: {count}")

        input("\nPress Enter to continue...")

    def demo_advanced_features(self):
        """Demonstrate advanced features"""
        print("\n🎛️  Demo 10: Advanced Features")
        print("=" * 40)

        print("Advanced MaScanner features:")
        print()

        # Network information
        print("1. Network Information Analysis:")
        local_ip = NetworkUtils.get_local_ip()
        network_info = NetworkUtils.get_network_info(local_ip)
        print(f"   Local IP: {local_ip}")
        for key, value in network_info.items():
            print(f"   {key.title()}: {value}")

        print()

        # Port categories
        print("2. Port Categories:")
        categories = ['web', 'mail', 'database', 'remote']
        for category in categories:
            ports = PortUtils.get_port_category_ports(category)
            print(f"   {category.title()}: {len(ports)} ports ({', '.join(map(str, ports[:5]))}{'...' if len(ports) > 5 else ''})")

        print()

        # Format utilities
        print("3. Format Utilities:")
        print(f"   Time formatting: {FormatUtils.format_time(3661)} (raw: 3661 seconds)")
        print(f"   Size formatting: {FormatUtils.format_size(1048576)} (raw: 1048576 bytes)")
        print(f"   Rate formatting: {FormatUtils.format_rate(1500)} (raw: 1500 ports/s)")

        print()

        # Security features
        print("4. Security Validation:")
        safe, message = ValidationUtils.validate_target_list("127.0.0.1,192.168.1.1,8.8.8.8")
        print(f"   Target validation: {message}")

        input("\nPress Enter to continue...")

    def interactive_scan_demo(self):
        """Interactive scan demonstration"""
        print("\n🔍 Interactive Scan Demo")
        print("=" * 40)

        print("Let's perform an interactive scan!")
        print("You can customize the scan parameters or use defaults.\n")

        # Get user input
        try:
            target = input("Enter target (default: 127.0.0.1): ").strip()
            if not target:
                target = "127.0.0.1"

            ports = input("Enter ports (default: 22,80,443,8080): ").strip()
            if not ports:
                ports = "22,80,443,8080"

            threads = input("Enter thread count (default: 20): ").strip()
            if not threads:
                threads = "20"

            print(f"\nStarting scan:")
            print(f"  Target: {target}")
            print(f"  Ports: {ports}")
            print(f"  Threads: {threads}")
            print()

            # Validate inputs
            if not self.scanner.validate_target(target):
                print("❌ Invalid target specified")
                return

            port_list = self.scanner.parse_port_range(ports)
            if not port_list:
                print("❌ No valid ports specified")
                return

            # Progress tracking
            progress_data = {'completed': 0, 'total': len(port_list)}

            def interactive_callback(callback_type, data=None):
                if callback_type == 'result':
                    result = data
                    print(f"  🎯 FOUND: {result['target']}:{result['port']} ({result['service']}) - {result['state']}")
                elif callback_type == 'progress':
                    print(f"  Progress: {data:.1f}% complete", end='\r')

            # Perform scan
            start_time = time.time()

            results = self.scanner.start_scan(
                [target],
                port_list,
                "fast",
                int(threads),
                1.0,
                interactive_callback
            )

            elapsed = time.time() - start_time

            print(f"\n")
            print(f"✅ Scan completed!")
            print(f"   Duration: {FormatUtils.format_time(elapsed)}")
            print(f"   Rate: {FormatUtils.format_rate(len(port_list) / max(elapsed, 0.1))}")
            print(f"   Results: {len(results)} open ports")

            if results:
                print(f"\nOpen ports found:")
                for result in results:
                    print(f"   {result['port']}/{result.get('protocol', 'tcp')} - {result['service']}")
            else:
                print(f"\nNo open ports found (this is normal for most localhost scans)")

        except KeyboardInterrupt:
            print("\n❌ Scan interrupted by user")
        except Exception as e:
            print(f"\n❌ Scan error: {e}")

        input("\nPress Enter to continue...")

    def demo_real_world_scenarios(self):
        """Demonstrate real-world scanning scenarios"""
        print("\n🌍 Demo 11: Real-World Scenarios")
        print("=" * 40)

        scenarios = [
            {
                'name': 'Web Server Discovery',
                'description': 'Find web servers in local network',
                'target': '192.168.1.0/24',
                'ports': '80,443,8080,8443',
                'threads': 100
            },
            {
                'name': 'Database Server Scan',
                'description': 'Check for database services',
                'target': '10.0.0.1-50',
                'ports': '1433,3306,5432,6379,27017',
                'threads': 50
            },
            {
                'name': 'Remote Access Audit',
                'description': 'Find remote access services',
                'target': '172.16.1.0/24',
                'ports': '22,23,3389,5900,5901',
                'threads': 75
            },
            {
                'name': 'Comprehensive Scan',
                'description': 'Full port scan on single host',
                'target': '192.168.1.100',
                'ports': '1-1000',
                'threads': 200
            }
        ]

        print("Common scanning scenarios:\n")

        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Command equivalent:")
            print(f"     Target: {scenario['target']}")
            print(f"     Ports: {scenario['ports']}")
            print(f"     Threads: {scenario['threads']}")

            # Calculate estimated time and scope
            try:
                target_count = len(self.scanner.expand_targets(scenario['target']))
                port_count = len(self.scanner.parse_port_range(scenario['ports']))
                total_checks = target_count * port_count

                print(f"   Scope: {target_count:,} targets × {port_count:,} ports = {total_checks:,} checks")

                # Rough time estimate
                estimated_time = (total_checks * 0.5) / scenario['threads']  # 0.5s per check average
                print(f"   Estimated time: ~{FormatUtils.format_time(estimated_time)}")

            except Exception as e:
                print(f"   Error calculating scope: {e}")

            print()

        input("Press Enter to continue...")

    def demo_security_considerations(self):
        """Demonstrate security considerations"""
        print("\n🔒 Demo 12: Security Considerations")
        print("=" * 40)

        print("Important security considerations when using MaScanner:\n")

        print("1. Legal and Ethical Use:")
        print("   ✓ Only scan networks you own")
        print("   ✓ Get explicit permission for penetration testing")
        print("   ✓ Follow responsible disclosure for vulnerabilities")
        print("   ✗ Never scan networks without authorization")

        print("\n2. Technical Considerations:")
        print("   • High thread counts can impact network performance")
        print("   • Some firewalls may detect and block scanning")
        print("   • SYN scans require administrator privileges")
        print("   • Rate limiting prevents network congestion")

        print("\n3. Target Safety Check:")
        test_targets = ["127.0.0.1", "192.168.1.1", "8.8.8.8"]

        for target in test_targets:
            try:
                from utils import SecurityUtils
                safe, message = SecurityUtils.validate_target_safety(target)
                status = "✓ Safe" if safe else "⚠️  Warning"
                print(f"   {target:<15} - {status}: {message}")
            except:
                print(f"   {target:<15} - Unable to validate")

        print("\n4. Best Practices:")
        print("   • Start with ping sweep to find live hosts")
        print("   • Use appropriate timeouts for your network")
        print("   • Monitor system resources during large scans")
        print("   • Save results for analysis and reporting")

        input("\nPress Enter to continue...")

    def show_final_summary(self):
        """Show final demo summary"""
        print("\n🎉 Demo Complete!")
        print("=" * 40)

        print("You've seen the key features of MaScanner:")
        print()
        print("✓ Target validation and expansion")
        print("✓ Flexible port specification")
        print("✓ High-performance concurrent scanning")
        print("✓ Service detection and banner grabbing")
        print("✓ Multiple export formats")
        print("✓ Real-time progress tracking")
        print("✓ Security validation")
        print()

        print("Getting Started:")
        print("1. GUI Launcher:     python launcher.py")
        print("2. Basic GUI:        python main.py")
        print("3. Advanced GUI:     python gui_advanced.py")
        print("4. Command Line:     python cli.py --help")
        print()

        print("Example Commands:")
        print("• Quick local scan:  python cli.py 127.0.0.1 -p 22,80,443")
        print("• Network discovery: python cli.py 192.168.1.0/24 --ping-sweep")
        print("• Web server scan:   python cli.py 192.168.1.1-254 -p 80,443,8080")
        print()

        print("Documentation:")
        print("• README.md - Complete usage guide")
        print("• python cli.py --help - CLI reference")
        print("• GUI tooltips and help menus")
        print()

        print("⚠️  Remember: Use responsibly and only on authorized networks!")
        print()
        print("Thank you for trying MaScanner! 🚀")

    def cleanup_demo_files(self):
        """Clean up demo files"""
        demo_files = ['demo_results.txt', 'demo_results.csv']
        for file in demo_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

    def run_demo(self):
        """Run the complete demo"""
        try:
            self.print_banner()

            demos = [
                self.demo_target_validation,
                self.demo_port_parsing,
                self.demo_network_expansion,
                self.demo_service_detection,
                self.demo_localhost_scan,
                self.demo_ping_sweep,
                self.demo_export_formats,
                self.demo_performance_analysis,
                self.demo_statistics,
                self.demo_advanced_features,
                self.demo_real_world_scenarios,
                self.demo_security_considerations
            ]

            print(f"This demo consists of {len(demos)} parts.")
            response = input("Run full demo? (y/N): ").lower()

            if response == 'y':
                for i, demo_func in enumerate(demos, 1):
                    print(f"\n{'='*60}")
                    print(f"Part {i}/{len(demos)}")
                    demo_func()
            else:
                print("Demo skipped. You can run individual parts by calling the functions directly.")

            self.show_final_summary()

        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\nDemo error: {e}")
        finally:
            self.cleanup_demo_files()

def quick_demo():
    """Run a quick demonstration without user interaction"""
    print("MaScanner Quick Demo")
    print("=" * 30)

    scanner = PortScanner()

    # Quick validation test
    print("1. Testing target validation...")
    targets = ["127.0.0.1", "invalid", "192.168.1.0/30"]
    for target in targets:
        valid = scanner.validate_target(target)
        print(f"   {target:<20} - {'Valid' if valid else 'Invalid'}")

    # Quick port parsing test
    print("\n2. Testing port parsing...")
    port_specs = ["80", "22,80,443", "80-85"]
    for spec in port_specs:
        ports = scanner.parse_port_range(spec)
        print(f"   {spec:<15} → {len(ports)} ports")

    # Quick localhost scan
    print("\n3. Testing localhost scan...")
    try:
        results = scanner.start_scan(["127.0.0.1"], [22, 80], "fast", 5, 0.5)
        print(f"   Scanned localhost:22,80 → {len(results)} open ports")
    except Exception as e:
        print(f"   Scan error: {e}")

    print("\n✅ Quick demo completed!")
    print("Run 'python demo.py' for the full interactive demo.")

def main():
    """Main demo entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_demo()
    else:
        demo = MaScannerDemo()
        demo.run_demo()

if __name__ == "__main__":
    main()
