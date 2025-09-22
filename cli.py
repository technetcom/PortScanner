#!/usr/bin/env python3
"""
MaScanner CLI - Command Line Interface for Network Port Scanner
"""

import argparse
import sys
import os
import time
import signal
from datetime import datetime
import json
import csv
from scanner import PortScanner

class MaScannerCLI:
    def __init__(self):
        self.scanner = PortScanner()
        self.start_time = None
        self.interrupted = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        print("\n[!] Scan interrupted by user")
        self.interrupted = True
        self.scanner.stop_scan()
        sys.exit(0)

    def print_banner(self):
        """Print application banner"""
        banner = """
    ███╗   ███╗ █████╗ ███████╗ ██████╗ █████╗ ███╗   ███╗███╗   ██╗███████╗██████╗
    ████╗ ████║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗ ████║████╗  ██║██╔════╝██╔══██╗
    ██╔████╔██║███████║███████╗██║     ███████║██╔████╔██║██╔██╗ ██║█████╗  ██████╔╝
    ██║╚██╔╝██║██╔══██║╚════██║██║     ██╔══██║██║╚██╔╝██║██║╚██╗██║██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║██║  ██║███████║╚██████╗██║  ██║██║ ╚═╝ ██║██║ ╚████║███████╗██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝

    MaScanner v1.0 - High-Performance Network Port Scanner
    Inspired by masscan | Built with Python
        """
        print(banner)

    def validate_targets(self, targets):
        """Validate target specifications"""
        target_list = targets.split(',')
        valid_targets = []
        invalid_targets = []

        for target in target_list:
            target = target.strip()
            if self.scanner.validate_target(target):
                valid_targets.append(target)
            else:
                invalid_targets.append(target)

        if invalid_targets:
            print(f"[!] Warning: Invalid targets found: {', '.join(invalid_targets)}")

        if not valid_targets:
            print("[!] Error: No valid targets specified")
            return False

        return valid_targets

    def validate_ports(self, ports):
        """Validate port specifications"""
        try:
            port_list = self.scanner.parse_port_range(ports)
            if not port_list:
                print("[!] Error: No valid ports specified")
                return False
            return port_list
        except ValueError as e:
            print(f"[!] Error: Invalid port specification: {str(e)}")
            return False

    def cli_callback(self, callback_type, data=None):
        """Handle callbacks from scanner for CLI output"""
        if callback_type == 'result':
            # Print result immediately
            result = data
            protocol = result.get('protocol', 'tcp')
            print(f"[+] {result['target']}:{result['port']} ({protocol}) - {result['service']} - {result['state']}")
        elif callback_type == 'progress':
            # Show progress bar
            self.show_progress(data)
        elif callback_type == 'error':
            print(f"[!] Error: {data}")
        elif isinstance(callback_type, str) and callback_type.startswith("Starting"):
            print(f"[*] {callback_type}")

    def show_progress(self, percentage):
        """Show progress bar in terminal"""
        bar_length = 50
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r[*] Progress: |{bar}| {percentage:.1f}%", end='', flush=True)

        if percentage >= 100:
            print()  # New line when complete

    def ping_sweep_cli(self, targets, output_file=None, verbose=False):
        """Perform ping sweep with CLI output"""
        print(f"[*] Starting ping sweep on {len(targets)} targets...")

        live_hosts = []

        def ping_callback(callback_type, data):
            nonlocal live_hosts
            if callback_type == 'ping_result':
                live_hosts.append(data['target'])
                if verbose:
                    print(f"[+] Live host: {data['target']}")
            elif callback_type == 'error':
                if verbose:
                    print(f"[!] {data}")

        results = self.scanner.ping_sweep(targets, ping_callback)

        print(f"\n[*] Ping sweep completed. Found {len(results)} live hosts:")
        for host in results:
            print(f"    {host}")

        if output_file:
            self.save_ping_results(results, output_file)

        return results

    def save_ping_results(self, hosts, filename):
        """Save ping sweep results to file"""
        try:
            with open(filename, 'w') as f:
                f.write(f"# MaScanner Ping Sweep Results\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total live hosts: {len(hosts)}\n\n")
                for host in hosts:
                    f.write(f"{host}\n")
            print(f"[*] Ping results saved to {filename}")
        except Exception as e:
            print(f"[!] Failed to save ping results: {str(e)}")

    def port_scan_cli(self, targets, ports, scan_type, max_workers, timeout, output_file, output_format, verbose):
        """Perform port scan with CLI output"""
        target_list = self.scanner.expand_targets(','.join(targets))
        port_list = self.scanner.parse_port_range(ports)

        total_combinations = len(target_list) * len(port_list)

        print(f"[*] Starting {scan_type} scan:")
        print(f"    Targets: {len(target_list)}")
        print(f"    Ports: {len(port_list)}")
        print(f"    Total combinations: {total_combinations:,}")
        print(f"    Threads: {max_workers}")
        print(f"    Timeout: {timeout}s")
        print()

        self.start_time = time.time()

        # Start scan
        results = self.scanner.start_scan(
            target_list, port_list, scan_type, max_workers, timeout, self.cli_callback
        )

        # Calculate scan statistics
        elapsed = time.time() - self.start_time
        scan_rate = total_combinations / max(elapsed, 0.1)

        print(f"\n[*] Scan completed in {elapsed:.2f} seconds")
        print(f"[*] Scan rate: {scan_rate:.0f} ports/second")
        print(f"[*] Open ports found: {len(results)}")

        if results:
            print(f"\n[*] Summary of open ports:")
            # Group by host for summary
            hosts = {}
            for result in results:
                host = result['target']
                if host not in hosts:
                    hosts[host] = []
                hosts[host].append(result)

            for host, host_results in hosts.items():
                ports_str = ','.join(str(r['port']) for r in host_results)
                print(f"    {host}: {ports_str}")

        # Save results if requested
        if output_file:
            self.save_results(results, output_file, output_format)

        return results

    def save_results(self, results, filename, format):
        """Save scan results to file"""
        try:
            if format == 'json':
                self.save_json_results(results, filename)
            elif format == 'csv':
                self.save_csv_results(results, filename)
            elif format == 'xml':
                self.save_xml_results(results, filename)
            else:  # txt
                self.save_txt_results(results, filename)

            print(f"[*] Results saved to {filename}")
        except Exception as e:
            print(f"[!] Failed to save results: {str(e)}")

    def save_json_results(self, results, filename):
        """Save results in JSON format"""
        output_data = {
            'scan_info': {
                'tool': 'MaScanner CLI',
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'elapsed_time': time.time() - self.start_time if self.start_time else 0,
                'total_results': len(results)
            },
            'results': results
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)

    def save_csv_results(self, results, filename):
        """Save results in CSV format"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Target', 'Port', 'State', 'Service', 'Protocol'])

            for result in results:
                writer.writerow([
                    result['target'],
                    result['port'],
                    result['state'],
                    result['service'],
                    result.get('protocol', 'tcp')
                ])

    def save_xml_results(self, results, filename):
        """Save results in XML format"""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<scanresults>\n')
            f.write(f'  <scaninfo tool="MaScanner CLI" version="1.0" timestamp="{datetime.now().isoformat()}"/>\n')

            for result in results:
                f.write(f'  <host addr="{result["target"]}">\n')
                f.write(f'    <port portid="{result["port"]}" protocol="{result.get("protocol", "tcp")}">\n')
                f.write(f'      <state state="{result["state"]}"/>\n')
                f.write(f'      <service name="{result["service"]}"/>\n')
                f.write(f'    </port>\n')
                f.write(f'  </host>\n')

            f.write('</scanresults>\n')

    def save_txt_results(self, results, filename):
        """Save results in text format"""
        with open(filename, 'w') as f:
            f.write("MaScanner CLI Scan Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for result in results:
                f.write(f"Target: {result['target']}\n")
                f.write(f"Port: {result['port']}\n")
                f.write(f"State: {result['state']}\n")
                f.write(f"Service: {result['service']}\n")
                f.write(f"Protocol: {result.get('protocol', 'tcp')}\n")
                f.write("-" * 40 + "\n")

    def load_targets_from_file(self, filename):
        """Load targets from file"""
        try:
            with open(filename, 'r') as f:
                targets = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
                return targets
        except Exception as e:
            print(f"[!] Error loading targets from {filename}: {str(e)}")
            return []

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="MaScanner - High-performance network port scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 192.168.1.1 -p 80,443
  %(prog)s 192.168.1.0/24 -p 1-1000 --threads 200
  %(prog)s scanme.nmap.org -p 22,80,443 --scan-type SYN
  %(prog)s -iL targets.txt -p 1-65535 -oJ results.json
  %(prog)s 192.168.1.1-254 --ping-sweep -oN live_hosts.txt

Target Specification:
  192.168.1.1          - Single IP
  192.168.1.1-254      - IP range
  192.168.1.0/24       - CIDR notation
  scanme.nmap.org      - Hostname
  -iL <file>           - Load from file

Port Specification:
  80                   - Single port
  1-1000               - Port range
  22,80,443            - Multiple ports
  22,80-90,443         - Mixed format
        """)

    # Target specification
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('targets', nargs='?', help='Target specification (IP, range, CIDR, hostname)')
    target_group.add_argument('-iL', '--input-file', dest='target_file',
                            help='Load targets from file (one per line)')

    # Port specification
    parser.add_argument('-p', '--ports', default='22,80,443,3389,21,23,25,53,110,143,993,995',
                       help='Port specification (default: common ports)')

    # Scan options
    parser.add_argument('-sT', '--scan-type', choices=['fast', 'SYN', 'TCP', 'UDP'],
                       default='fast', help='Scan type (default: fast)')
    parser.add_argument('--threads', type=int, default=100,
                       help='Number of scanning threads (default: 100)')
    parser.add_argument('--timeout', type=float, default=1.0,
                       help='Connection timeout in seconds (default: 1.0)')
    parser.add_argument('--rate-limit', type=int, default=1000,
                       help='Maximum packets per second (default: 1000)')

    # Output options
    output_group = parser.add_argument_group('output options')
    output_group.add_argument('-oN', '--output-normal', dest='output_txt',
                            help='Save results in normal format')
    output_group.add_argument('-oJ', '--output-json', dest='output_json',
                            help='Save results in JSON format')
    output_group.add_argument('-oC', '--output-csv', dest='output_csv',
                            help='Save results in CSV format')
    output_group.add_argument('-oX', '--output-xml', dest='output_xml',
                            help='Save results in XML format')

    # Special scans
    parser.add_argument('--ping-sweep', action='store_true',
                       help='Perform ping sweep (host discovery only)')
    parser.add_argument('--top-ports', type=int, metavar='N',
                       help='Scan top N most common ports')

    # Verbosity and timing
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (minimal output)')
    parser.add_argument('--no-banner', action='store_true',
                       help='Suppress banner')

    # Performance options
    parser.add_argument('-T', '--timing', type=int, choices=[0,1,2,3,4,5], default=3,
                       help='Timing template (0=paranoid, 5=insane, default: 3)')

    return parser

def get_top_ports(n):
    """Get top N most common ports"""
    top_ports = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
        143, 443, 993, 995, 1723, 3306, 3389, 5900, 8080
    ]

    if n <= len(top_ports):
        return ','.join(map(str, top_ports[:n]))
    else:
        # Extend with more ports if needed
        extended_ports = list(range(1, n + 1))
        return ','.join(map(str, extended_ports))

def main():
    """Main CLI entry point"""
    parser = create_parser()

    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    args = parser.parse_args()

    # Create CLI instance
    cli = MaScannerCLI()

    # Show banner unless suppressed
    if not args.no_banner and not args.quiet:
        cli.print_banner()

    # Get targets
    if args.target_file:
        targets = cli.load_targets_from_file(args.target_file)
        if not targets:
            print("[!] No valid targets loaded from file")
            return 1
        targets_str = ','.join(targets)
    else:
        targets_str = args.targets

    # Validate targets
    target_list = cli.validate_targets(targets_str)
    if not target_list:
        return 1

    # Handle top ports option
    ports = args.ports
    if args.top_ports:
        ports = get_top_ports(args.top_ports)
        if not args.quiet:
            print(f"[*] Using top {args.top_ports} ports")

    # Validate ports
    port_list = cli.validate_ports(ports)
    if not port_list:
        return 1

    # Ping sweep mode
    if args.ping_sweep:
        if not args.quiet:
            print(f"[*] Ping sweep mode enabled")

        expanded_targets = cli.scanner.expand_targets(targets_str)
        results = cli.ping_sweep_cli(expanded_targets, args.output_txt, args.verbose)

        if not results and not args.quiet:
            print("[*] No live hosts found")

        return 0

    # Port scan mode
    if not args.quiet:
        print(f"[*] Scan configuration:")
        print(f"    Targets: {len(cli.scanner.expand_targets(targets_str))}")
        print(f"    Ports: {len(port_list)}")
        print(f"    Scan type: {args.scan_type}")
        print(f"    Threads: {args.threads}")
        print(f"    Timeout: {args.timeout}s")
        print()

    # Adjust timeout based on timing template
    timing_timeouts = {0: 5.0, 1: 2.0, 2: 1.5, 3: 1.0, 4: 0.5, 5: 0.3}
    if args.timing in timing_timeouts:
        timeout = timing_timeouts[args.timing]
        if not args.quiet:
            print(f"[*] Using timing template T{args.timing} (timeout: {timeout}s)")
    else:
        timeout = args.timeout

    # Start the scan
    try:
        results = cli.port_scan_cli(
            target_list, ports, args.scan_type,
            args.threads, timeout,
            args.output_txt, 'txt', args.verbose
        )

        # Save results in different formats if requested
        if args.output_json:
            cli.save_results(results, args.output_json, 'json')
        if args.output_csv:
            cli.save_results(results, args.output_csv, 'csv')
        if args.output_xml:
            cli.save_results(results, args.output_xml, 'xml')

        # Final summary
        if not args.quiet:
            if results:
                print(f"\n[*] Scan Summary:")
                hosts_with_open_ports = len(set(r['target'] for r in results))
                print(f"    Hosts with open ports: {hosts_with_open_ports}")
                print(f"    Total open ports: {len(results)}")

                # Most common services
                services = {}
                for result in results:
                    service = result['service']
                    services[service] = services.get(service, 0) + 1

                if services:
                    print(f"    Most common services:")
                    sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
                    for service, count in sorted_services[:5]:
                        print(f"      {service}: {count}")
            else:
                print("[*] No open ports found")

        return 0

    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        return 1
    except Exception as e:
        print(f"[!] Scan error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
