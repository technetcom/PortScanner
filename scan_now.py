#!/usr/bin/env python3
"""
MaScanner - Working CLI Port Scanner
Fast network port scanner that works immediately without external dependencies
"""

import socket
import threading
import time
import sys
import argparse
import ipaddress
import subprocess
import platform
import json
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class FastPortScanner:
    """High-performance port scanner using only Python standard library"""

    def __init__(self):
        self.results = []
        self.is_scanning = False
        self.scan_stats = {
            'start_time': None,
            'total_targets': 0,
            'total_ports': 0,
            'open_ports': 0,
            'live_hosts': set()
        }

    def validate_ip(self, ip_str):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    def resolve_hostname(self, hostname):
        """Resolve hostname to IP"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

    def expand_targets(self, target_str):
        """Expand target specification to list of IPs"""
        targets = []

        for target in target_str.split(','):
            target = target.strip()

            if '/' in target:  # CIDR notation
                try:
                    network = ipaddress.ip_network(target, strict=False)
                    targets.extend([str(ip) for ip in network.hosts()])
                except ValueError:
                    print(f"Warning: Invalid CIDR notation: {target}")

            elif '-' in target:  # IP range
                try:
                    start_ip, end_part = target.split('-')
                    start_parts = start_ip.strip().split('.')
                    end_num = int(end_part.strip())
                    start_num = int(start_parts[3])
                    base = '.'.join(start_parts[:3])

                    for i in range(start_num, end_num + 1):
                        targets.append(f"{base}.{i}")
                except (ValueError, IndexError):
                    print(f"Warning: Invalid IP range: {target}")

            else:  # Single IP or hostname
                if self.validate_ip(target):
                    targets.append(target)
                else:
                    # Try to resolve as hostname
                    resolved_ip = self.resolve_hostname(target)
                    if resolved_ip:
                        targets.append(resolved_ip)
                    else:
                        print(f"Warning: Cannot resolve target: {target}")

        return list(set(targets))  # Remove duplicates

    def parse_ports(self, port_str):
        """Parse port specification"""
        ports = []

        if not port_str.strip():
            return [22, 80, 443, 3389]  # Default common ports

        for part in port_str.split(','):
            part = part.strip()

            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end:
                        ports.extend(range(start, end + 1))
                except ValueError:
                    print(f"Warning: Invalid port range: {part}")
            else:
                try:
                    port = int(part)
                    if 1 <= port <= 65535:
                        ports.append(port)
                    else:
                        print(f"Warning: Port out of range: {port}")
                except ValueError:
                    print(f"Warning: Invalid port: {part}")

        return sorted(list(set(ports)))

    def get_service_name(self, port):
        """Get common service name for port"""
        services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
            80: 'http', 110: 'pop3', 143: 'imap', 443: 'https', 993: 'imaps',
            995: 'pop3s', 1433: 'mssql', 3306: 'mysql', 3389: 'rdp',
            5432: 'postgresql', 5900: 'vnc', 6379: 'redis', 8080: 'http-alt',
            8443: 'https-alt', 27017: 'mongodb'
        }
        return services.get(port, 'unknown')

    def scan_port(self, host, port, timeout=1.0):
        """Scan single port using TCP connect"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return {
                    'target': host,
                    'port': port,
                    'state': 'open',
                    'service': self.get_service_name(port),
                    'protocol': 'tcp'
                }
        except Exception:
            pass

        return None

    def ping_host(self, host, timeout=1):
        """Ping host to check if alive"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), host]
            else:
                cmd = ['ping', '-c', '1', '-W', str(timeout), host]

            result = subprocess.run(cmd, capture_output=True, timeout=timeout + 1)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def start_scan(self, targets, ports, max_workers=100, timeout=1.0, progress_callback=None):
        """Start concurrent port scan"""
        self.results = []
        self.is_scanning = True
        self.scan_stats['start_time'] = time.time()
        self.scan_stats['total_targets'] = len(targets)
        self.scan_stats['total_ports'] = len(ports)
        self.scan_stats['open_ports'] = 0
        self.scan_stats['live_hosts'].clear()

        total_scans = len(targets) * len(ports)
        completed_scans = 0

        print(f"[*] Starting scan: {len(targets)} targets × {len(ports)} ports = {total_scans:,} checks")
        print(f"[*] Configuration: {max_workers} threads, {timeout}s timeout")
        print()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scan tasks
            future_to_scan = {}
            for target in targets:
                for port in ports:
                    if not self.is_scanning:
                        break
                    future = executor.submit(self.scan_port, target, port, timeout)
                    future_to_scan[future] = (target, port)

            # Process completed scans
            for future in as_completed(future_to_scan):
                if not self.is_scanning:
                    break

                result = future.result()
                completed_scans += 1

                if result:
                    self.results.append(result)
                    self.scan_stats['open_ports'] += 1
                    self.scan_stats['live_hosts'].add(result['target'])
                    print(f"[+] {result['target']}:{result['port']} - {result['service']} - {result['state']}")

                # Update progress
                progress = (completed_scans / total_scans) * 100
                if progress_callback:
                    progress_callback(progress)
                elif completed_scans % max(1, total_scans // 20) == 0:  # Show progress every 5%
                    print(f"[*] Progress: {progress:.1f}% ({completed_scans:,}/{total_scans:,})")

        return self.results

    def ping_sweep(self, targets, timeout=1, progress_callback=None):
        """Perform ping sweep to find live hosts"""
        live_hosts = []
        total_targets = len(targets)

        print(f"[*] Starting ping sweep on {total_targets} targets...")

        for i, target in enumerate(targets):
            if not self.is_scanning:
                break

            if self.ping_host(target, timeout):
                live_hosts.append(target)
                print(f"[+] Live host: {target}")

            # Progress update
            progress = ((i + 1) / total_targets) * 100
            if progress_callback:
                progress_callback(progress)
            elif (i + 1) % max(1, total_targets // 10) == 0:
                print(f"[*] Ping progress: {progress:.1f}%")

        return live_hosts

    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False

    def get_scan_stats(self):
        """Get scan statistics"""
        if self.scan_stats['start_time']:
            elapsed = time.time() - self.scan_stats['start_time']
            total_checks = self.scan_stats['total_targets'] * self.scan_stats['total_ports']
            rate = total_checks / max(elapsed, 0.1)

            return {
                'elapsed_time': elapsed,
                'total_checks': total_checks,
                'scan_rate': rate,
                'open_ports': self.scan_stats['open_ports'],
                'live_hosts': len(self.scan_stats['live_hosts'])
            }
        return {}

def export_results(results, filename, format_type='txt'):
    """Export scan results to file"""
    try:
        if format_type == 'json':
            export_data = {
                'scan_info': {
                    'tool': 'MaScanner',
                    'timestamp': datetime.now().isoformat(),
                    'total_results': len(results)
                },
                'results': results
            }
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)

        elif format_type == 'csv':
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Target', 'Port', 'State', 'Service', 'Protocol'])
                for result in results:
                    writer.writerow([
                        result['target'], result['port'], result['state'],
                        result['service'], result['protocol']
                    ])

        else:  # txt format
            with open(filename, 'w') as f:
                f.write("MaScanner Scan Results\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                for result in results:
                    f.write(f"Target: {result['target']}\n")
                    f.write(f"Port: {result['port']}\n")
                    f.write(f"State: {result['state']}\n")
                    f.write(f"Service: {result['service']}\n")
                    f.write(f"Protocol: {result['protocol']}\n")
                    f.write("-" * 30 + "\n")

        print(f"[*] Results exported to {filename}")
        return True

    except Exception as e:
        print(f"[!] Export failed: {e}")
        return False

def print_banner():
    """Print MaScanner banner"""
    banner = """
    ███╗   ███╗ █████╗ ███████╗ ██████╗ █████╗ ███╗   ███╗
    ████╗ ████║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗ ████║
    ██╔████╔██║███████║███████╗██║     ███████║██╔████╔██║
    ██║╚██╔╝██║██╔══██║╚════██║██║     ██╔══██║██║╚██╔╝██║
    ██║ ╚═╝ ██║██║  ██║███████║╚██████╗██║  ██║██║ ╚═╝ ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝

    MaScanner v1.0 - Fast Network Port Scanner
    High-performance scanning with Python standard library
    """
    print(banner)

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="MaScanner - Fast Network Port Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 127.0.0.1 -p 22,80,443
  %(prog)s 192.168.1.1-254 -p 80,443 --threads 200
  %(prog)s 192.168.1.0/24 --ping-sweep
  %(prog)s scanme.nmap.org -p 1-1000 -o results.json
  %(prog)s 10.0.0.1-50 -p 22,3389 --timeout 2.0

Target formats:
  192.168.1.1          Single IP
  192.168.1.1-254      IP range
  192.168.1.0/24       CIDR notation
  example.com          Hostname
  target1,target2      Multiple targets
        """)

    # Target specification
    parser.add_argument('targets', help='Target specification (IP, range, CIDR, hostname)')

    # Port specification
    parser.add_argument('-p', '--ports', default='22,80,443,3389',
                       help='Port specification (default: 22,80,443,3389)')

    # Scan options
    parser.add_argument('--threads', type=int, default=100,
                       help='Number of scanning threads (default: 100)')
    parser.add_argument('--timeout', type=float, default=1.0,
                       help='Connection timeout in seconds (default: 1.0)')
    parser.add_argument('--ping-sweep', action='store_true',
                       help='Perform ping sweep only (host discovery)')

    # Output options
    parser.add_argument('-o', '--output',
                       help='Output file for results')
    parser.add_argument('--format', choices=['txt', 'json', 'csv'], default='txt',
                       help='Output format (default: txt)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode')

    # Timing templates
    parser.add_argument('-T', '--timing', type=int, choices=[0,1,2,3,4,5], default=3,
                       help='Timing template (0=paranoid, 5=insane, default: 3)')

    args = parser.parse_args()

    # Show banner unless quiet
    if not args.quiet:
        print_banner()

    # Create scanner
    scanner = FastPortScanner()

    # Adjust settings based on timing template
    timing_settings = {
        0: {'threads': 10, 'timeout': 5.0},   # Paranoid
        1: {'threads': 20, 'timeout': 3.0},   # Sneaky
        2: {'threads': 50, 'timeout': 2.0},   # Polite
        3: {'threads': 100, 'timeout': 1.0},  # Normal
        4: {'threads': 200, 'timeout': 0.5},  # Aggressive
        5: {'threads': 500, 'timeout': 0.3}   # Insane
    }

    if args.timing in timing_settings:
        settings = timing_settings[args.timing]
        if args.threads == 100:  # Only override if user didn't specify
            args.threads = settings['threads']
        if args.timeout == 1.0:  # Only override if user didn't specify
            args.timeout = settings['timeout']

    # Expand targets
    target_list = scanner.expand_targets(args.targets)
    if not target_list:
        print("[!] No valid targets found")
        return 1

    if not args.quiet:
        print(f"[*] Targets: {len(target_list)}")
        if args.verbose:
            for target in target_list[:5]:
                print(f"    {target}")
            if len(target_list) > 5:
                print(f"    ... and {len(target_list) - 5} more")

    # Handle ping sweep mode
    if args.ping_sweep:
        if not args.quiet:
            print(f"[*] Ping sweep mode")

        try:
            live_hosts = scanner.ping_sweep(target_list, timeout=args.timeout)

            if not args.quiet:
                print(f"\n[*] Ping sweep completed")
                print(f"[*] Live hosts: {len(live_hosts)}")

            if live_hosts:
                if not args.quiet:
                    print(f"\nLive hosts found:")
                for host in live_hosts:
                    print(f"  {host}")

                # Export if requested
                if args.output:
                    ping_results = [{'target': host, 'status': 'alive'} for host in live_hosts]
                    if args.format == 'json':
                        export_data = {
                            'scan_type': 'ping_sweep',
                            'timestamp': datetime.now().isoformat(),
                            'live_hosts': live_hosts
                        }
                        with open(args.output, 'w') as f:
                            json.dump(export_data, f, indent=2)
                    else:
                        with open(args.output, 'w') as f:
                            f.write("MaScanner Ping Sweep Results\n")
                            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("=" * 40 + "\n\n")
                            for host in live_hosts:
                                f.write(f"{host}\n")
                    print(f"[*] Results saved to {args.output}")
            else:
                print("No live hosts found")

        except KeyboardInterrupt:
            print("\n[!] Ping sweep interrupted")
            return 1

        return 0

    # Parse ports for port scanning
    port_list = scanner.parse_ports(args.ports)
    if not port_list:
        print("[!] No valid ports found")
        return 1

    if not args.quiet:
        print(f"[*] Ports: {len(port_list)}")
        if args.verbose:
            if len(port_list) <= 20:
                print(f"    {port_list}")
            else:
                print(f"    {port_list[:10]}... (+{len(port_list)-10} more)")
        print(f"[*] Threads: {args.threads}")
        print(f"[*] Timeout: {args.timeout}s")
        print(f"[*] Total checks: {len(target_list) * len(port_list):,}")
        print()

    # Start port scan
    try:
        def progress_callback(progress):
            if not args.quiet and args.verbose:
                print(f"\r[*] Progress: {progress:.1f}%", end='', flush=True)

        start_time = time.time()

        results = scanner.start_scan(
            target_list, port_list, args.threads, args.timeout,
            progress_callback if args.verbose else None
        )

        elapsed = time.time() - start_time

        if args.verbose:
            print()  # New line after progress

        # Print summary
        if not args.quiet:
            print(f"\n[*] Scan completed in {elapsed:.2f} seconds")
            print(f"[*] Scan rate: {(len(target_list) * len(port_list)) / elapsed:.0f} checks/second")
            print(f"[*] Open ports found: {len(results)}")
            print(f"[*] Live hosts: {len(scanner.scan_stats['live_hosts'])}")

        if results:
            if not args.quiet:
                print(f"\nOpen ports by host:")

            # Group results by host
            hosts = {}
            for result in results:
                host = result['target']
                if host not in hosts:
                    hosts[host] = []
                hosts[host].append(result)

            for host, host_results in hosts.items():
                ports_str = ','.join(str(r['port']) for r in host_results)
                print(f"  {host}: {ports_str}")
        else:
            print("No open ports found")

        # Export results if requested
        if args.output and results:
            export_results(results, args.output, args.format)

    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        scanner.stop_scan()
        return 1
    except Exception as e:
        print(f"[!] Scan error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        sys.exit(1)
