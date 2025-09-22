import nmap
import socket
import threading
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import subprocess
import platform

class PortScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.is_scanning = False
        self.scan_thread = None
        self.results = []

    def validate_target(self, target):
        """Validate if target is a valid IP, IP range, or hostname"""
        if not target or not target.strip():
            return False
            
        try:
            # Check if it's a single IP
            ipaddress.ip_address(target)
            return True
        except ValueError:
            pass

        try:
            # Check if it's a CIDR notation
            ipaddress.ip_network(target, strict=False)
            return True
        except ValueError:
            pass

        try:
            # Check if it's a hostname
            socket.gethostbyname(target)
            return True
        except socket.gaierror:
            pass

        # Check if it's an IP range (e.g., 192.168.1.1-254)
        if '-' in target:
            parts = target.split('-')
            if len(parts) == 2:
                try:
                    base_ip = parts[0].strip()
                    end_range = int(parts[1].strip())
                    # Validate base IP
                    ip_parts = base_ip.split('.')
                    if len(ip_parts) == 4:
                        for part in ip_parts:
                            int(part)
                        return True
                except (ValueError, IndexError):
                    pass

        return False

    def parse_port_range(self, port_range):
        """Parse port range string into list of ports"""
        ports = []

        if not port_range.strip():
            return list(range(1, 1001))  # Default common ports

        ranges = port_range.split(',')
        for r in ranges:
            r = r.strip()
            if '-' in r:
                start, end = map(int, r.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(r))

        return sorted(list(set(ports)))

    def expand_targets(self, target_string):
        """Expand target string into list of individual IPs"""
        targets = []

        for target in target_string.split(','):
            target = target.strip()

            if '/' in target:  # CIDR notation
                network = ipaddress.ip_network(target, strict=False)
                targets.extend([str(ip) for ip in network.hosts()])
            elif '-' in target:  # IP range
                parts = target.split('-')
                if len(parts) == 2:
                    base_ip = parts[0].strip()
                    end_range = int(parts[1].strip())
                    ip_parts = base_ip.split('.')
                    base_num = int(ip_parts[-1])
                    base_prefix = '.'.join(ip_parts[:-1])

                    for i in range(base_num, end_range + 1):
                        targets.append(f"{base_prefix}.{i}")
            else:  # Single IP or hostname
                try:
                    # Try to resolve hostname to IP
                    ip = socket.gethostbyname(target)
                    targets.append(ip)
                except socket.gaierror:
                    targets.append(target)

        return targets

    def scan_port(self, target, port, timeout=1):
        """Scan a single port on a target"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()

            if result == 0:
                return {
                    'target': target,
                    'port': port,
                    'state': 'open',
                    'service': self.get_service_name(port)
                }
        except Exception as e:
            pass

        return None

    def get_service_name(self, port):
        """Get common service name for port"""
        common_ports = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
            53: 'dns', 80: 'http', 110: 'pop3', 143: 'imap',
            443: 'https', 993: 'imaps', 995: 'pop3s',
            3389: 'rdp', 5432: 'postgresql', 3306: 'mysql',
            1433: 'mssql', 6379: 'redis', 27017: 'mongodb'
        }
        return common_ports.get(port, 'unknown')

    def nmap_scan(self, targets, ports, scan_type='SYN', callback=None):
        """Perform nmap scan"""
        try:
            target_str = ' '.join(targets) if isinstance(targets, list) else targets
            port_str = ','.join(map(str, ports)) if isinstance(ports, list) else str(ports)

            scan_args = f'-p {port_str}'

            if scan_type == 'SYN':
                scan_args += ' -sS'
            elif scan_type == 'TCP':
                scan_args += ' -sT'
            elif scan_type == 'UDP':
                scan_args += ' -sU'
            elif scan_type == 'PING':
                scan_args = '-sn'

            scan_args += ' -T4'  # Aggressive timing

            if callback:
                callback(f"Starting nmap scan: nmap {scan_args} {target_str}")

            self.nm.scan(target_str, arguments=scan_args)

            results = []
            for host in self.nm.all_hosts():
                for protocol in self.nm[host].all_protocols():
                    ports_info = self.nm[host][protocol].keys()
                    for port in ports_info:
                        state = self.nm[host][protocol][port]['state']
                        if state == 'open':
                            service = self.nm[host][protocol][port].get('name', 'unknown')
                            results.append({
                                'target': host,
                                'port': port,
                                'protocol': protocol,
                                'state': state,
                                'service': service
                            })

            return results

        except Exception as e:
            if callback:
                callback(f"Error during nmap scan: {str(e)}")
            return []

    def fast_scan(self, targets, ports, max_workers=100, timeout=1, callback=None):
        """Fast concurrent port scan similar to masscan"""
        if not isinstance(targets, list):
            targets = [targets]

        if not isinstance(ports, list):
            ports = [ports]

        self.results = []
        total_scans = len(targets) * len(ports)
        completed_scans = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scan tasks
            future_to_scan = {}
            for target in targets:
                for port in ports:
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
                    if callback:
                        callback('result', result)

                # Update progress
                progress = (completed_scans / total_scans) * 100
                if callback:
                    callback('progress', progress)

        return self.results

    def ping_sweep(self, targets, callback=None):
        """Perform ping sweep to find live hosts"""
        if not isinstance(targets, list):
            targets = [targets]

        live_hosts = []

        for target in targets:
            if not self.is_scanning:
                break

            try:
                # Use ping command based on OS
                if platform.system().lower() == 'windows':
                    cmd = ['ping', '-n', '1', '-w', '1000', target]
                else:
                    cmd = ['ping', '-c', '1', '-W', '1', target]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)

                if result.returncode == 0:
                    live_hosts.append(target)
                    if callback:
                        callback('ping_result', {'target': target, 'status': 'alive'})

            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                if callback:
                    callback('error', f"Ping error for {target}: {str(e)}")

        return live_hosts

    def start_scan(self, targets, ports, scan_type='fast', max_workers=100, timeout=1, callback=None):
        """Start scanning process"""
        self.is_scanning = True
        self.results = []

        if scan_type == 'fast':
            return self.fast_scan(targets, ports, max_workers, timeout, callback)
        elif scan_type in ['SYN', 'TCP', 'UDP', 'PING']:
            return self.nmap_scan(targets, ports, scan_type, callback)
        else:
            if callback:
                callback('error', f"Unknown scan type: {scan_type}")
            return []

    def stop_scan(self):
        """Stop ongoing scan"""
        self.is_scanning = False

    def get_results(self):
        """Get current scan results"""
        return self.results

    def export_results(self, filename, format='txt'):
        """Export results to file"""
        try:
            with open(filename, 'w') as f:
                if format == 'txt':
                    f.write("MaScanner Results\n")
                    f.write("=" * 50 + "\n\n")
                    for result in self.results:
                        f.write(f"Host: {result['target']}\n")
                        f.write(f"Port: {result['port']}\n")
                        f.write(f"State: {result['state']}\n")
                        f.write(f"Service: {result['service']}\n")
                        f.write("-" * 30 + "\n")
                elif format == 'csv':
                    f.write("Target,Port,State,Service\n")
                    for result in self.results:
                        f.write(f"{result['target']},{result['port']},{result['state']},{result['service']}\n")

            return True
        except Exception as e:
            return False
