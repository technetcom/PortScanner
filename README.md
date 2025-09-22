# MaScanner - Network Port Scanner GUI

A high-performance network port scanner with a graphical user interface, inspired by masscan. MaScanner provides fast, concurrent port scanning capabilities with an intuitive GUI built using Python and tkinter.

## Features

- **Fast Concurrent Scanning**: Multi-threaded port scanning for high performance
- **Multiple Target Formats**: Support for single IPs, IP ranges, CIDR notation, and hostnames
- **Flexible Port Specification**: Individual ports, ranges, and comma-separated lists
- **Multiple Scan Types**: Fast TCP connect, SYN scan, UDP scan, and ping sweep
- **Real-time Results**: Live updating results table during scan
- **Export Functionality**: Export results to TXT, CSV, or JSON formats
- **Customizable Settings**: Adjustable thread count and timeout values
- **Progress Tracking**: Visual progress bar and status updates
- **Cross-platform**: Works on Windows, Linux, and macOS

## Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│ MaScanner - Network Port Scanner                            │
├─────────────────────────────────────────────────────────────┤
│ Target(s): [192.168.1.1-254                              ] │
│ Port(s):   [22,80,443,3389,21,23,25,53,110,143,993,995   ] │
│ Scan Type: [fast                                         ▼] │
│                                                             │
│ ┌─ Advanced Options ─────────────────────────────────────┐  │
│ │ Threads: [100] Timeout (s): [1.0]                     │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                             │
│ [Start Scan] [Stop Scan] [Clear Results]                   │
│ ████████████████████████████████████████████ 100%          │
│                                                             │
│ ┌─ Scan Results ─────────────────────────────────────────┐  │
│ │ Target      │ Port │ State │ Service │ Protocol        │  │
│ │ 192.168.1.1 │ 22   │ open  │ ssh     │ tcp            │  │
│ │ 192.168.1.1 │ 80   │ open  │ http    │ tcp            │  │
│ │ 192.168.1.5 │ 443  │ open  │ https   │ tcp            │  │
│ └───────────────────────────────────────────────────────┘  │
│ Status: Scan completed. Found 3 open ports.  Results: 3    │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.6 or higher
- nmap installed on your system

#### Installing nmap

**Ubuntu/Debian:**
```bash
sudo apt-get install nmap
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install nmap  # or dnf install nmap
```

**macOS:**
```bash
brew install nmap
```

**Windows:**
Download and install from: https://nmap.org/download.html

### Install Python Dependencies

1. Clone or download this repository
2. Navigate to the project directory
3. Install required Python packages:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install python-nmap
```

Note: `tkinter` is included with most Python installations by default.

## Usage

### Running the Application

```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Target Specification

MaScanner supports various target formats:

- **Single IP**: `192.168.1.1`
- **IP Range**: `192.168.1.1-254`
- **CIDR Notation**: `192.168.1.0/24`
- **Hostname**: `example.com`
- **Multiple Targets**: `192.168.1.1,192.168.1.5,example.com`

### Port Specification

- **Single Port**: `80`
- **Port Range**: `1-1000`
- **Multiple Ports**: `22,80,443,3389`
- **Mixed**: `22,80-90,443,8000-8080`

### Scan Types

1. **Fast**: High-speed TCP connect scan (default)
2. **SYN**: TCP SYN scan (requires root/admin privileges)
3. **TCP**: Full TCP connect scan
4. **UDP**: UDP port scan
5. **PING**: Ping sweep only (no port scanning)

### Advanced Options

- **Threads**: Number of concurrent scanning threads (1-1000)
- **Timeout**: Connection timeout in seconds (0.1-10.0)

## GUI Controls

### Main Interface

- **Target(s)**: Enter target IPs, ranges, or hostnames
- **Port(s)**: Specify ports to scan
- **Scan Type**: Choose scanning method
- **Start Scan**: Begin the scanning process
- **Stop Scan**: Halt current scan
- **Clear Results**: Remove all results from the table

### Menu Options

**File Menu:**
- Export Results: Save results to file (TXT, CSV, JSON)
- Exit: Close application

**Tools Menu:**
- Ping Sweep: Check which hosts are alive
- Clear Results: Remove all scan results

**Help Menu:**
- About: Show application information

## Example Usage Scenarios

### Basic Network Discovery

1. Set target to your network range: `192.168.1.0/24`
2. Use common ports: `22,80,443,3389`
3. Select "fast" scan type
4. Click "Start Scan"

### Comprehensive Port Scan

1. Set target to specific host: `192.168.1.100`
2. Scan all ports: `1-65535`
3. Adjust threads to `200` for faster scanning
4. Select "TCP" scan type for more reliable results

### Service Discovery

1. First run a ping sweep to find live hosts
2. Then scan common service ports: `21,22,23,25,53,80,110,143,443,993,995,3389`
3. Use "SYN" scan for stealth (requires admin privileges)

## Export Formats

### Text Format
```
MaScanner Scan Results
Generated: 2024-01-15 14:30:22
============================================================

Target: 192.168.1.1
Port: 22
State: open
Service: ssh
Protocol: tcp
----------------------------------------
```

### CSV Format
```
Target,Port,State,Service,Protocol
192.168.1.1,22,open,ssh,tcp
192.168.1.1,80,open,http,tcp
```

### JSON Format
```json
{
  "scan_info": {
    "timestamp": "2024-01-15T14:30:22",
    "tool": "MaScanner",
    "total_results": 2
  },
  "results": [
    {
      "target": "192.168.1.1",
      "port": 22,
      "state": "open",
      "service": "ssh",
      "protocol": "tcp"
    }
  ]
}
```

## Performance Tips

1. **Adjust Thread Count**: Increase threads for faster scanning, but be mindful of system resources
2. **Use Appropriate Timeouts**: Lower timeouts for faster scans, higher for more reliable results
3. **Target Specific Ports**: Scanning fewer ports will complete faster
4. **Use SYN Scans**: For better performance on large networks (requires admin privileges)

## Troubleshooting

### Common Issues

**Permission Denied (SYN Scans)**
- SYN scans require administrator/root privileges
- Run with `sudo python main.py` on Linux/macOS
- Run as Administrator on Windows

**Nmap Not Found**
- Ensure nmap is installed and in your system PATH
- Try running `nmap --version` in terminal to verify installation

**Slow Scanning**
- Reduce thread count if experiencing high CPU usage
- Increase timeout for unreliable networks
- Use "fast" scan type for maximum speed

**No Results**
- Verify targets are reachable (try ping sweep first)
- Check firewall settings on target systems
- Ensure correct port specification

### Error Messages

- **"Invalid target"**: Check IP address format or hostname spelling
- **"No valid ports"**: Verify port range syntax
- **"Connection timeout"**: Increase timeout value or check network connectivity

## Technical Details

### Architecture

- **Frontend**: tkinter GUI with threaded scanning to prevent freezing
- **Backend**: python-nmap wrapper with custom fast scanning engine
- **Concurrency**: ThreadPoolExecutor for parallel port scanning
- **Networking**: Raw socket connections for fast TCP scanning

### Dependencies

- `python-nmap`: Python wrapper for nmap
- `tkinter`: GUI framework (usually included with Python)
- `threading`: Concurrent execution
- `ipaddress`: IP address validation and manipulation
- `socket`: Network socket operations

## Security Considerations

- This tool is intended for network administration and security testing
- Only scan networks and systems you own or have explicit permission to test
- Some scan types may trigger intrusion detection systems
- Use responsibly and in accordance with local laws and regulations

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- Feature enhancements
- Documentation improvements
- Performance optimizations

## License

This project is released under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is for educational and administrative purposes only. Users are responsible for ensuring they have proper authorization before scanning any networks or systems. The authors are not responsible for any misuse of this software.

## Changelog

### v1.0.0
- Initial release
- Basic GUI interface
- Fast TCP scanning
- Multiple target formats
- Export functionality
- Ping sweep capability
- Progress tracking