#!/usr/bin/env python3
"""
MaScanner Startup Script - Easy launcher for all interfaces
"""

import sys
import os
import argparse
import subprocess
import tkinter as tk
from tkinter import messagebox
import time

def check_dependencies():
    """Check if all required dependencies are available"""
    missing = []

    # Check Python modules
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter (usually included with Python)")

    try:
        import nmap
    except ImportError:
        missing.append("python-nmap (install with: pip install python-nmap)")

    # Check nmap binary
    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, timeout=3)
        if result.returncode != 0:
            missing.append("nmap binary")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        missing.append("nmap binary (install from https://nmap.org/)")

    return missing

def install_dependencies():
    """Install missing Python dependencies"""
    try:
        print("Installing python-nmap...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-nmap'],
                      check=True, capture_output=True)
        print("✓ python-nmap installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install python-nmap: {e}")
        return False
    except Exception as e:
        print(f"✗ Installation error: {e}")
        return False

def show_help():
    """Show help information"""
    help_text = """
MaScanner - Network Port Scanner

Usage: python start.py [OPTIONS] [MODE]

MODES:
    gui         Start GUI launcher (default)
    basic       Start basic GUI interface
    advanced    Start advanced GUI interface
    cli         Start command-line interface
    demo        Run interactive demo
    test        Run test suite

OPTIONS:
    --install   Install missing dependencies
    --check     Check dependencies only
    --help      Show this help message
    --version   Show version information

EXAMPLES:
    python start.py                    # Start GUI launcher
    python start.py basic              # Start basic GUI
    python start.py advanced           # Start advanced GUI
    python start.py cli --help         # Show CLI help
    python start.py demo               # Run demo
    python start.py --install          # Install dependencies

QUICK START:
    1. python start.py --install       # Install dependencies
    2. python start.py                 # Start GUI

For detailed usage, see README.md
"""
    print(help_text)

def show_version():
    """Show version information"""
    print("MaScanner v1.0.0")
    print("Network Port Scanner with GUI")
    print("Inspired by masscan, built with Python")
    print()
    print(f"Python: {sys.version.split()[0]}")

    try:
        import nmap
        print(f"python-nmap: {nmap.__version__}")
    except:
        print("python-nmap: Not installed")

    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"nmap: {version_line}")
        else:
            print("nmap: Not found")
    except:
        print("nmap: Not installed")

def launch_gui():
    """Launch GUI launcher"""
    try:
        if os.path.exists('launcher.py'):
            subprocess.run([sys.executable, 'launcher.py'])
        else:
            print("launcher.py not found, trying basic GUI...")
            launch_basic_gui()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return False
    return True

def launch_basic_gui():
    """Launch basic GUI interface"""
    try:
        if os.path.exists('main.py'):
            subprocess.run([sys.executable, 'main.py'])
        else:
            print("Error: main.py not found")
            return False
    except Exception as e:
        print(f"Error launching basic GUI: {e}")
        return False
    return True

def launch_advanced_gui():
    """Launch advanced GUI interface"""
    try:
        if os.path.exists('gui_advanced.py'):
            subprocess.run([sys.executable, 'gui_advanced.py'])
        else:
            print("Error: gui_advanced.py not found")
            return False
    except Exception as e:
        print(f"Error launching advanced GUI: {e}")
        return False
    return True

def launch_cli(args):
    """Launch CLI interface"""
    try:
        if os.path.exists('cli.py'):
            cmd = [sys.executable, 'cli.py'] + args
            subprocess.run(cmd)
        else:
            print("Error: cli.py not found")
            return False
    except Exception as e:
        print(f"Error launching CLI: {e}")
        return False
    return True

def launch_demo():
    """Launch interactive demo"""
    try:
        if os.path.exists('demo.py'):
            subprocess.run([sys.executable, 'demo.py'])
        else:
            print("Error: demo.py not found")
            return False
    except Exception as e:
        print(f"Error launching demo: {e}")
        return False
    return True

def run_tests():
    """Run test suite"""
    try:
        if os.path.exists('tests.py'):
            subprocess.run([sys.executable, 'tests.py'])
        else:
            print("Error: tests.py not found")
            return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False
    return True

def main():
    """Main startup function"""
    # Print banner
    print("""
    ███╗   ███╗ █████╗ ███████╗ ██████╗ █████╗ ███╗   ███╗███╗   ██╗███████╗██████╗
    ████╗ ████║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗ ████║████╗  ██║██╔════╝██╔══██╗
    ██╔████╔██║███████║███████╗██║     ███████║██╔████╔██║██╔██╗ ██║█████╗  ██████╔╝
    ██║╚██╔╝██║██╔══██║╚════██║██║     ██╔══██║██║╚██╔╝██║██║╚██╗██║██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║██║  ██║███████║╚██████╗██║  ██║██║ ╚═╝ ██║██║ ╚████║███████╗██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝

    MaScanner v1.0 - Network Port Scanner
    """)

    # Parse arguments
    parser = argparse.ArgumentParser(description='MaScanner Startup Script', add_help=False)
    parser.add_argument('mode', nargs='?', default='gui',
                       choices=['gui', 'basic', 'advanced', 'cli', 'demo', 'test'],
                       help='Interface mode (default: gui)')
    parser.add_argument('--install', action='store_true', help='Install dependencies')
    parser.add_argument('--check', action='store_true', help='Check dependencies')
    parser.add_argument('--help', action='store_true', help='Show help')
    parser.add_argument('--version', action='store_true', help='Show version')

    # Parse known args to handle CLI passthrough
    args, unknown_args = parser.parse_known_args()

    # Handle special options
    if args.help:
        show_help()
        return 0

    if args.version:
        show_version()
        return 0

    if args.check:
        print("Checking dependencies...")
        missing = check_dependencies()
        if missing:
            print("Missing dependencies:")
            for dep in missing:
                print(f"  ✗ {dep}")
            return 1
        else:
            print("✓ All dependencies available")
            return 0

    if args.install:
        print("Installing dependencies...")
        missing = check_dependencies()

        if 'python-nmap' in ' '.join(missing):
            if install_dependencies():
                print("✓ Dependencies installed successfully")
            else:
                print("✗ Dependency installation failed")
                return 1

        # Check for nmap binary
        if any('nmap' in dep for dep in missing):
            print("\nNmap binary installation required:")
            print("  Ubuntu/Debian: sudo apt-get install nmap")
            print("  CentOS/RHEL:   sudo yum install nmap")
            print("  macOS:         brew install nmap")
            print("  Windows:       Download from https://nmap.org/download.html")

        return 0

    # Check dependencies before launching
    missing = check_dependencies()
    if missing:
        print("⚠️  Missing dependencies detected:")
        for dep in missing:
            print(f"   ✗ {dep}")
        print()
        print("Run 'python start.py --install' to install Python dependencies")
        print("For nmap installation, see: https://nmap.org/download.html")
        print()

        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return 1

    # Launch appropriate interface
    success = False

    if args.mode == 'gui':
        print("🚀 Starting GUI launcher...")
        success = launch_gui()
    elif args.mode == 'basic':
        print("🚀 Starting basic GUI...")
        success = launch_basic_gui()
    elif args.mode == 'advanced':
        print("🚀 Starting advanced GUI...")
        success = launch_advanced_gui()
    elif args.mode == 'cli':
        print("🚀 Starting CLI interface...")
        success = launch_cli(unknown_args)
    elif args.mode == 'demo':
        print("🚀 Starting interactive demo...")
        success = launch_demo()
    elif args.mode == 'test':
        print("🚀 Running test suite...")
        success = run_tests()

    if not success:
        print("\n❌ Failed to start MaScanner")
        print("Try running with --check to verify dependencies")
        return 1

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nStartup interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
