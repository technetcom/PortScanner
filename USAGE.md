# MaScanner Usage Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [User Interfaces](#user-interfaces)
4. [Target Specification](#target-specification)
5. [Port Specification](#port-specification)
6. [Scan Types](#scan-types)
7. [Advanced Features](#advanced-features)
8. [Export Options](#export-options)
9. [Performance Tuning](#performance-tuning)
10. [Security Considerations](#security-considerations)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)

## Quick Start

### 1. Install Dependencies
```bash
# Auto-install (recommended)
python start.py --install

# Manual install
pip install python-nmap
# Install nmap binary for your OS (see Installation section)
```

### 2. Launch MaScanner
```bash
# GUI Launcher (recommended for beginners)
python start.py

# Direct launches
python launcher.py     # GUI launcher
python main.py         # Basic GUI
python gui_advanced.py # Advanced GUI
python cli.py --help   # Command line help
```

### 3. Quick Scan Example
```bash
# GUI: Enter "192.168.1.1-254" as target, "22,80,443" as ports, click Start
# CLI: python cli.py 192.168.1.1-254 -p 22,80,443
```

## Installation

### Prerequisites

- **Python 3.6+** (required)
- **nmap binary** (required)
- **python-nmap package** (auto-installed)

### Automated Installation

The easiest way to install MaScanner:

```bash
# Clone or download MaScanner
cd mascanner/

# Run automated installer
./install.sh
# or
python start.py --install
```

### Manual Installation

#### 1. Install nmap binary

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install nmap
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install nmap
# or for newer versions:
sudo dnf install nmap
```

**macOS:**
```bash
# Using Homebrew
brew install nmap

# Using MacPorts
sudo port install nmap
```

**Windows:**
- Download from: https://nmap.org/download.html
- Run installer as Administrator
- Add nmap to PATH

#### 2. Install Python dependencies

```bash
pip install python-nmap
# or
pip install -r requirements.txt
```

#### 3. Verify Installation

```bash
python start.py --check
```

## User Interfaces

MaScanner provides three different interfaces:

### 1. GUI Launcher
**File:** `launcher.py`
**Command:** `python launcher.py`

- Choose between Basic and Advanced GUI
- System requirements check
- Dependency installation help
- About information

### 2. Basic GUI
**File:** `main.py`
**Command:** `python main.py`

**Features:**
- Simple, clean interface
- Target and port input fields
- Scan type selection
- Real-time progress tracking
- Results table with sorting
- Export to TXT, CSV, JSON
- Ping sweep functionality

**Best for:** Quick scans, beginners, lightweight usage

### 3. Advanced GUI
**File:** `gui_advanced.py`
**Command:** `python gui_advanced.py`

**Features:**
- Tabbed interface (Config, Results, Statistics, Log)
- Advanced filtering and search
- Grouping by host/service
- Real-time statistics
- Comprehensive logging
- Multiple export formats
- Performance optimization tools
- Port presets and quick actions

**Best for:** Professional use, detailed analysis, complex scans

### 4. Command Line Interface
**File:** `cli.py`
**Command:** `python cli.py [options] targets`

**Features:**
- Full command-line control
- Scriptable and automatable
- Multiple output formats
- Batch processing
- Integration with other tools

**Best for:** Automation, scripting, CI/CD integration

## Target Specification

### Supported Formats

| Format | Example | Description |
|--------|---------|-------------|
| Single IP | `192.168.1.1` | Scan single host |
| IP Range | `192.168.1.1-254` | Scan IP range |
| CIDR Notation | `192.168.1.0/24` | Scan entire subnet |
| Hostname | `example.com` | Resolve and scan hostname |
| Multiple Targets | `192.168.1.1,192.168.1.5,example.com` | Comma-separated list |
| File Input | `-iL targets.txt` (CLI only) | Load targets from file |

### Examples

```bash
# Single host
192.168.1.100

# Small range
192.168.1.1-10

# Entire subnet
10.0.0.0/24

# Mixed targets
192.168.1.1,10.0.0.1-5,example.com

# Large range
172.16.0.0/16
```

### Target File Format

For CLI file input (`-iL targets.txt`):

```
# Target list for MaScanner
# Lines starting with # are comments

192.168.1.1
192.168.1.10-20
10.0.0.0/24
example.com
scanme.nmap.org
```

## Port Specification

### Supported Formats

| Format | Example | Description |
|--------|---------|-------------|
| Single Port | `80` | Scan single port |
| Port Range | `1-1000` | Scan port range |
| Multiple Ports | `22,80,443` | Comma-separated list |
| Mixed Format | `22,80-90,443,8000-8080` | Combination of above |

### Port Presets

**GUI Presets (Advanced interface):**
- **Top 100**: Most common 100 ports
- **Top 1000**: Most common 1000 ports
- **Web Ports**: HTTP/HTTPS related ports
- **Database**: Database service ports
- **Mail**: Email service ports
- **Remote**: Remote access ports
- **All Ports**: Complete range 1-65535

**CLI Examples:**
```bash
# Common ports
python cli.py target -p 22,80,443,3389

# Web servers
python cli.py target -p 80,443,8080,8443

# Database ports
python cli.py target -p 1433,3306,5432,6379,27017

# Top 100 ports
python cli.py target --top-ports 100

# All ports (large scan)
python cli.py target -p 1-65535
```

## Scan Types

### 1. Fast Scan (default)
- **Method:** TCP connect scan
- **Speed:** Very fast
- **Stealth:** Low (connections logged)
- **Privileges:** None required
- **Best for:** Quick discovery, internal networks

```bash
# GUI: Select "fast" from dropdown
# CLI: python cli.py target -p ports --scan-type fast
```

### 2. SYN Scan
- **Method:** TCP SYN packets
- **Speed:** Fast
- **Stealth:** High (half-open connections)
- **Privileges:** Administrator/root required
- **Best for:** Stealth scanning, external networks

```bash
# GUI: Select "SYN" from dropdown
# CLI: python cli.py target -p ports --scan-type SYN
```

### 3. TCP Connect Scan
- **Method:** Full TCP connection
- **Speed:** Medium
- **Stealth:** Low (full connections)
- **Privileges:** None required
- **Best for:** Reliable results, firewalled networks

```bash
# GUI: Select "TCP" from dropdown
# CLI: python cli.py target -p ports --scan-type TCP
```

### 4. UDP Scan
- **Method:** UDP packets
- **Speed:** Slow
- **Stealth:** Medium
- **Privileges:** Administrator/root required
- **Best for:** UDP service discovery

```bash
# GUI: Select "UDP" from dropdown
# CLI: python cli.py target -p ports --scan-type UDP
```

### 5. Ping Sweep
- **Method:** ICMP ping
- **Speed:** Fast
- **Purpose:** Host discovery only
- **Best for:** Finding live hosts before port scanning

```bash
# GUI: Tools → Ping Sweep
# CLI: python cli.py target --ping-sweep
```

## Advanced Features

### 1. Performance Tuning

#### Thread Count
- **Default:** 100 threads
- **Range:** 1-1000 threads
- **Recommendation:** 
  - Local networks: 100-200 threads
  - Internet scans: 50-100 threads
  - Slow networks: 20-50 threads

#### Timeout Settings
- **Default:** 1.0 seconds
- **Range:** 0.1-10.0 seconds
- **Recommendation:**
  - Local networks: 0.5-1.0 seconds
  - Internet scans: 2.0-3.0 seconds
  - Slow networks: 3.0-5.0 seconds

#### Rate Limiting
- **Purpose:** Prevent network congestion
- **Default:** 1000 packets/second
- **Recommendation:** Adjust based on network capacity

### 2. Service Detection

MaScanner automatically detects services on open ports:

- **Banner Grabbing:** Attempts to retrieve service banners
- **Service Fingerprinting:** Matches responses to known services
- **Version Detection:** Identifies service versions when possible

### 3. Results Filtering and Grouping

**Advanced GUI Features:**
- **Search:** Filter results by IP, port, or service
- **Group by Host:** Organize results by target host
- **Group by Service:** Organize results by service type
- **State Filtering:** Show only open, closed, or filtered ports

### 4. Real-time Statistics

**Track during scans:**
- Elapsed time
- Scan progress percentage
- Targets scanned
- Open ports found
- Live hosts discovered
- Scan rate (ports/second)

## Export Options

### Supported Formats

#### 1. Text Format (.txt)
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

#### 2. CSV Format (.csv)
```csv
Target,Port,State,Service,Protocol
192.168.1.1,22,open,ssh,tcp
192.168.1.1,80,open,http,tcp
```

#### 3. JSON Format (.json)
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

#### 4. XML Format (.xml)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<scanresults>
  <scaninfo tool="MaScanner" version="1.0" timestamp="2024-01-15T14:30:22"/>
  <host addr="192.168.1.1">
    <port portid="22" protocol="tcp">
      <state state="open"/>
      <service name="ssh"/>
    </port>
  </host>
</scanresults>
```

### Export Commands

**GUI:**
- File → Export Results
- Choose format and location

**CLI:**
```bash
python cli.py target -p ports -oN results.txt    # Text format
python cli.py target -p ports -oC results.csv    # CSV format
python cli.py target -p ports -oJ results.json   # JSON format
python cli.py target -p ports -oX results.xml    # XML format
```

## Performance Tuning

### Optimization Guidelines

#### For Speed
```bash
# Maximum speed configuration
Threads: 200-500
Timeout: 0.3-0.5 seconds
Scan Type: Fast or SYN
Rate Limit: 2000+ packets/sec
```

#### For Reliability
```bash
# Maximum reliability configuration
Threads: 50-100
Timeout: 2.0-3.0 seconds
Scan Type: TCP Connect
Rate Limit: 500-1000 packets/sec
```

#### For Stealth
```bash
# Stealth configuration
Threads: 20-50
Timeout: 1.0-2.0 seconds
Scan Type: SYN
Rate Limit: 100-500 packets/sec
Randomize: Enabled
```

### Performance Factors

1. **Network Latency:** Higher latency requires longer timeouts
2. **Network Bandwidth:** More bandwidth allows higher rate limits
3. **Target Load:** Busy targets may need longer timeouts
4. **Firewall Rules:** May affect optimal scan timing
5. **System Resources:** CPU and memory limit thread count

### Optimization Tips

1. **Start with ping sweep** to identify live hosts
2. **Use SYN scans** for better performance (requires admin)
3. **Adjust thread count** based on target count
4. **Use port presets** instead of full port ranges
5. **Monitor system resources** during large scans

## Security Considerations

### Legal and Ethical Use

⚠️ **IMPORTANT:** Only scan networks you own or have explicit permission to test.

#### Authorized Use Cases:
- ✅ Your own networks and systems
- ✅ Penetration testing with written permission
- ✅ Security audits with proper authorization
- ✅ Educational use in controlled environments

#### Prohibited Use:
- ❌ Scanning networks without permission
- ❌ Unauthorized security testing
- ❌ Malicious network reconnaissance
- ❌ Violating terms of service

### Technical Security

#### Scan Detection
- **IDS/IPS Systems:** May detect scanning patterns
- **Firewall Logs:** Connection attempts are logged
- **Rate Limiting:** Prevent overwhelming targets
- **Timing Variations:** Avoid predictable patterns

#### Privacy Protection
- **No Data Collection:** MaScanner doesn't send data externally
- **Local Processing:** All scanning is performed locally
- **Secure Storage:** Results stored locally only

### Best Practices

1. **Get Permission:** Always obtain written authorization
2. **Start Small:** Begin with limited scans
3. **Monitor Impact:** Watch for performance degradation
4. **Document Scans:** Keep records of authorized testing
5. **Follow Disclosure:** Report vulnerabilities responsibly

## Troubleshooting

### Common Issues

#### 1. "nmap not found"
**Problem:** nmap binary not installed or not in PATH

**Solutions:**
```bash
# Check if nmap is installed
nmap --version

# Install nmap (Ubuntu/Debian)
sudo apt-get install nmap

# Install nmap (macOS)
brew install nmap

# Windows: Download from https://nmap.org/download.html
```

#### 2. "python-nmap import error"
**Problem:** python-nmap package not installed

**Solutions:**
```bash
# Install python-nmap
pip install python-nmap

# Or use requirements file
pip install -r requirements.txt

# Check installation
python -c "import nmap; print('OK')"
```

#### 3. "Permission denied" (SYN scans)
**Problem:** SYN scans require administrator privileges

**Solutions:**
```bash
# Linux/macOS: Run with sudo
sudo python main.py

# Windows: Run as Administrator
# Right-click → "Run as Administrator"

# Alternative: Use TCP connect scan instead
# (Select "TCP" or "fast" scan type)
```

#### 4. GUI won't start
**Problem:** tkinter not available

**Solutions:**
```bash
# Ubuntu/Debian: Install tkinter
sudo apt-get install python3-tk

# CentOS/RHEL: Install tkinter
sudo yum install tkinter

# macOS: Reinstall Python with tkinter support
brew install python-tk
```

#### 5. Slow scanning
**Problem:** Scans taking too long

**Solutions:**
- Reduce thread count (try 50-100)
- Decrease timeout (try 0.5-1.0 seconds)
- Use "fast" or "SYN" scan types
- Scan fewer ports or targets
- Check network connectivity

#### 6. No results found
**Problem:** Scan completes but finds no open ports

**Solutions:**
- Verify targets are reachable (use ping sweep)
- Check if ports are actually open
- Try different scan types
- Increase timeout for slow networks
- Verify firewall settings

### Debugging Steps

1. **Check Dependencies:**
   ```bash
   python start.py --check
   ```

2. **Test Basic Functionality:**
   ```bash
   python demo.py --quick
   ```

3. **Run Full Demo:**
   ```bash
   python demo.py
   ```

4. **Test Specific Component:**
   ```bash
   python -c "from scanner import PortScanner; s=PortScanner(); print('Scanner OK')"
   ```

5. **Enable Verbose Logging:**
   ```bash
   python cli.py target -p ports --verbose
   ```

## Examples

### Basic Examples

#### 1. Simple Host Scan
```bash
# GUI: Target="192.168.1.100", Ports="22,80,443"
# CLI:
python cli.py 192.168.1.100 -p 22,80,443
```

#### 2. Network Discovery
```bash
# GUI: Target="192.168.1.0/24", Use ping sweep first
# CLI:
python cli.py 192.168.1.0/24 --ping-sweep
```

#### 3. Web Server Detection
```bash
# GUI: Target="192.168.1.1-254", Ports preset="Web Ports"
# CLI:
python cli.py 192.168.1.1-254 -p 80,443,8080,8443
```

### Advanced Examples

#### 1. Comprehensive Network Audit
```bash
# Step 1: Find live hosts
python cli.py 192.168.1.0/24 --ping-sweep -oN live_hosts.txt

# Step 2: Scan common ports on live hosts
python cli.py -iL live_hosts.txt -p 1-1000 --threads 200 -oJ results.json

# Step 3: Full scan on interesting hosts
python cli.py 192.168.1.100 -p 1-65535 --scan-type SYN -oX full_scan.xml
```

#### 2. Service-Specific Scans
```bash
# Web services
python cli.py targets -p 80,443,8000-8080 --threads 100

# Database services
python cli.py targets -p 1433,3306,5432,6379,27017

# Remote access services
python cli.py targets -p 22,23,3389,5900-5910
```

#### 3. Stealth Scanning
```bash
# Low-profile scan
python cli.py target -p 1-1000 --scan-type SYN --threads 20 --timeout 2.0 -T1
```

#### 4. High-Speed Scanning
```bash
# Maximum speed scan
python cli.py target -p 1-1000 --scan-type fast --threads 500 --timeout 0.3 -T5
```

### Automation Examples

#### 1. Scheduled Network Monitoring
```bash
#!/bin/bash
# daily_scan.sh - Daily network monitoring script

DATE=$(date +%Y%m%d)
python cli.py 192.168.1.0/24 --ping-sweep -oN "live_hosts_$DATE.txt"
python cli.py -iL "live_hosts_$DATE.txt" -p 22,80,443 -oJ "scan_results_$DATE.json"
```

#### 2. Continuous Monitoring
```bash
#!/bin/bash
# monitor_critical_hosts.sh

CRITICAL_HOSTS="192.168.1.10,192.168.1.20,192.168.1.30"
CRITICAL_PORTS="22,80,443,3389"

while true; do
    echo "$(date): Scanning critical infrastructure..."
    python cli.py $CRITICAL_HOSTS -p $CRITICAL_PORTS -oC "monitoring_$(date +%H%M).csv"
    sleep 300  # Wait 5 minutes
done
```

#### 3. CI/CD Integration
```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Install dependencies
      run: |
        sudo apt-get install nmap
        pip install python-nmap
    - name: Scan staging environment
      run: |
        python cli.py staging-server.example.com -p 80,443,22 -oJ security-scan.json
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: security-scan-results
        path: security-scan.json
```

## FAQ

### Q: How does MaScanner compare to masscan?
A: MaScanner is inspired by masscan and offers similar high-speed scanning with these differences:
- **GUI Interface:** User-friendly graphical interface
- **Python-based:** More accessible and customizable
- **Cross-platform:** Works on Windows, Linux, macOS
- **Integrated Tools:** Built-in export, statistics, and analysis

### Q: Can I scan the entire internet?
A: Technically possible but **not recommended**:
- **Legal Issues:** Unauthorized scanning may violate laws
- **Resource Intensive:** Requires significant bandwidth and time
- **Detection Risk:** Likely to be detected and blocked
- **Ethical Concerns:** May impact network performance

### Q: Why do I need administrator privileges for some scans?
A: SYN and UDP scans require raw socket access, which needs administrator privileges for security reasons.

### Q: How accurate are the results?
A: Accuracy depends on:
- **Network conditions:** Latency, packet loss
- **Firewall configuration:** May block or filter scans
- **Target system load:** Busy systems may drop connections
- **Scan parameters:** Timeout and retry settings

### Q: Can I scan IPv6 addresses?
A: Current version supports IPv4 only. IPv6 support is planned for future releases.

### Q: How do I report bugs or request features?
A: Please check the project repository for issue tracking and contribution guidelines.

## Command Reference

### GUI Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Start Scan |
| Ctrl+T | Stop Scan |
| Ctrl+E | Export Results |
| Ctrl+L | Load Targets |
| Ctrl+C | Clear Results |
| F5 | Refresh View |
| F1 | Show Help |
| Escape | Stop Current Scan |

### CLI Commands

#### Basic Syntax
```bash
python cli.py [TARGETS] [OPTIONS]
```

#### Common Options
| Option | Description |
|--------|-------------|
| `-p, --ports` | Port specification |
| `-sT, --scan-type` | Scan type (fast, SYN, TCP, UDP) |
| `--threads` | Number of scanning threads |
| `--timeout` | Connection timeout |
| `-oN` | Output to text file |
| `-oJ` | Output to JSON file |
| `-oC` | Output to CSV file |
| `-oX` | Output to XML file |
| `--ping-sweep` | Ping sweep only |
| `--top-ports N` | Scan top N ports |
| `-v, --verbose` | Verbose output |
| `-q, --quiet` | Quiet mode |

## Performance Benchmarks

### Typical Performance

**Local Network (1ms latency):**
- Fast scan: 1000-5000 ports/second
- SYN scan: 800-3000 ports/second
- TCP scan: 500-2000 ports/second

**Internet (50ms latency):**
- Fast scan: 200-1000 ports/second
- SYN scan: 100-500 ports/second
- TCP scan: 50-200 ports/second

**Factors Affecting Performance:**
- Network latency and bandwidth
- Target system responsiveness
- Firewall and filtering
- System resources (CPU, memory)
- Thread count and timeout settings

### Benchmark Command
```bash
# Run performance benchmark
python -c "
from utils import BenchmarkUtils
from scanner import PortScanner
scanner = PortScanner()
results = BenchmarkUtils.benchmark_scan_performance(scanner)
for config, stats in results.items():
    print(f'{config}: {stats[\"scan_rate\"]:.0f} ports/sec')
"
```

---

**Last Updated:** 2024-01-15
**Version:** 1.0.0
**For support, see README.md or project documentation**