#!/usr/bin/env python3
"""
MaScanner Run Script - Final launcher with comprehensive error handling
"""

import sys
import os
import subprocess
import platform
import time
from pathlib import Path

class MaScannerRunner:
    def __init__(self):
        self.python_cmd = self.detect_python()
        self.project_dir = Path(__file__).parent
        self.missing_deps = []

    def detect_python(self):
        """Detect appropriate Python command"""
        commands = ['python3', 'python', 'py']

        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--version'],
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    version_str = result.stdout.strip()
                    # Extract version number
                    version_parts = version_str.split()[1].split('.')
                    major, minor = int(version_parts[0]), int(version_parts[1])

                    if major >= 3 and minor >= 6:
                        return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError):
                continue

        return None

    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                        MaScanner v1.0                       ║
║                Network Port Scanner Suite                    ║
╚══════════════════════════════════════════════════════════════╝

High-performance network port scanner with GUI and CLI interfaces
Inspired by masscan | Built with Python
        """
        print(banner)

    def check_python(self):
        """Check Python installation"""
        if not self.python_cmd:
            print("❌ Error: Python 3.6+ not found!")
            print("\nInstallation required:")
            if platform.system() == "Windows":
                print("  • Download from: https://python.org/downloads/")
                print("  • Make sure to check 'Add Python to PATH'")
            elif platform.system() == "Darwin":
                print("  • Install with Homebrew: brew install python")
                print("  • Or download from: https://python.org/downloads/")
            else:
                print("  • Ubuntu/Debian: sudo apt-get install python3")
                print("  • CentOS/RHEL: sudo yum install python3")
                print("  • Fedora: sudo dnf install python3")
            return False

        try:
            result = subprocess.run([self.python_cmd, '--version'],
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"✅ Python: {version}")
            return True
        except Exception as e:
            print(f"❌ Python check failed: {e}")
            return False

    def check_nmap(self):
        """Check nmap installation"""
        try:
            result = subprocess.run(['nmap', '--version'],
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ {version_line}")
                return True
            else:
                self.missing_deps.append("nmap")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ nmap: Not installed")
            self.missing_deps.append("nmap")
            return False

    def check_python_nmap(self):
        """Check python-nmap package"""
        try:
            result = subprocess.run([self.python_cmd, '-c', 'import nmap; print(f"python-nmap: {nmap.__version__}")'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {result.stdout.strip()}")
                return True
            else:
                print("❌ python-nmap: Import failed")
                self.missing_deps.append("python-nmap")
                return False
        except Exception:
            print("❌ python-nmap: Not installed")
            self.missing_deps.append("python-nmap")
            return False

    def check_tkinter(self):
        """Check tkinter availability"""
        try:
            result = subprocess.run([self.python_cmd, '-c', 'import tkinter; print("tkinter: Available")'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ tkinter: Available (GUI will work)")
                return True
            else:
                print("❌ tkinter: Not available (GUI will not work)")
                self.missing_deps.append("tkinter")
                return False
        except Exception:
            print("❌ tkinter: Not available")
            self.missing_deps.append("tkinter")
            return False

    def check_files(self):
        """Check required files exist"""
        required_files = [
            'scanner.py', 'main.py', 'gui_advanced.py',
            'launcher.py', 'cli.py', 'utils.py'
        ]

        missing_files = []
        for file in required_files:
            if not (self.project_dir / file).exists():
                missing_files.append(file)

        if missing_files:
            print("❌ Missing files:")
            for file in missing_files:
                print(f"    • {file}")
            return False
        else:
            print("✅ All required files present")
            return True

    def install_python_deps(self):
        """Install Python dependencies"""
        print("\n🔧 Installing Python dependencies...")

        try:
            # Check if pip is available
            pip_cmd = None
            for cmd in ['pip3', 'pip', f'{self.python_cmd} -m pip']:
                try:
                    if cmd.startswith(self.python_cmd):
                        test_cmd = cmd.split()
                    else:
                        test_cmd = [cmd]

                    result = subprocess.run(test_cmd + ['--version'],
                                          capture_output=True, timeout=3)
                    if result.returncode == 0:
                        pip_cmd = cmd
                        break
                except:
                    continue

            if not pip_cmd:
                print("❌ pip not found!")
                return False

            # Install python-nmap
            if 'python-nmap' in self.missing_deps:
                print("  Installing python-nmap...")
                if pip_cmd.startswith(self.python_cmd):
                    install_cmd = pip_cmd.split() + ['install', 'python-nmap']
                else:
                    install_cmd = [pip_cmd, 'install', 'python-nmap']

                result = subprocess.run(install_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("  ✅ python-nmap installed successfully")
                    self.missing_deps.remove("python-nmap")
                else:
                    print(f"  ❌ Failed to install python-nmap: {result.stderr}")
                    return False

            return True

        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False

    def show_installation_help(self):
        """Show installation help for missing dependencies"""
        if not self.missing_deps:
            return

        print("\n📋 Installation Required:")
        print("=" * 50)

        if 'nmap' in self.missing_deps:
            print("\n🔧 Install nmap:")
            system = platform.system()
            if system == "Linux":
                print("  Ubuntu/Debian:  sudo apt-get install nmap")
                print("  CentOS/RHEL:    sudo yum install nmap")
                print("  Fedora:         sudo dnf install nmap")
                print("  Arch:           sudo pacman -S nmap")
            elif system == "Darwin":
                print("  macOS:          brew install nmap")
                print("  Alternative:    sudo port install nmap")
            elif system == "Windows":
                print("  Windows:        Download from https://nmap.org/download.html")
                print("                  Run installer as Administrator")

        if 'python-nmap' in self.missing_deps:
            print("\n🐍 Install python-nmap:")
            print("  pip install python-nmap")
            print("  or")
            print("  pip3 install python-nmap")

        if 'tkinter' in self.missing_deps:
            print("\n🖥️  Install tkinter:")
            system = platform.system()
            if system == "Linux":
                print("  Ubuntu/Debian:  sudo apt-get install python3-tk")
                print("  CentOS/RHEL:    sudo yum install tkinter")
                print("  Fedora:         sudo dnf install python3-tkinter")
            elif system == "Darwin":
                print("  macOS:          brew install python-tk")
            elif system == "Windows":
                print("  Windows:        Usually included with Python")
                print("                  Reinstall Python if missing")

    def launch_interface(self, interface_type, args=None):
        """Launch specified interface"""
        interface_files = {
            'launcher': 'launcher.py',
            'basic': 'main.py',
            'advanced': 'gui_advanced.py',
            'cli': 'cli.py',
            'demo': 'demo.py',
            'test': 'test_basic.py'
        }

        if interface_type not in interface_files:
            print(f"❌ Unknown interface: {interface_type}")
            return False

        file_path = self.project_dir / interface_files[interface_type]
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        try:
            cmd = [self.python_cmd, str(file_path)]
            if args:
                cmd.extend(args)

            print(f"🚀 Starting {interface_type} interface...")
            subprocess.run(cmd, cwd=self.project_dir)
            return True

        except KeyboardInterrupt:
            print("\n⏹️  Interface stopped by user")
            return True
        except Exception as e:
            print(f"❌ Failed to start {interface_type}: {e}")
            return False

    def run_dependency_check(self):
        """Run comprehensive dependency check"""
        print("🔍 Checking Dependencies:")
        print("-" * 30)

        checks = [
            ("Python 3.6+", self.check_python),
            ("nmap binary", self.check_nmap),
            ("python-nmap", self.check_python_nmap),
            ("tkinter (GUI)", self.check_tkinter),
            ("Required files", self.check_files)
        ]

        all_passed = True
        for check_name, check_func in checks:
            print(f"\n{check_name}:")
            if not check_func():
                all_passed = False

        return all_passed

    def auto_install(self):
        """Attempt automatic installation"""
        print("\n🔧 Attempting automatic installation...")

        if 'python-nmap' in self.missing_deps:
            if not self.install_python_deps():
                return False

        # Re-check after installation
        self.missing_deps = []
        if self.check_python_nmap():
            print("✅ Installation successful!")
            return True
        else:
            print("❌ Installation incomplete")
            return False

    def interactive_menu(self):
        """Show interactive menu for interface selection"""
        print("\n📋 Select Interface:")
        print("-" * 20)
        print("1. 🎛️  GUI Launcher (Recommended)")
        print("2. 🔍 Basic GUI")
        print("3. ⚡ Advanced GUI")
        print("4. 💻 Command Line")
        print("5. 🎮 Interactive Demo")
        print("6. 🧪 Basic Network Test")
        print("7. ❓ Show Help")
        print("8. ❌ Exit")

        while True:
            try:
                choice = input("\nEnter choice (1-8): ").strip()

                if choice == '1':
                    return self.launch_interface('launcher')
                elif choice == '2':
                    return self.launch_interface('basic')
                elif choice == '3':
                    return self.launch_interface('advanced')
                elif choice == '4':
                    args = input("CLI arguments (or press Enter for help): ").strip().split()
                    if not args:
                        args = ['--help']
                    return self.launch_interface('cli', args)
                elif choice == '5':
                    return self.launch_interface('demo')
                elif choice == '6':
                    return self.launch_interface('test')
                elif choice == '7':
                    self.show_help()
                    continue
                elif choice == '8':
                    print("👋 Goodbye!")
                    return True
                else:
                    print("❌ Invalid choice. Please enter 1-8.")
                    continue

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return True
            except EOFError:
                print("\n👋 Goodbye!")
                return True

    def show_help(self):
        """Show help information"""
        help_text = """
📖 MaScanner Help
================

INTERFACES:
  GUI Launcher    - Choose between Basic and Advanced GUI
  Basic GUI       - Simple interface for quick scans
  Advanced GUI    - Feature-rich interface with tabs and statistics
  Command Line    - Full CLI for automation and scripting
  Demo            - Interactive demonstration of features
  Basic Test      - Test core functionality

QUICK START:
  1. Install dependencies: Choose option 6 first, then auto-install
  2. Run demo: Choose option 5 to see features
  3. Start scanning: Choose option 1 for GUI launcher

EXAMPLE SCANS:
  • Local network: 192.168.1.0/24
  • Single host: 192.168.1.1
  • Port range: 1-1000
  • Common ports: 22,80,443,3389

SECURITY NOTICE:
⚠️  Only scan networks you own or have explicit permission to test!
Unauthorized network scanning may violate laws and policies.

For detailed documentation, see README.md and USAGE.md
        """
        print(help_text)

    def run(self):
        """Main run function"""
        try:
            self.print_banner()

            # Parse command line arguments
            if len(sys.argv) > 1:
                mode = sys.argv[1].lower()

                if mode in ['--help', '-h', 'help']:
                    self.show_help()
                    return 0
                elif mode in ['--version', '-v', 'version']:
                    print("MaScanner v1.0.0")
                    return 0
                elif mode == '--check':
                    if self.run_dependency_check():
                        print("\n✅ All dependencies satisfied!")
                        return 0
                    else:
                        print("\n❌ Missing dependencies found")
                        self.show_installation_help()
                        return 1
                elif mode == '--install':
                    if not self.run_dependency_check():
                        return 1 if not self.auto_install() else 0
                    else:
                        print("✅ All dependencies already satisfied!")
                        return 0
                elif mode in ['gui', 'launcher']:
                    if not self.run_dependency_check():
                        print("\n❌ Dependencies missing. Run with --install first.")
                        return 1
                    return 0 if self.launch_interface('launcher') else 1
                elif mode in ['basic']:
                    if not self.run_dependency_check():
                        print("\n❌ Dependencies missing. Run with --install first.")
                        return 1
                    return 0 if self.launch_interface('basic') else 1
                elif mode in ['advanced']:
                    if not self.run_dependency_check():
                        print("\n❌ Dependencies missing. Run with --install first.")
                        return 1
                    return 0 if self.launch_interface('advanced') else 1
                elif mode in ['cli']:
                    if not self.run_dependency_check():
                        print("\n❌ Dependencies missing. Run with --install first.")
                        return 1
                    return 0 if self.launch_interface('cli', sys.argv[2:]) else 1
                elif mode in ['demo']:
                    # Demo can run with basic dependencies
                    if not self.python_cmd:
                        print("❌ Python required for demo")
                        return 1
                    return 0 if self.launch_interface('demo') else 1
                elif mode in ['test', 'check-basic']:
                    # Basic test requires only Python
                    if not self.python_cmd:
                        print("❌ Python required for testing")
                        return 1
                    return 0 if self.launch_interface('test') else 1
                else:
                    print(f"❌ Unknown mode: {mode}")
                    self.show_help()
                    return 1

            # No arguments - run interactive mode
            print("🔍 Checking system...")

            # Quick dependency check
            deps_ok = self.run_dependency_check()

            if not deps_ok:
                print(f"\n⚠️  Found {len(self.missing_deps)} missing dependencies")
                self.show_installation_help()

                if 'python-nmap' in self.missing_deps and 'nmap' not in self.missing_deps:
                    print(f"\n🤖 Auto-install python-nmap?")
                    try:
                        response = input("Install now? (y/N): ").lower()
                        if response == 'y':
                            if self.auto_install():
                                deps_ok = True
                            else:
                                print("❌ Auto-installation failed")
                    except (KeyboardInterrupt, EOFError):
                        pass

                if not deps_ok:
                    print(f"\n⚡ You can still run the basic network test or demo")

            # Show interactive menu
            return 0 if self.interactive_menu() else 1

        except KeyboardInterrupt:
            print("\n\n👋 Startup interrupted. Goodbye!")
            return 0
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Try running with --help for usage information")
            return 1

def main():
    """Main entry point"""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    runner = MaScannerRunner()
    return runner.run()

if __name__ == "__main__":
    sys.exit(main())
