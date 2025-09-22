#!/usr/bin/env python3
"""
MaScanner Utilities - Common networking and helper functions
"""

import socket
import struct
import ipaddress
import re
import subprocess
import platform
import threading
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
import random

class NetworkUtils:
    """Network utility functions"""

    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        """Check if string is a valid IP address"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_network(network_str: str) -> bool:
        """Check if string is a valid network in CIDR notation"""
        try:
            ipaddress.ip_network(network_str, strict=False)
            return True
        except ValueError:
            return False

    @staticmethod
    def expand_ip_range(ip_range: str) -> List[str]:
        """Expand IP range string to list of IPs"""
        if '/' in ip_range:
            # CIDR notation
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
                return [str(ip) for ip in network.hosts()]
            except ValueError:
                return []

        elif '-' in ip_range:
            # Range notation (e.g., 192.168.1.1-254)
            try:
                start_ip, end_part = ip_range.split('-')
                start_ip = start_ip.strip()
                end_part = end_part.strip()

                # Parse start IP
                start_parts = start_ip.split('.')
                if len(start_parts) != 4:
                    return []

                # Handle different range formats
                if '.' in end_part:
                    # Full end IP
                    end_ip = end_part
                    start = ipaddress.ip_address(start_ip)
                    end = ipaddress.ip_address(end_ip)

                    ips = []
                    current = int(start)
                    end_int = int(end)

                    while current <= end_int:
                        ips.append(str(ipaddress.ip_address(current)))
                        current += 1

                    return ips
                else:
                    # Just the last octet
                    end_octet = int(end_part)
                    start_octet = int(start_parts[3])
                    base = '.'.join(start_parts[:3])

                    ips = []
                    for i in range(start_octet, end_octet + 1):
                        ips.append(f"{base}.{i}")

                    return ips
            except (ValueError, IndexError):
                return []

        else:
            # Single IP or hostname
            return [ip_range]

    @staticmethod
    def resolve_hostname(hostname: str) -> Optional[str]:
        """Resolve hostname to IP address"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

    @staticmethod
    def reverse_dns(ip: str) -> Optional[str]:
        """Perform reverse DNS lookup"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except socket.herror:
            return None

    @staticmethod
    def get_local_ip() -> str:
        """Get local machine's IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def get_local_network() -> str:
        """Get local network in CIDR notation"""
        try:
            local_ip = NetworkUtils.get_local_ip()
            # Assume /24 network for simplicity
            network_base = '.'.join(local_ip.split('.')[:-1]) + '.0'
            return f"{network_base}/24"
        except Exception:
            return "192.168.1.0/24"

    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """Check if IP address is in private ranges"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False

    @staticmethod
    def get_network_info(ip: str) -> Dict[str, str]:
        """Get network information for an IP"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return {
                'ip': str(ip_obj),
                'version': f"IPv{ip_obj.version}",
                'is_private': str(ip_obj.is_private),
                'is_multicast': str(ip_obj.is_multicast),
                'is_loopback': str(ip_obj.is_loopback),
                'is_link_local': str(ip_obj.is_link_local)
            }
        except ValueError:
            return {'error': 'Invalid IP address'}

class PortUtils:
    """Port-related utility functions"""

    # Common port to service mappings
    COMMON_PORTS = {
        20: 'ftp-data', 21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
        26: 'rsftp', 53: 'dns', 67: 'dhcp', 68: 'dhcp', 69: 'tftp',
        79: 'finger', 80: 'http', 88: 'kerberos', 102: 'iso-tsap',
        110: 'pop3', 113: 'ident', 119: 'nntp', 135: 'msrpc',
        137: 'netbios-ns', 138: 'netbios-dgm', 139: 'netbios-ssn',
        143: 'imap', 161: 'snmp', 179: 'bgp', 389: 'ldap',
        443: 'https', 445: 'microsoft-ds', 465: 'smtps', 514: 'syslog',
        515: 'printer', 587: 'smtp', 631: 'ipp', 636: 'ldaps',
        873: 'rsync', 993: 'imaps', 995: 'pop3s', 1433: 'mssql',
        1521: 'oracle', 1723: 'pptp', 3306: 'mysql', 3389: 'rdp',
        5432: 'postgresql', 5900: 'vnc', 6379: 'redis', 8080: 'http-alt',
        8443: 'https-alt', 27017: 'mongodb'
    }

    # Port categories
    PORT_CATEGORIES = {
        'web': [80, 443, 8000, 8008, 8080, 8081, 8443, 8888, 9000, 9080, 9443],
        'mail': [25, 110, 143, 465, 587, 993, 995],
        'database': [1433, 1521, 3306, 5432, 6379, 27017],
        'remote': [22, 23, 3389, 5900, 5901],
        'file': [20, 21, 69, 445, 515, 873, 2049],
        'dns': [53, 853],
        'dhcp': [67, 68],
        'common': [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 3389]
    }

    @staticmethod
    def get_service_name(port: int) -> str:
        """Get service name for port number"""
        return PortUtils.COMMON_PORTS.get(port, 'unknown')

    @staticmethod
    def get_port_info(port: int) -> Dict[str, Union[str, int]]:
        """Get detailed information about a port"""
        service = PortUtils.get_service_name(port)

        # Determine category
        category = 'other'
        for cat_name, ports in PortUtils.PORT_CATEGORIES.items():
            if port in ports:
                category = cat_name
                break

        # Get protocol
        protocol = 'tcp'  # Most ports are TCP by default
        udp_ports = [53, 67, 68, 69, 123, 161, 162, 500, 514, 1194]
        if port in udp_ports:
            protocol = 'udp'

        return {
            'port': port,
            'service': service,
            'category': category,
            'protocol': protocol,
            'description': PortUtils.get_port_description(port)
        }

    @staticmethod
    def get_port_description(port: int) -> str:
        """Get description for port"""
        descriptions = {
            21: 'File Transfer Protocol',
            22: 'Secure Shell',
            23: 'Telnet',
            25: 'Simple Mail Transfer Protocol',
            53: 'Domain Name System',
            80: 'Hypertext Transfer Protocol',
            110: 'Post Office Protocol v3',
            143: 'Internet Message Access Protocol',
            443: 'HTTP Secure',
            993: 'IMAP over SSL',
            995: 'POP3 over SSL',
            3389: 'Remote Desktop Protocol',
            3306: 'MySQL Database',
            5432: 'PostgreSQL Database'
        }
        return descriptions.get(port, f'Port {port}')

    @staticmethod
    def parse_port_list(port_string: str) -> List[int]:
        """Parse port string into list of port numbers"""
        ports = []

        if not port_string.strip():
            return ports

        # Split by commas
        ranges = port_string.split(',')

        for port_range in ranges:
            port_range = port_range.strip()

            if '-' in port_range:
                # Port range
                try:
                    start, end = map(int, port_range.split('-'))
                    if start <= end and 1 <= start <= 65535 and 1 <= end <= 65535:
                        ports.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                # Single port
                try:
                    port = int(port_range)
                    if 1 <= port <= 65535:
                        ports.append(port)
                except ValueError:
                    continue

        return sorted(list(set(ports)))

    @staticmethod
    def get_port_category_ports(category: str) -> List[int]:
        """Get ports for a specific category"""
        return PortUtils.PORT_CATEGORIES.get(category, [])

class ScanUtils:
    """Scanning utility functions"""

    @staticmethod
    def check_port_tcp(host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if TCP port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    @staticmethod
    def check_port_udp(host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if UDP port is open (basic check)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(b'', (host, port))
            sock.close()
            return True  # UDP is connectionless, so we assume it's open
        except Exception:
            return False

    @staticmethod
    def ping_host(host: str, timeout: int = 1) -> bool:
        """Ping a host to check if it's alive"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), host]
            else:
                cmd = ['ping', '-c', '1', '-W', str(timeout), host]

            result = subprocess.run(cmd, capture_output=True, timeout=timeout + 1)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    @staticmethod
    def get_banner(host: str, port: int, timeout: float = 2.0) -> Optional[str]:
        """Try to grab banner from a service"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Send some common probes
            probes = [b'', b'\r\n', b'GET / HTTP/1.0\r\n\r\n']

            for probe in probes:
                try:
                    if probe:
                        sock.send(probe)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        sock.close()
                        return banner
                except:
                    continue

            sock.close()
        except Exception:
            pass

        return None

    @staticmethod
    def detect_os(host: str) -> Dict[str, str]:
        """Basic OS detection based on TTL and other factors"""
        try:
            # This is a simplified OS detection
            # Real implementation would use nmap's OS detection
            if platform.system().lower() == 'windows':
                result = subprocess.run(['ping', '-n', '1', host],
                                      capture_output=True, text=True, timeout=3)
            else:
                result = subprocess.run(['ping', '-c', '1', host],
                                      capture_output=True, text=True, timeout=3)

            if result.returncode == 0:
                output = result.stdout

                # Look for TTL values
                ttl_match = re.search(r'ttl=(\d+)', output.lower())
                if ttl_match:
                    ttl = int(ttl_match.group(1))

                    if ttl <= 64:
                        return {'os': 'Linux/Unix', 'confidence': 'medium', 'ttl': str(ttl)}
                    elif ttl <= 128:
                        return {'os': 'Windows', 'confidence': 'medium', 'ttl': str(ttl)}
                    else:
                        return {'os': 'Unknown', 'confidence': 'low', 'ttl': str(ttl)}

            return {'os': 'Unknown', 'confidence': 'none', 'ttl': '0'}

        except Exception:
            return {'os': 'Unknown', 'confidence': 'none', 'ttl': '0'}

class FormatUtils:
    """Formatting and output utility functions"""

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format elapsed time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}h {minutes}m {secs}s"

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format byte size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def format_rate(rate: float) -> str:
        """Format scan rate in human-readable format"""
        if rate < 1000:
            return f"{rate:.0f} ports/s"
        elif rate < 1000000:
            return f"{rate/1000:.1f}k ports/s"
        else:
            return f"{rate/1000000:.1f}M ports/s"

    @staticmethod
    def colorize_text(text: str, color: str) -> str:
        """Add ANSI color codes to text for terminal output"""
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }

        color_code = colors.get(color.lower(), '')
        reset_code = colors['reset']

        return f"{color_code}{text}{reset_code}"

class ValidationUtils:
    """Input validation utilities"""

    @staticmethod
    def validate_port_range(port_string: str) -> Tuple[bool, str]:
        """Validate port range string"""
        try:
            ports = PortUtils.parse_port_list(port_string)
            if not ports:
                return False, "No valid ports found"

            if len(ports) > 65535:
                return False, "Too many ports specified"

            return True, f"Valid: {len(ports)} ports"

        except Exception as e:
            return False, f"Invalid format: {str(e)}"

    @staticmethod
    def validate_target_list(target_string: str) -> Tuple[bool, str, List[str]]:
        """Validate target list and return expanded targets"""
        if not target_string or not target_string.strip():
            return False, "Empty target string", []
            
        try:
            target_parts = [t.strip() for t in target_string.split(',')]
            valid_targets = []
            invalid_targets = []

            for target in target_parts:
                if NetworkUtils.is_valid_ip(target) or NetworkUtils.is_valid_network(target):
                    valid_targets.extend(NetworkUtils.expand_ip_range(target))
                elif '-' in target and not target.startswith('-'):
                    # IP range
                    expanded = NetworkUtils.expand_ip_range(target)
                    if expanded:
                        valid_targets.extend(expanded)
                    else:
                        invalid_targets.append(target)
                else:
                    # Try to resolve as hostname
                    ip = NetworkUtils.resolve_hostname(target)
                    if ip:
                        valid_targets.append(ip)
                    else:
                        invalid_targets.append(target)

            # Remove duplicates
            valid_targets = list(set(valid_targets))

            if not valid_targets:
                return False, "No valid targets found", []

            warning = ""
            if invalid_targets:
                warning = f"Warning: {len(invalid_targets)} invalid targets ignored"

            return True, f"Valid: {len(valid_targets)} targets. {warning}".strip(), valid_targets

        except Exception as e:
            return False, f"Error parsing targets: {str(e)}", []

    @staticmethod
    def validate_thread_count(thread_count: int) -> Tuple[bool, str]:
        """Validate thread count"""
        if thread_count < 1:
            return False, "Thread count must be at least 1"
        elif thread_count > 2000:
            return False, "Thread count too high (max: 2000)"
        elif thread_count > 500:
            return True, "Warning: High thread count may impact performance"
        else:
            return True, "Valid thread count"

    @staticmethod
    def validate_timeout(timeout: float) -> Tuple[bool, str]:
        """Validate timeout value"""
        if timeout <= 0:
            return False, "Timeout must be greater than 0"
        elif timeout > 30:
            return False, "Timeout too high (max: 30s)"
        elif timeout < 0.1:
            return True, "Warning: Very low timeout may miss slow services"
        else:
            return True, "Valid timeout"

class FileUtils:
    """File handling utilities"""

    @staticmethod
    def load_targets_from_file(filename: str) -> List[str]:
        """Load targets from file, filtering comments and empty lines"""
        targets = []
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Basic validation
                    if NetworkUtils.is_valid_ip(line) or NetworkUtils.is_valid_network(line):
                        targets.append(line)
                    elif NetworkUtils.resolve_hostname(line):
                        targets.append(line)
                    else:
                        print(f"Warning: Invalid target on line {line_num}: {line}")

        except FileNotFoundError:
            print(f"Error: File not found: {filename}")
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")

        return targets

    @staticmethod
    def save_targets_to_file(targets: List[str], filename: str) -> bool:
        """Save targets to file"""
        try:
            with open(filename, 'w') as f:
                f.write(f"# MaScanner Target List\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total targets: {len(targets)}\n\n")

                for target in targets:
                    f.write(f"{target}\n")

            return True
        except Exception as e:
            print(f"Error saving targets to {filename}: {str(e)}")
            return False

    @staticmethod
    def get_safe_filename(base_name: str, extension: str = '') -> str:
        """Generate safe filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)

        if extension and not extension.startswith('.'):
            extension = '.' + extension

        return f"{safe_name}_{timestamp}{extension}"

class RateLimiter:
    """Rate limiting utility for controlling scan speed"""

    def __init__(self, max_rate: int):
        """Initialize rate limiter with maximum operations per second"""
        self.max_rate = max_rate
        self.tokens = max_rate
        self.last_update = time.time()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        """Acquire permission to proceed (rate limiting)"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_update

            # Add tokens based on time passed
            self.tokens = min(self.max_rate, self.tokens + time_passed * self.max_rate)
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                # Need to wait
                wait_time = (1 - self.tokens) / self.max_rate
                time.sleep(wait_time)
                self.tokens = 0
                return True

class ProgressTracker:
    """Progress tracking utility"""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def update(self, increment: int = 1) -> Dict[str, Union[int, float]]:
        """Update progress and return statistics"""
        with self.lock:
            self.completed += increment

            elapsed = time.time() - self.start_time
            percentage = (self.completed / self.total) * 100 if self.total > 0 else 0

            rate = self.completed / max(elapsed, 0.1)

            eta = (self.total - self.completed) / max(rate, 0.1) if rate > 0 else 0

            return {
                'completed': self.completed,
                'total': self.total,
                'percentage': percentage,
                'elapsed': elapsed,
                'rate': rate,
                'eta': eta
            }

    def get_progress_bar(self, width: int = 50) -> str:
        """Get ASCII progress bar"""
        percentage = (self.completed / self.total) * 100 if self.total > 0 else 0
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"|{bar}| {percentage:.1f}%"

class ConfigUtils:
    """Configuration management utilities"""

    DEFAULT_CONFIG = {
        'scan': {
            'default_ports': '22,80,443,3389,21,23,25,53,110,143,993,995',
            'default_threads': 100,
            'default_timeout': 1.0,
            'default_scan_type': 'fast'
        },
        'ui': {
            'window_geometry': '1000x700',
            'auto_save_results': True,
            'show_progress': True,
            'theme': 'default'
        },
        'output': {
            'default_format': 'txt',
            'include_timestamp': True,
            'verbose_output': False
        }
    }

    @staticmethod
    def load_config(config_file: str = 'mascanner_config.json') -> Dict:
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Merge with defaults
            merged_config = ConfigUtils.DEFAULT_CONFIG.copy()
            for section, values in config.items():
                if section in merged_config:
                    merged_config[section].update(values)
                else:
                    merged_config[section] = values

            return merged_config

        except FileNotFoundError:
            return ConfigUtils.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return ConfigUtils.DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(config: Dict, config_file: str = 'mascanner_config.json') -> bool:
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False

class StatisticsCalculator:
    """Calculate scanning statistics"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all statistics"""
        self.scan_start_time = None
        self.scan_end_time = None
        self.total_targets = 0
        self.total_ports = 0
        self.open_ports = 0
        self.live_hosts = set()
        self.services_found = {}
        self.ports_by_host = {}

    def start_scan(self, total_targets: int, total_ports: int):
        """Initialize scan statistics"""
        self.scan_start_time = time.time()
        self.total_targets = total_targets
        self.total_ports = total_ports

    def end_scan(self):
        """Finalize scan statistics"""
        self.scan_end_time = time.time()

    def add_result(self, result: Dict):
        """Add scan result to statistics"""
        if result['state'] == 'open':
            self.open_ports += 1
            self.live_hosts.add(result['target'])

            # Track services
            service = result['service']
            self.services_found[service] = self.services_found.get(service, 0) + 1

            # Track ports by host
            host = result['target']
            if host not in self.ports_by_host:
                self.ports_by_host[host] = []
            self.ports_by_host[host].append(result['port'])

    def get_statistics(self) -> Dict:
        """Get comprehensive scan statistics"""
        if not self.scan_start_time:
            return {}

        elapsed = time.time() - self.scan_start_time
        if self.scan_end_time:
            elapsed = self.scan_end_time - self.scan_start_time

        total_combinations = self.total_targets * self.total_ports
        scan_rate = total_combinations / max(elapsed, 0.1)

        # Calculate service distribution
        total_services = sum(self.services_found.values())
        service_percentages = {}
        for service, count in self.services_found.items():
            service_percentages[service] = (count / max(total_services, 1)) * 100

        return {
            'timing': {
                'start_time': datetime.fromtimestamp(self.scan_start_time).isoformat(),
                'elapsed_seconds': elapsed,
                'elapsed_formatted': FormatUtils.format_time(elapsed),
                'scan_rate': scan_rate,
                'scan_rate_formatted': FormatUtils.format_rate(scan_rate)
            },
            'targets': {
                'total_targets': self.total_targets,
                'live_hosts': len(self.live_hosts),
                'live_host_percentage': (len(self.live_hosts) / max(self.total_targets, 1)) * 100
            },
            'ports': {
                'total_ports_scanned': self.total_ports,
                'total_combinations': total_combinations,
                'open_ports_found': self.open_ports,
                'open_port_percentage': (self.open_ports / max(total_combinations, 1)) * 100
            },
            'services': {
                'unique_services': len(self.services_found),
                'service_distribution': service_percentages,
                'top_services': sorted(self.services_found.items(), key=lambda x: x[1], reverse=True)[:10]
            },
            'hosts': {
                'hosts_with_open_ports': len(self.ports_by_host),
                'average_ports_per_host': sum(len(ports) for ports in self.ports_by_host.values()) / max(len(self.ports_by_host), 1),
                'most_open_host': max(self.ports_by_host.items(), key=lambda x: len(x[1])) if self.ports_by_host else None
            }
        }

class TargetGenerator:
    """Generate target lists for testing"""

    @staticmethod
    def generate_random_ips(count: int, network: str = "192.168.1.0/24") -> List[str]:
        """Generate random IP addresses within a network"""
        try:
            net = ipaddress.ip_network(network, strict=False)
            hosts = list(net.hosts())

            if count >= len(hosts):
                return [str(ip) for ip in hosts]

            return [str(ip) for ip in random.sample(hosts, count)]
        except Exception:
            return []

    @staticmethod
    def generate_port_ranges(categories: List[str]) -> str:
        """Generate port ranges based on categories"""
        all_ports = []

        for category in categories:
            ports = PortUtils.get_port_category_ports(category)
            all_ports.extend(ports)

        # Remove duplicates and sort
        unique_ports = sorted(list(set(all_ports)))

        # Convert to range format for efficiency
        ranges = []
        start = unique_ports[0] if unique_ports else 1
        end = start

        for port in unique_ports[1:] + [None]:  # Add None to process last range
            if port is None or port != end + 1:
                # End of current range
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")

                if port is not None:
                    start = end = port
            else:
                end = port

        return ','.join(ranges)

class ServiceDetector:
    """Service detection and banner grabbing utilities"""

    # Service detection patterns
    SERVICE_PATTERNS = {
        'ssh': [b'SSH-', b'OpenSSH'],
        'http': [b'HTTP/', b'Server:', b'<html', b'<HTML'],
        'https': [b'HTTP/', b'Server:'],
        'ftp': [b'220', b'FTP', b'vsftpd', b'ProFTPD'],
        'smtp': [b'220', b'SMTP', b'ESMTP'],
        'pop3': [b'+OK', b'POP3'],
        'imap': [b'* OK', b'IMAP'],
        'mysql': [b'mysql_native_password', b'Protocol mismatch'],
        'postgresql': [b'SCRAM-SHA-256', b'unsupported frontend protocol'],
        'redis': [b'-NOAUTH', b'+PONG', b'-ERR'],
        'mongodb': [b'MongoDB', b'version'],
        'vnc': [b'RFB'],
        'rdp': [b'\x03\x00', b'mstshash'],
        'telnet': [b'login:', b'Username:', b'Password:']
    }

    @staticmethod
    def detect_service(host: str, port: int, timeout: float = 2.0) -> Dict[str, str]:
        """Detect service running on a port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Try to get banner
            banner = b''

            # For HTTP services, send GET request
            if port in [80, 443, 8080, 8443]:
                sock.send(b'GET / HTTP/1.0\r\n\r\n')
                banner = sock.recv(1024)
            else:
                # For other services, just receive
                banner = sock.recv(1024)

            sock.close()

            # Detect service based on banner
            banner_str = banner.decode('utf-8', errors='ignore').strip()
            detected_service = ServiceDetector.match_service_pattern(banner)

            return {
                'service': detected_service,
                'banner': banner_str[:200],  # Limit banner length
                'confidence': 'high' if detected_service != 'unknown' else 'low'
            }

        except Exception:
            # Fallback to common port mapping
            service = PortUtils.get_service_name(port)
            return {
                'service': service,
                'banner': '',
                'confidence': 'low' if service == 'unknown' else 'medium'
            }

    @staticmethod
    def match_service_pattern(banner: bytes) -> str:
        """Match banner against known service patterns"""
        banner_lower = banner.lower()

        for service, patterns in ServiceDetector.SERVICE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in banner_lower:
                    return service

        return 'unknown'

class ReportGenerator:
    """Generate comprehensive scan reports"""

    @staticmethod
    def generate_html_report(results: List[Dict], stats: Dict, output_file: str):
        """Generate HTML report with styling and charts"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>MaScanner Scan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .summary { background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .results-table th, .results-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .results-table th { background: #3498db; color: white; }
        .results-table tr:nth-child(even) { background: #f2f2f2; }
        .open-port { color: #27ae60; font-weight: bold; }
        .closed-port { color: #e74c3c; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-box { background: white; border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 MaScanner Scan Report</h1>
        <p>Generated: {timestamp}</p>
    </div>

    <div class="summary">
        <h2>Scan Summary</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number">{total_targets}</div>
                <div>Targets Scanned</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{live_hosts}</div>
                <div>Live Hosts</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{open_ports}</div>
                <div>Open Ports</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{elapsed_time}</div>
                <div>Scan Time</div>
            </div>
        </div>
    </div>

    <div class="results">
        <h2>Detailed Results</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Target</th>
                    <th>Port</th>
                    <th>State</th>
                    <th>Service</th>
                    <th>Protocol</th>
                    <th>Banner</th>
                </tr>
            </thead>
            <tbody>
                {results_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p><em>Report generated by MaScanner v1.0</em></p>
    </div>
</body>
</html>
"""

        try:
            # Generate results rows
            results_rows = ""
            for result in results:
                state_class = "open-port" if result['state'] == 'open' else "closed-port"
                banner = result.get('banner', '')[:100]  # Truncate long banners

                results_rows += f"""
                <tr>
                    <td>{result['target']}</td>
                    <td>{result['port']}</td>
                    <td class="{state_class}">{result['state']}</td>
                    <td>{result['service']}</td>
                    <td>{result.get('protocol', 'tcp')}</td>
                    <td title="{banner}">{banner}</td>
                </tr>
                """

            # Fill template
            html_content = html_template.format(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_targets=stats.get('targets', {}).get('total_targets', 0),
                live_hosts=stats.get('targets', {}).get('live_hosts', 0),
                open_ports=stats.get('ports', {}).get('open_ports_found', 0),
                elapsed_time=stats.get('timing', {}).get('elapsed_formatted', '0s'),
                results_rows=results_rows
            )

            with open(output_file, 'w') as f:
                f.write(html_content)

            return True

        except Exception as e:
            print(f"Error generating HTML report: {str(e)}")
            return False

    @staticmethod
    def generate_summary_report(results: List[Dict], stats: Dict) -> str:
        """Generate text summary report"""
        if not stats:
            return "No statistics available"

        summary = f"""
MaScanner Scan Summary Report
{'=' * 50}

Scan Information:
  Start Time: {stats.get('timing', {}).get('start_time', 'Unknown')}
  Duration: {stats.get('timing', {}).get('elapsed_formatted', 'Unknown')}
  Scan Rate: {stats.get('timing', {}).get('scan_rate_formatted', 'Unknown')}

Target Information:
  Total Targets: {stats.get('targets', {}).get('total_targets', 0):,}
  Live Hosts: {stats.get('targets', {}).get('live_hosts', 0):,}
  Live Host %: {stats.get('targets', {}).get('live_host_percentage', 0):.1f}%

Port Information:
  Ports Scanned: {stats.get('ports', {}).get('total_ports_scanned', 0):,}
  Total Combinations: {stats.get('ports', {}).get('total_combinations', 0):,}
  Open Ports Found: {stats.get('ports', {}).get('open_ports_found', 0):,}
  Success Rate: {stats.get('ports', {}).get('open_port_percentage', 0):.3f}%

Service Information:
  Unique Services: {stats.get('services', {}).get('unique_services', 0)}

Top Services Found:
"""

        # Add top services
        top_services = stats.get('services', {}).get('top_services', [])
        for service, count in top_services[:10]:
            percentage = (count / max(len(results), 1)) * 100
            summary += f"  {service}: {count} ({percentage:.1f}%)\n"

        # Add host information
        host_info = stats.get('hosts', {})
        if host_info.get('most_open_host'):
            most_open_host, port_count = host_info['most_open_host']
            summary += f"\nHost with Most Open Ports:\n  {most_open_host}: {len(port_count)} ports\n"

        return summary

class SecurityUtils:
    """Security-related utilities"""

    @staticmethod
    def check_privileges() -> Dict[str, bool]:
        """Check current user privileges"""
        try:
            # Check if running as admin/root
            if platform.system().lower() == 'windows':
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                is_admin = os.geteuid() == 0

            return {
                'is_admin': is_admin,
                'can_syn_scan': is_admin,
                'can_raw_sockets': is_admin
            }
        except Exception:
            return {
                'is_admin': False,
                'can_syn_scan': False,
                'can_raw_sockets': False
            }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        # Remove path separators and dangerous characters
        safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_chars = re.sub(r'\.\.', '_', safe_chars)  # Remove directory traversal

        # Ensure it's not empty
        if not safe_chars.strip():
            safe_chars = 'output'

        return safe_chars.strip()

    @staticmethod
    def validate_target_safety(target: str) -> Tuple[bool, str]:
        """Validate that target is safe to scan"""
        try:
            # Check if it's a private/local network
            if NetworkUtils.is_valid_ip(target):
                ip_obj = ipaddress.ip_address(target)
                if ip_obj.is_private or ip_obj.is_loopback:
                    return True, "Safe: Private/local IP"
                else:
                    return False, "Warning: Public IP - ensure you have permission"

            elif NetworkUtils.is_valid_network(target):
                network = ipaddress.ip_network(target, strict=False)
                if network.is_private:
                    return True, "Safe: Private network"
                else:
                    return False, "Warning: Public network - ensure you have permission"

            else:
                # Hostname - resolve and check
                ip = NetworkUtils.resolve_hostname(target)
                if ip:
                    return SecurityUtils.validate_target_safety(ip)
                else:
                    return False, "Cannot resolve hostname"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

class BenchmarkUtils:
    """Performance benchmarking utilities"""

    @staticmethod
    def benchmark_scan_performance(scanner, target: str = "127.0.0.1", ports: str = "1-1000") -> Dict:
        """Benchmark scan performance with different configurations"""
        results = {}

        test_configs = [
            {'threads': 50, 'timeout': 1.0},
            {'threads': 100, 'timeout': 1.0},
            {'threads': 200, 'timeout': 1.0},
            {'threads': 100, 'timeout': 0.5},
            {'threads': 100, 'timeout': 2.0}
        ]

        for i, config in enumerate(test_configs):
            print(f"Running benchmark {i+1}/{len(test_configs)}...")

            start_time = time.time()

            # Run scan
            target_list = scanner.expand_targets(target)
            port_list = scanner.parse_port_range(ports)

            scan_results = scanner.start_scan(
                target_list, port_list, 'fast',
                config['threads'], config['timeout']
            )

            elapsed = time.time() - start_time
            rate = (len(target_list) * len(port_list)) / max(elapsed, 0.1)

            results[f"config_{i+1}"] = {
                'threads': config['threads'],
                'timeout': config['timeout'],
                'elapsed_time': elapsed,
                'scan_rate': rate,
                'open_ports': len(scan_results)
            }

        return results

class ExportUtils:
    """Enhanced export utilities"""

    @staticmethod
    def export_to_nmap_xml(results: List[Dict], stats: Dict, filename: str) -> bool:
        """Export results in nmap XML format"""
        try:
            with open(filename, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<!DOCTYPE nmaprun>\n')
                f.write('<?xml-stylesheet href="file:///usr/bin/../share/nmap/nmap.xsl" type="text/xsl"?>\n')
                f.write(f'<nmaprun scanner="mascanner" args="mascanner" start="{int(time.time())}" startstr="{datetime.now().strftime("%c")}" version="1.0" xmloutputversion="1.05">\n')

                # Group results by host
                hosts = {}
                for result in results:
                    host = result['target']
                    if host not in hosts:
                        hosts[host] = []
                    hosts[host].append(result)

                # Write host information
                for host, host_results in hosts.items():
                    f.write(f'<host starttime="{int(time.time())}" endtime="{int(time.time())}">\n')
                    f.write(f'  <status state="up" reason="user-set"/>\n')
                    f.write(f'  <address addr="{host}" addrtype="ipv4"/>\n')
                    f.write(f'  <ports>\n')

                    for result in host_results:
                        state = result['state']
                        port = result['port']
                        service = result['service']
                        protocol = result.get('protocol', 'tcp')

                        f.write(f'    <port protocol="{protocol}" portid="{port}">\n')
                        f.write(f'      <state state="{state}" reason="syn-ack" reason_ttl="0"/>\n')
                        f.write(f'      <service name="{service}" method="table" conf="3"/>\n')
                        f.write(f'    </port>\n')

                    f.write(f'  </ports>\n')
                    f.write(f'</host>\n')

                f.write('</nmaprun>\n')

            return True
        except Exception as e:
            print(f"Error exporting to XML: {str(e)}")
            return False

    @staticmethod
    def export_to_masscan_format(results: List[Dict], filename: str) -> bool:
        """Export results in masscan format"""
        try:
            with open(filename, 'w') as f:
                f.write("# masscan compatible output\n")
                f.write(f"# Generated by MaScanner on {datetime.now().strftime('%c')}\n")

                for result in results:
                    if result['state'] == 'open':
                        timestamp = int(time.time())
                        f.write(f"open tcp {result['port']} {result['target']} {timestamp}\n")

            return True
        except Exception as e:
            print(f"Error exporting to masscan format: {str(e)}")
            return False

# Convenience functions for common operations
def quick_ping(host: str) -> bool:
    """Quick ping function"""
    return ScanUtils.ping_host(host, timeout=1)

def quick_port_check(host: str, port: int) -> bool:
    """Quick port check function"""
    return ScanUtils.check_port_tcp(host, port, timeout=1.0)

def get_common_ports() -> List[int]:
    """Get list of most common ports"""
    return PortUtils.get_port_category_ports('common')

def expand_targets(target_string: str) -> List[str]:
    """Expand target string to list of IPs"""
    targets = []
    for target in target_string.split(','):
        targets.extend(NetworkUtils.expand_ip_range(target.strip()))
    return list(set(targets))  # Remove duplicates

def format_scan_results(results: List[Dict], format_type: str = 'table') -> str:
    """Format scan results for display"""
    if not results:
        return "No results to display"

    if format_type == 'table':
        # Table format
        output = f"{'Target':<15} {'Port':<6} {'State':<8} {'Service':<12} {'Protocol':<8}\n"
        output += "-" * 60 + "\n"

        for result in results:
            output += f"{result['target']:<15} {result['port']:<6} {result['state']:<8} {result['service']:<12} {result.get('protocol', 'tcp'):<8}\n"

        return output

    elif format_type == 'list':
        # List format
        output = ""
        for result in results:
            output += f"{result['target']}:{result['port']} ({result['service']}) - {result['state']}\n"

        return output

    elif format_type == 'grouped':
        # Grouped by host
        hosts = {}
        for result in results:
            host = result['target']
            if host not in hosts:
                hosts[host] = []
            hosts[host].append(result)

        output = ""
        for host, host_results in hosts.items():
            output += f"\n{host}:\n"
            for result in host_results:
                output += f"  {result['port']}/{result.get('protocol', 'tcp')} ({result['service']}) - {result['state']}\n"

        return output

    else:
        return str(results)

# Performance optimization utilities
class PerformanceUtils:
    """Performance optimization utilities"""

    @staticmethod
    def optimize_thread_count(target_count: int, port_count: int) -> int:
        """Calculate optimal thread count based on scan size"""
        total_combinations = target_count * port_count

        if total_combinations < 1000:
            return min(50, total_combinations)
        elif total_combinations < 10000:
            return min(100, total_combinations // 10)
        elif total_combinations < 100000:
            return min(200, total_combinations // 50)
        else:
            return min(500, total_combinations // 200)

    @staticmethod
    def optimize_timeout(scan_type: str, network_type: str = 'local') -> float:
        """Calculate optimal timeout based on scan type and network"""
        base_timeouts = {
            'fast': 1.0,
            'TCP': 2.0,
            'SYN': 1.5,
            'UDP': 2.0
        }

        base_timeout = base_timeouts.get(scan_type, 1.0)

        # Adjust for network type
        if network_type == 'local':
            return base_timeout * 0.5
        elif network_type == 'wan':
            return base_timeout * 2.0
        else:
            return base_timeout

    @staticmethod
    def estimate_scan_time(target_count: int, port_count: int, threads: int, timeout: float) -> float:
        """Estimate scan completion time"""
        total_combinations = target_count * port_count

        # Rough estimate based on timeout and parallelism
        sequential_time = total_combinations * timeout
        parallel_time = sequential_time / threads

        # Add overhead factor
        overhead_factor = 1.2

        return parallel_time * overhead_factor

# Global utility instances for easy access
network_utils = NetworkUtils()
port_utils = PortUtils()
scan_utils = ScanUtils()
format_utils = FormatUtils()
validation_utils = ValidationUtils()

# Module-level convenience functions
def validate_target(target: str) -> bool:
    """Validate a single target"""
    return (NetworkUtils.is_valid_ip(target) or
            NetworkUtils.is_valid_network(target) or
            NetworkUtils.resolve_hostname(target) is not None)

def validate_port(port: Union[int, str]) -> bool:
    """Validate a single port"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False

def get_target_count(target_string: str) -> int:
    """Get total number of targets from target string"""
    return len(expand_targets(target_string))

def get_port_count(port_string: str) -> int:
    """Get total number of ports from port string"""
    return len(PortUtils.parse_port_list(port_string))
