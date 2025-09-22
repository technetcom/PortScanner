# MaScanner Quick Start Guide

## 🚀 Get Started in 5 Minutes

MaScanner is a high-performance network port scanner with GUI and CLI interfaces, inspired by masscan. This guide will get you up and running quickly.

## ⚡ Super Quick Start

```bash
# 1. Download/clone MaScanner
cd mascanner/

# 2. Run basic test (works without dependencies)
python3 test_basic.py

# 3. Install dependencies (if needed)
python3 start.py --install

# 4. Start GUI
python3 start.py gui
```

## 📦 What's Included

### Core Files
- **`main.py`** - Basic GUI interface (simple and fast)
- **`gui_advanced.py`** - Advanced GUI with tabs and statistics
- **`launcher.py`** - GUI launcher to choose interface
- **`cli.py`** - Full command-line interface
- **`scanner.py`** - Core scanning engine
- **`utils.py`** - Utility functions and helpers

### Launchers & Tools
- **`start.py`** - Main startup script with dependency checking
- **`run.py`** - Enhanced launcher with error handling
- **`demo.py`** - Interactive feature demonstration
- **`demo_simple.py`** - Demo without external dependencies
- **`gui_test.py`** - Simple GUI test
- **`test_basic.py`** - Basic network functionality test

### Setup & Documentation
- **`install.sh`** - Automated installation script (Linux/macOS)
- **`setup.py`** - Python package setup
- **`Makefile`** - Build automation
- **`requirements.txt`** - Python dependencies
- **`README.md`** - Complete documentation
- **`USAGE.md`** - Detailed usage guide

## 🎯 Choose Your Interface

### 1. GUI Launcher (Recommended for Beginners)
```bash
python3 launcher.py
```
**Features:** Choose between Basic and Advanced GUI, system check, help

### 2. Basic GUI (Simple & Fast)
```bash
python3 main.py
```
**Features:** Clean interface, quick scans, basic export, real-time progress

### 3. Advanced GUI (Power Users)
```bash
python3 gui_advanced.py
```
**Features:** Tabs, statistics, logging, filtering, grouping, advanced export

### 4. Command Line (Automation)
```bash
python3 cli.py --help
```
**Features:** Scriptable, batch processing, multiple output formats

## 📋 Prerequisites Check

### Required
- **Python 3.6+** (check: `python3 --version`)
- **nmap binary** (check: `nmap --version`)
- **python-nmap** (auto-installed: `pip install python-nmap`)

### Quick Check
```bash
python3 start.py --check
```

## 🔧 Installation Options

### Option 1: Automated (Recommended)
```bash
# Linux/macOS
./install.sh

# Any platform
python3 start.py --install
```

### Option 2: Manual
```bash
# 1. Install nmap binary
sudo apt-get install nmap        # Ubuntu/Debian
sudo yum install nmap            # CentOS/RHEL
brew install nmap                # macOS
# Windows: Download from https://nmap.org/

# 2. Install Python package
pip3 install python-nmap
```

### Option 3: Test Without Dependencies
```bash
# Basic functionality test (no nmap needed)
python3 test_basic.py

# Simple GUI test (no nmap needed)
python3 gui_test.py

# Simple demo (no nmap needed)
python3 demo_simple.py
```

## 🎮 Quick Examples

### Example 1: Scan Local Network
```bash
# GUI: 
#   Target: 192.168.1.0/24
#   Ports: 22,80,443
#   Click "Start Scan"

# CLI:
python3 cli.py 192.168.1.0/24 -p 22,80,443
```

### Example 2: Quick Host Check
```bash
# GUI:
#   Target: 192.168.1.1
#   Ports: 22,80,443,3389
#   Scan Type: Fast

# CLI:
python3 cli.py 192.168.1.1 -p 22,80,443,3389 --scan-type fast
```

### Example 3: Web Server Discovery
```bash
# GUI:
#   Target: 192.168.1.1-254
#   Ports: 80,443,8080,8443
#   Threads: 100

# CLI:
python3 cli.py 192.168.1.1-254 -p 80,443,8080,8443 --threads 100
```

### Example 4: Ping Sweep
```bash
# GUI: Tools → Ping Sweep
# CLI:
python3 cli.py 192.168.1.0/24 --ping-sweep
```

## 🔍 Testing Your Installation

### 1. Basic Test
```bash
python3 test_basic.py
```
Expected output: All tests should pass

### 2. Demo Run
```bash
python3 demo_simple.py
```
Choose demo option to see features

### 3. GUI Test
```bash
python3 gui_test.py
```
Simple GUI should open and work

### 4. CLI Test
```bash
python3 cli.py 127.0.0.1 -p 22,80 --timeout 0.5
```
Should scan localhost and show results

## 📖 Common Commands

### All-in-One Launcher
```bash
python3 start.py                 # Interactive menu
python3 start.py gui             # GUI launcher
python3 start.py basic           # Basic GUI
python3 start.py advanced        # Advanced GUI
python3 start.py cli --help      # CLI help
python3 start.py demo            # Interactive demo
python3 start.py test            # Basic test
```

### Direct Launches
```bash
python3 launcher.py              # GUI launcher
python3 main.py                  # Basic GUI
python3 gui_advanced.py          # Advanced GUI
python3 cli.py --help            # CLI help
```

### Utility Commands
```bash
python3 start.py --check         # Check dependencies
python3 start.py --install       # Install dependencies
python3 start.py --version       # Show version
python3 demo.py                  # Full interactive demo
python3 tests.py                 # Run test suite
```

## 🏃‍♂️ Scan Examples by Use Case

### Network Discovery
```bash
# Find live hosts first
python3 cli.py 192.168.1.0/24 --ping-sweep

# Then scan common ports
python3 cli.py 192.168.1.1-254 -p 22,80,443,3389
```

### Web Security Audit
```bash
# Scan web-related ports
python3 cli.py target -p 80,443,8000-8080,9000-9090
```

### Database Discovery
```bash
# Scan database ports
python3 cli.py target -p 1433,3306,5432,6379,27017
```

### Comprehensive Scan
```bash
# Full port range (requires admin for SYN)
python3 cli.py target -p 1-65535 --scan-type SYN --threads 300
```

## ⚠️ Important Notes

### Security & Legal
- **Only scan networks you own** or have explicit permission to test
- **Unauthorized scanning** may violate laws and policies
- **Get written permission** for penetration testing
- **Follow responsible disclosure** for any vulnerabilities found

### Performance Tips
- **Start with ping sweep** to find live hosts
- **Use appropriate thread counts** (50-200 for most cases)
- **Adjust timeouts** based on network speed
- **Monitor system resources** during large scans

### Privilege Requirements
- **Fast/TCP scans**: No special privileges needed
- **SYN scans**: Require administrator/root privileges
- **UDP scans**: Require administrator/root privileges

## 🆘 Need Help?

### Quick Fixes
```bash
# Dependencies missing?
python3 start.py --install

# GUI not working?
python3 test_basic.py

# Want to see features?
python3 demo_simple.py
```

### Documentation
- **README.md** - Complete documentation
- **USAGE.md** - Detailed usage guide
- **PROJECT_OVERVIEW.md** - Technical overview
- **Built-in help** - Use --help with any command

### Common Issues
1. **"nmap not found"** → Install nmap binary for your OS
2. **"python-nmap import error"** → Run `pip install python-nmap`
3. **"Permission denied"** → Use `sudo` for SYN/UDP scans or choose "fast" scan
4. **"tkinter not available"** → Install python3-tk package
5. **"Slow scanning"** → Reduce threads or increase timeout

## 🎉 Success!

If you can run any of these commands successfully, MaScanner is working:

```bash
✅ python3 test_basic.py         # Basic test passed
✅ python3 gui_test.py           # GUI opens and works  
✅ python3 cli.py 127.0.0.1 -p 80 # CLI scan works
✅ python3 start.py gui          # Full GUI launcher works
```

## 🚀 Ready to Scan!

You're now ready to use MaScanner! Here are some next steps:

1. **Learn the interfaces** - Try both Basic and Advanced GUI
2. **Read the docs** - Check out README.md for comprehensive guide
3. **Try examples** - Use the provided scan examples
4. **Explore features** - Run the interactive demo
5. **Go advanced** - Learn CLI for automation

**Happy scanning! 🎯**

---

*MaScanner v1.0 - High-performance network port scanner*  
*Use responsibly and only on authorized networks*