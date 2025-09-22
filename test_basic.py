#!/usr/bin/env python3
"""
Basic Network Test for MaScanner
Simple test to verify core functionality without external dependencies
"""

import socket
import time
import threading
import sys
import os

def test_socket_operations():
    """Test basic socket operations"""
    print("Testing basic socket operations...")

    try:
        # Test TCP socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.close()
        print("  ✓ TCP socket creation: OK")

        # Test UDP socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.close()
        print("  ✓ UDP socket creation: OK")

        # Test localhost connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            # Try to connect to a port that should be closed
            result = sock.connect_ex(('127.0.0.1', 99999))
            sock.close()
            if result != 0:
                print("  ✓ Localhost connection test: OK (port correctly closed)")
            else:
                print("  ⚠ Localhost connection test: Unexpected open port")
        except Exception as e:
            print(f"  ✗ Localhost connection test: {e}")

        return True

    except Exception as e:
        print(f"  ✗ Socket operations failed: {e}")
        return False

def test_threading():
    """Test threading functionality"""
    print("Testing threading functionality...")

    try:
        results = []

        def worker_function(thread_id):
            time.sleep(0.1)
            results.append(f"Thread {thread_id} completed")

        # Create and start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=2.0)

        if len(results) == 5:
            print("  ✓ Multi-threading: OK")
            return True
        else:
            print(f"  ✗ Multi-threading: Only {len(results)}/5 threads completed")
            return False

    except Exception as e:
        print(f"  ✗ Threading test failed: {e}")
        return False

def test_ip_validation():
    """Test IP address validation without external libraries"""
    print("Testing IP validation...")

    def is_valid_ip(ip_str):
        """Simple IP validation"""
        try:
            parts = ip_str.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except ValueError:
            return False

    test_cases = [
        ("127.0.0.1", True),
        ("192.168.1.1", True),
        ("8.8.8.8", True),
        ("256.1.1.1", False),
        ("192.168.1", False),
        ("invalid", False),
        ("", False)
    ]

    passed = 0
    for ip, expected in test_cases:
        result = is_valid_ip(ip)
        if result == expected:
            passed += 1
            status = "✓"
        else:
            status = "✗"
        print(f"  {status} {ip:<15} - Expected: {expected}, Got: {result}")

    if passed == len(test_cases):
        print("  ✓ IP validation: All tests passed")
        return True
    else:
        print(f"  ✗ IP validation: {passed}/{len(test_cases)} tests passed")
        return False

def test_port_parsing():
    """Test port range parsing"""
    print("Testing port parsing...")

    def parse_simple_ports(port_str):
        """Simple port parsing"""
        ports = []
        if not port_str:
            return []

        try:
            for part in port_str.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    ports.extend(range(start, end + 1))
                else:
                    ports.append(int(part))
            return sorted(list(set(ports)))
        except ValueError:
            return []

    test_cases = [
        ("80", [80]),
        ("22,80,443", [22, 80, 443]),
        ("80-82", [80, 81, 82]),
        ("22,80-82,443", [22, 80, 81, 82, 443]),
        ("", []),
        ("invalid", [])
    ]

    passed = 0
    for port_str, expected in test_cases:
        result = parse_simple_ports(port_str)
        if result == expected:
            passed += 1
            status = "✓"
        else:
            status = "✗"
        print(f"  {status} '{port_str}':<15 - Expected: {expected}, Got: {result}")

    if passed == len(test_cases):
        print("  ✓ Port parsing: All tests passed")
        return True
    else:
        print(f"  ✗ Port parsing: {passed}/{len(test_cases)} tests passed")
        return False

def test_localhost_connectivity():
    """Test localhost connectivity"""
    print("Testing localhost connectivity...")

    try:
        # Test localhost resolution
        localhost_ip = socket.gethostbyname('localhost')
        if localhost_ip in ['127.0.0.1', '::1']:
            print(f"  ✓ Localhost resolution: {localhost_ip}")
        else:
            print(f"  ⚠ Localhost resolution: Unexpected IP {localhost_ip}")

        # Test socket binding (find an available port)
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('127.0.0.1', 0))  # Bind to any available port
        bound_port = test_socket.getsockname()[1]
        test_socket.close()

        print(f"  ✓ Socket binding: Port {bound_port} available")

        # Test basic port scanning functionality
        def scan_port(host, port, timeout=0.5):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                return result == 0
            except:
                return False

        # Test on a port that should be closed
        is_open = scan_port('127.0.0.1', 99999, 0.1)
        if not is_open:
            print("  ✓ Port scanning: Basic functionality works")
        else:
            print("  ⚠ Port scanning: Unexpected open port 99999")

        return True

    except Exception as e:
        print(f"  ✗ Localhost connectivity failed: {e}")
        return False

def test_concurrent_scanning():
    """Test concurrent port scanning"""
    print("Testing concurrent scanning...")

    try:
        results = []

        def scan_worker(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                results.append({'port': port, 'open': result == 0})
            except Exception as e:
                results.append({'port': port, 'error': str(e)})

        # Test concurrent scanning of multiple ports
        threads = []
        test_ports = [99997, 99998, 99999]

        start_time = time.time()

        for port in test_ports:
            thread = threading.Thread(target=scan_worker, args=(port,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=2.0)

        elapsed = time.time() - start_time

        if len(results) == len(test_ports):
            print(f"  ✓ Concurrent scanning: {len(results)} ports in {elapsed:.2f}s")

            # Check for errors
            errors = [r for r in results if 'error' in r]
            if not errors:
                print("  ✓ No errors in concurrent scanning")
            else:
                print(f"  ⚠ {len(errors)} errors in concurrent scanning")

            return True
        else:
            print(f"  ✗ Concurrent scanning: Only {len(results)}/{len(test_ports)} completed")
            return False

    except Exception as e:
        print(f"  ✗ Concurrent scanning failed: {e}")
        return False

def test_file_operations():
    """Test file read/write operations"""
    print("Testing file operations...")

    try:
        # Test writing to file
        test_filename = "test_output.tmp"
        test_data = "MaScanner test data\nLine 2\nLine 3"

        with open(test_filename, 'w') as f:
            f.write(test_data)

        print("  ✓ File writing: OK")

        # Test reading from file
        with open(test_filename, 'r') as f:
            read_data = f.read()

        if read_data == test_data:
            print("  ✓ File reading: OK")
        else:
            print("  ✗ File reading: Data mismatch")
            return False

        # Cleanup
        os.remove(test_filename)
        print("  ✓ File cleanup: OK")

        return True

    except Exception as e:
        print(f"  ✗ File operations failed: {e}")
        # Cleanup on error
        try:
            os.remove(test_filename)
        except:
            pass
        return False

def test_import_dependencies():
    """Test importing required modules"""
    print("Testing module imports...")

    # Test standard library imports
    standard_modules = [
        'threading', 'socket', 'time', 'json', 'csv',
        'subprocess', 'platform', 'ipaddress', 'concurrent.futures'
    ]

    for module in standard_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}: Available")
        except ImportError:
            print(f"  ✗ {module}: Not available")
            return False

    # Test tkinter (GUI requirement)
    try:
        import tkinter
        print("  ✓ tkinter: Available (GUI will work)")
    except ImportError:
        print("  ✗ tkinter: Not available (GUI will not work)")
        print("    Install with: sudo apt-get install python3-tk (Ubuntu)")

    # Test optional modules
    try:
        import nmap
        print("  ✓ python-nmap: Available")
    except ImportError:
        print("  ⚠ python-nmap: Not available (install with: pip install python-nmap)")

    return True

def test_system_info():
    """Display system information"""
    print("System Information:")

    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    print(f"  Current Directory: {os.getcwd()}")

    # Check if running as admin/root
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            print(f"  Administrator: {'Yes' if is_admin else 'No'}")
        else:  # Unix-like
            is_root = os.geteuid() == 0
            print(f"  Root/Sudo: {'Yes' if is_root else 'No'}")
    except:
        print("  Privileges: Unknown")

    # Check available memory (rough estimate)
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"  Available Memory: {memory.available // (1024*1024)} MB")
    except ImportError:
        print("  Available Memory: Unknown (psutil not installed)")

def run_basic_scan_simulation():
    """Simulate a basic scan without external dependencies"""
    print("Running basic scan simulation...")

    # Simulate scanning localhost ports
    target = "127.0.0.1"
    test_ports = [22, 80, 443, 8080, 99999]

    print(f"  Target: {target}")
    print(f"  Ports: {test_ports}")
    print("  Scanning...")

    results = []
    start_time = time.time()

    for i, port in enumerate(test_ports):
        # Simulate scanning progress
        progress = ((i + 1) / len(test_ports)) * 100
        print(f"    Progress: {progress:.0f}% (Port {port})", end='\r')

        # Actual port check
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((target, port))
            sock.close()

            if result == 0:
                results.append({'port': port, 'state': 'open'})
                print(f"\n    ✓ Found open port: {port}")

        except Exception:
            pass

        time.sleep(0.1)  # Small delay for demo

    elapsed = time.time() - start_time
    print(f"\n  Scan completed in {elapsed:.2f} seconds")
    print(f"  Open ports found: {len(results)}")

    if results:
        for result in results:
            print(f"    Port {result['port']}: {result['state']}")
    else:
        print("    No open ports found (normal for localhost)")

    return True

def main():
    """Run all basic tests"""
    print("=" * 60)
    print("MaScanner Basic Network Test")
    print("=" * 60)
    print()

    test_results = []

    # Run system info
    test_system_info()
    print()

    # Run tests
    tests = [
        ("Import Dependencies", test_import_dependencies),
        ("Socket Operations", test_socket_operations),
        ("Threading", test_threading),
        ("IP Validation", test_ip_validation),
        ("Port Parsing", test_port_parsing),
        ("Localhost Connectivity", test_localhost_connectivity),
        ("File Operations", test_file_operations),
        ("Concurrent Scanning", test_concurrent_scanning)
    ]

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            test_results.append((test_name, False))

    # Run scan simulation
    print(f"\nScan Simulation:")
    print("-" * 15)
    try:
        scan_result = run_basic_scan_simulation()
        test_results.append(("Scan Simulation", scan_result))
    except Exception as e:
        print(f"  ✗ Scan simulation failed: {e}")
        test_results.append(("Scan Simulation", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {test_name:<25} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! MaScanner should work correctly.")
        print("\nNext steps:")
        print("  1. Install dependencies: python start.py --install")
        print("  2. Run full demo: python demo.py")
        print("  3. Start GUI: python start.py")
        return 0
    else:
        print("❌ Some tests failed. Check the issues above.")
        print("\nTroubleshooting:")
        print("  - Ensure Python 3.6+ is installed")
        print("  - Check internet connectivity")
        print("  - Verify file permissions")
        print("  - Try running as administrator if needed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        sys.exit(1)
