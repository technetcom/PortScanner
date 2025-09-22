#!/usr/bin/env python3
"""
MaScanner Tests - Comprehensive test suite for all modules
"""

import unittest
import threading
import time
import socket
import tempfile
import os
import json
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import PortScanner
from utils import (
    NetworkUtils, PortUtils, ScanUtils, FormatUtils,
    ValidationUtils, SecurityUtils, StatisticsCalculator
)

class TestNetworkUtils(unittest.TestCase):
    """Test NetworkUtils class"""

    def test_is_valid_ip(self):
        """Test IP address validation"""
        self.assertTrue(NetworkUtils.is_valid_ip("192.168.1.1"))
        self.assertTrue(NetworkUtils.is_valid_ip("127.0.0.1"))
        self.assertTrue(NetworkUtils.is_valid_ip("8.8.8.8"))
        self.assertFalse(NetworkUtils.is_valid_ip("192.168.1.256"))
        self.assertFalse(NetworkUtils.is_valid_ip("invalid"))
        self.assertFalse(NetworkUtils.is_valid_ip(""))

    def test_is_valid_network(self):
        """Test network validation"""
        self.assertTrue(NetworkUtils.is_valid_network("192.168.1.0/24"))
        self.assertTrue(NetworkUtils.is_valid_network("10.0.0.0/8"))
        self.assertFalse(NetworkUtils.is_valid_network("192.168.1.0/33"))
        self.assertFalse(NetworkUtils.is_valid_network("invalid/24"))

    def test_expand_ip_range(self):
        """Test IP range expansion"""
        # CIDR notation
        result = NetworkUtils.expand_ip_range("192.168.1.0/30")
        self.assertEqual(len(result), 2)  # Host addresses only
        self.assertIn("192.168.1.1", result)
        self.assertIn("192.168.1.2", result)

        # Range notation
        result = NetworkUtils.expand_ip_range("192.168.1.1-3")
        self.assertEqual(len(result), 3)
        self.assertIn("192.168.1.1", result)
        self.assertIn("192.168.1.2", result)
        self.assertIn("192.168.1.3", result)

        # Single IP
        result = NetworkUtils.expand_ip_range("192.168.1.1")
        self.assertEqual(result, ["192.168.1.1"])

    def test_get_local_ip(self):
        """Test local IP detection"""
        local_ip = NetworkUtils.get_local_ip()
        self.assertTrue(NetworkUtils.is_valid_ip(local_ip))

    def test_is_private_ip(self):
        """Test private IP detection"""
        self.assertTrue(NetworkUtils.is_private_ip("192.168.1.1"))
        self.assertTrue(NetworkUtils.is_private_ip("10.0.0.1"))
        self.assertTrue(NetworkUtils.is_private_ip("172.16.0.1"))
        self.assertFalse(NetworkUtils.is_private_ip("8.8.8.8"))
        self.assertFalse(NetworkUtils.is_private_ip("1.1.1.1"))

    def test_get_network_info(self):
        """Test network information retrieval"""
        info = NetworkUtils.get_network_info("192.168.1.1")
        self.assertEqual(info['ip'], "192.168.1.1")
        self.assertEqual(info['version'], "IPv4")
        self.assertEqual(info['is_private'], "True")

        # Test invalid IP
        info = NetworkUtils.get_network_info("invalid")
        self.assertIn('error', info)

class TestPortUtils(unittest.TestCase):
    """Test PortUtils class"""

    def test_get_service_name(self):
        """Test service name lookup"""
        self.assertEqual(PortUtils.get_service_name(80), "http")
        self.assertEqual(PortUtils.get_service_name(443), "https")
        self.assertEqual(PortUtils.get_service_name(22), "ssh")
        self.assertEqual(PortUtils.get_service_name(99999), "unknown")

    def test_parse_port_list(self):
        """Test port list parsing"""
        # Single port
        result = PortUtils.parse_port_list("80")
        self.assertEqual(result, [80])

        # Multiple ports
        result = PortUtils.parse_port_list("80,443,22")
        self.assertEqual(sorted(result), [22, 80, 443])

        # Port range
        result = PortUtils.parse_port_list("80-82")
        self.assertEqual(result, [80, 81, 82])

        # Mixed format
        result = PortUtils.parse_port_list("22,80-82,443")
        self.assertEqual(sorted(result), [22, 80, 81, 82, 443])

        # Empty string
        result = PortUtils.parse_port_list("")
        self.assertEqual(result, [])

        # Invalid ranges should be ignored
        result = PortUtils.parse_port_list("80,invalid,443")
        self.assertEqual(sorted(result), [80, 443])

    def test_get_port_info(self):
        """Test port information retrieval"""
        info = PortUtils.get_port_info(80)
        self.assertEqual(info['port'], 80)
        self.assertEqual(info['service'], 'http')
        self.assertEqual(info['protocol'], 'tcp')
        self.assertIn('category', info)

    def test_get_port_category_ports(self):
        """Test port category retrieval"""
        web_ports = PortUtils.get_port_category_ports('web')
        self.assertIn(80, web_ports)
        self.assertIn(443, web_ports)

        # Non-existent category
        empty_ports = PortUtils.get_port_category_ports('nonexistent')
        self.assertEqual(empty_ports, [])

class TestScanUtils(unittest.TestCase):
    """Test ScanUtils class"""

    def test_check_port_tcp_localhost(self):
        """Test TCP port checking on localhost"""
        # Test a port that's likely to be closed
        result = ScanUtils.check_port_tcp("127.0.0.1", 99999, timeout=0.1)
        self.assertFalse(result)

        # Test invalid host
        result = ScanUtils.check_port_tcp("999.999.999.999", 80, timeout=0.1)
        self.assertFalse(result)

    def test_ping_host(self):
        """Test host ping functionality"""
        # Test localhost (should always work)
        result = ScanUtils.ping_host("127.0.0.1", timeout=1)
        self.assertTrue(result)

        # Test invalid host
        result = ScanUtils.ping_host("999.999.999.999", timeout=1)
        self.assertFalse(result)

    def test_get_banner(self):
        """Test banner grabbing"""
        # This test might be unreliable, so we'll just test the function exists
        banner = ScanUtils.get_banner("127.0.0.1", 99999, timeout=0.1)
        # Banner should be None for closed port
        self.assertIsNone(banner)

class TestPortScanner(unittest.TestCase):
    """Test PortScanner class"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    def test_validate_target(self):
        """Test target validation"""
        self.assertTrue(self.scanner.validate_target("192.168.1.1"))
        self.assertTrue(self.scanner.validate_target("127.0.0.1"))
        self.assertTrue(self.scanner.validate_target("192.168.1.0/24"))
        self.assertTrue(self.scanner.validate_target("192.168.1.1-10"))
        self.assertFalse(self.scanner.validate_target(""))
        self.assertFalse(self.scanner.validate_target("invalid"))

    def test_parse_port_range(self):
        """Test port range parsing"""
        # Single port
        result = self.scanner.parse_port_range("80")
        self.assertEqual(result, [80])

        # Range
        result = self.scanner.parse_port_range("80-82")
        self.assertEqual(result, [80, 81, 82])

        # Multiple ports
        result = self.scanner.parse_port_range("22,80,443")
        self.assertEqual(sorted(result), [22, 80, 443])

        # Empty should return default range
        result = self.scanner.parse_port_range("")
        self.assertGreater(len(result), 0)

    def test_expand_targets(self):
        """Test target expansion"""
        # Single IP
        result = self.scanner.expand_targets("192.168.1.1")
        self.assertEqual(result, ["192.168.1.1"])

        # Multiple IPs
        result = self.scanner.expand_targets("192.168.1.1,192.168.1.2")
        self.assertEqual(sorted(result), ["192.168.1.1", "192.168.1.2"])

        # IP range
        result = self.scanner.expand_targets("192.168.1.1-3")
        expected = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
        self.assertEqual(sorted(result), sorted(expected))

    def test_get_service_name(self):
        """Test service name retrieval"""
        self.assertEqual(self.scanner.get_service_name(80), "http")
        self.assertEqual(self.scanner.get_service_name(443), "https")
        self.assertEqual(self.scanner.get_service_name(99999), "unknown")

    def test_scan_port(self):
        """Test single port scanning"""
        # Test on a port that should be closed
        result = self.scanner.scan_port("127.0.0.1", 99999, timeout=0.1)
        self.assertIsNone(result)

    def test_stop_scan(self):
        """Test scan stopping functionality"""
        self.scanner.is_scanning = True
        self.scanner.stop_scan()
        self.assertFalse(self.scanner.is_scanning)

    def test_get_results(self):
        """Test results retrieval"""
        results = self.scanner.get_results()
        self.assertIsInstance(results, list)

class TestFormatUtils(unittest.TestCase):
    """Test FormatUtils class"""

    def test_format_time(self):
        """Test time formatting"""
        self.assertEqual(FormatUtils.format_time(30), "30.0s")
        self.assertEqual(FormatUtils.format_time(90), "1m 30s")
        self.assertEqual(FormatUtils.format_time(3661), "1h 1m 1s")

    def test_format_size(self):
        """Test size formatting"""
        self.assertEqual(FormatUtils.format_size(1024), "1.0 KB")
        self.assertEqual(FormatUtils.format_size(1048576), "1.0 MB")
        self.assertEqual(FormatUtils.format_size(512), "512.0 B")

    def test_format_rate(self):
        """Test rate formatting"""
        self.assertEqual(FormatUtils.format_rate(500), "500 ports/s")
        self.assertEqual(FormatUtils.format_rate(1500), "1.5k ports/s")
        self.assertEqual(FormatUtils.format_rate(1500000), "1.5M ports/s")

    def test_colorize_text(self):
        """Test text colorization"""
        colored = FormatUtils.colorize_text("test", "red")
        self.assertIn("test", colored)
        self.assertIn("\033[", colored)  # ANSI escape sequence

class TestValidationUtils(unittest.TestCase):
    """Test ValidationUtils class"""

    def test_validate_port_range(self):
        """Test port range validation"""
        valid, message = ValidationUtils.validate_port_range("80,443")
        self.assertTrue(valid)
        self.assertIn("Valid", message)

        valid, message = ValidationUtils.validate_port_range("")
        self.assertFalse(valid)

        valid, message = ValidationUtils.validate_port_range("invalid")
        self.assertFalse(valid)

    def test_validate_target_list(self):
        """Test target list validation"""
        valid, message, targets = ValidationUtils.validate_target_list("127.0.0.1")
        self.assertTrue(valid)
        self.assertEqual(targets, ["127.0.0.1"])

        valid, message, targets = ValidationUtils.validate_target_list("")
        self.assertFalse(valid)
        self.assertEqual(targets, [])

    def test_validate_thread_count(self):
        """Test thread count validation"""
        valid, message = ValidationUtils.validate_thread_count(100)
        self.assertTrue(valid)

        valid, message = ValidationUtils.validate_thread_count(0)
        self.assertFalse(valid)

        valid, message = ValidationUtils.validate_thread_count(3000)
        self.assertFalse(valid)

    def test_validate_timeout(self):
        """Test timeout validation"""
        valid, message = ValidationUtils.validate_timeout(1.0)
        self.assertTrue(valid)

        valid, message = ValidationUtils.validate_timeout(0)
        self.assertFalse(valid)

        valid, message = ValidationUtils.validate_timeout(50)
        self.assertFalse(valid)

class TestSecurityUtils(unittest.TestCase):
    """Test SecurityUtils class"""

    def test_check_privileges(self):
        """Test privilege checking"""
        privileges = SecurityUtils.check_privileges()
        self.assertIn('is_admin', privileges)
        self.assertIn('can_syn_scan', privileges)
        self.assertIn('can_raw_sockets', privileges)
        self.assertIsInstance(privileges['is_admin'], bool)

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        safe = SecurityUtils.sanitize_filename("test<>file.txt")
        self.assertNotIn('<', safe)
        self.assertNotIn('>', safe)

        safe = SecurityUtils.sanitize_filename("../../../etc/passwd")
        self.assertNotIn('..', safe)

        safe = SecurityUtils.sanitize_filename("")
        self.assertEqual(safe, "output")

    def test_validate_target_safety(self):
        """Test target safety validation"""
        # Private IP should be safe
        safe, message = SecurityUtils.validate_target_safety("192.168.1.1")
        self.assertTrue(safe)
        self.assertIn("Safe", message)

        # Localhost should be safe
        safe, message = SecurityUtils.validate_target_safety("127.0.0.1")
        self.assertTrue(safe)

        # Public IP should generate warning
        safe, message = SecurityUtils.validate_target_safety("8.8.8.8")
        self.assertFalse(safe)
        self.assertIn("Warning", message)

class TestStatisticsCalculator(unittest.TestCase):
    """Test StatisticsCalculator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.stats = StatisticsCalculator()

    def test_initialization(self):
        """Test statistics calculator initialization"""
        self.assertIsNone(self.stats.scan_start_time)
        self.assertEqual(self.stats.total_targets, 0)
        self.assertEqual(self.stats.open_ports, 0)

    def test_start_scan(self):
        """Test scan start tracking"""
        self.stats.start_scan(10, 100)
        self.assertEqual(self.stats.total_targets, 10)
        self.assertEqual(self.stats.total_ports, 100)
        self.assertIsNotNone(self.stats.scan_start_time)

    def test_add_result(self):
        """Test result addition"""
        self.stats.start_scan(1, 1)

        result = {
            'target': '192.168.1.1',
            'port': 80,
            'state': 'open',
            'service': 'http'
        }

        self.stats.add_result(result)
        self.assertEqual(self.stats.open_ports, 1)
        self.assertIn('192.168.1.1', self.stats.live_hosts)
        self.assertEqual(self.stats.services_found['http'], 1)

    def test_get_statistics(self):
        """Test statistics generation"""
        self.stats.start_scan(2, 50)

        # Add some mock results
        for i in range(3):
            result = {
                'target': f'192.168.1.{i+1}',
                'port': 80,
                'state': 'open',
                'service': 'http'
            }
            self.stats.add_result(result)

        self.stats.end_scan()
        stats = self.stats.get_statistics()

        self.assertIn('timing', stats)
        self.assertIn('targets', stats)
        self.assertIn('ports', stats)
        self.assertIn('services', stats)
        self.assertEqual(stats['ports']['open_ports_found'], 3)

class TestPortScannerIntegration(unittest.TestCase):
    """Integration tests for PortScanner"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    def test_scan_localhost_closed_port(self):
        """Test scanning a closed port on localhost"""
        results = self.scanner.start_scan(
            ["127.0.0.1"], [99999], "fast", 10, 0.1
        )
        # Should return empty list for closed port
        self.assertEqual(results, [])

    def test_expand_multiple_targets(self):
        """Test expanding multiple target formats"""
        targets = "127.0.0.1,192.168.1.1-2"
        expanded = self.scanner.expand_targets(targets)

        expected_ips = ["127.0.0.1", "192.168.1.1", "192.168.1.2"]
        self.assertEqual(sorted(expanded), sorted(expected_ips))

    def test_concurrent_scanning(self):
        """Test that concurrent scanning doesn't crash"""
        # Scan some closed ports with multiple threads
        try:
            results = self.scanner.start_scan(
                ["127.0.0.1"], [99998, 99999], "fast", 5, 0.1
            )
            # Should complete without error
            self.assertIsInstance(results, list)
        except Exception as e:
            self.fail(f"Concurrent scanning raised exception: {e}")

    def test_stop_scan_functionality(self):
        """Test scan stopping during execution"""
        def stop_after_delay():
            time.sleep(0.1)
            self.scanner.stop_scan()

        # Start stop thread
        stop_thread = threading.Thread(target=stop_after_delay)
        stop_thread.start()

        # Start scan that would normally take longer
        start_time = time.time()
        self.scanner.start_scan(
            ["127.0.0.1"], list(range(99990, 99999)), "fast", 1, 1.0
        )
        elapsed = time.time() - start_time

        stop_thread.join()

        # Scan should have been stopped early (less than expected time)
        self.assertLess(elapsed, 5.0)

class TestFileOperations(unittest.TestCase):
    """Test file operations and export functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_export_results_txt(self):
        """Test TXT export functionality"""
        # Mock some results
        self.scanner.results = [
            {'target': '127.0.0.1', 'port': 80, 'state': 'open', 'service': 'http'},
            {'target': '127.0.0.1', 'port': 443, 'state': 'open', 'service': 'https'}
        ]

        filename = os.path.join(self.temp_dir, "test_results.txt")
        success = self.scanner.export_results(filename, 'txt')

        self.assertTrue(success)
        self.assertTrue(os.path.exists(filename))

        # Check file content
        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn("127.0.0.1", content)
            self.assertIn("80", content)
            self.assertIn("http", content)

    def test_export_results_csv(self):
        """Test CSV export functionality"""
        # Mock some results
        self.scanner.results = [
            {'target': '127.0.0.1', 'port': 80, 'state': 'open', 'service': 'http'}
        ]

        filename = os.path.join(self.temp_dir, "test_results.csv")
        success = self.scanner.export_results(filename, 'csv')

        self.assertTrue(success)
        self.assertTrue(os.path.exists(filename))

        # Check CSV format
        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn("Target,Port,State,Service", content)
            self.assertIn("127.0.0.1,80,open,http", content)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""

    def test_module_level_functions(self):
        """Test module-level convenience functions"""
        from utils import validate_target, validate_port, expand_targets

        # Test validate_target
        self.assertTrue(validate_target("127.0.0.1"))
        self.assertFalse(validate_target("invalid"))

        # Test validate_port
        self.assertTrue(validate_port(80))
        self.assertTrue(validate_port("443"))
        self.assertFalse(validate_port("invalid"))
        self.assertFalse(validate_port(70000))

        # Test expand_targets
        targets = expand_targets("127.0.0.1,192.168.1.1")
        self.assertIn("127.0.0.1", targets)
        self.assertIn("192.168.1.1", targets)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    def test_invalid_target_handling(self):
        """Test handling of invalid targets"""
        # Should not crash on invalid targets
        try:
            result = self.scanner.expand_targets("999.999.999.999")
            self.assertIsInstance(result, list)
        except Exception as e:
            self.fail(f"Invalid target handling raised exception: {e}")

    def test_invalid_port_handling(self):
        """Test handling of invalid ports"""
        # Should not crash on invalid ports
        try:
            result = self.scanner.parse_port_range("invalid,99999")
            self.assertIsInstance(result, list)
        except Exception as e:
            # ValueError is expected for invalid formats
            self.assertIsInstance(e, ValueError)

    def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        # Test with very short timeout
        result = self.scanner.scan_port("192.168.1.1", 80, timeout=0.001)
        # Should return None without crashing
        self.assertIsNone(result)

    def test_empty_input_handling(self):
        """Test handling of empty inputs"""
        # Empty target
        self.assertFalse(self.scanner.validate_target(""))

        # Empty port range should return default
        result = self.scanner.parse_port_range("")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

class TestThreadSafety(unittest.TestCase):
    """Test thread safety of scanner operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    def test_concurrent_stop_calls(self):
        """Test multiple stop calls don't cause issues"""
        # Start scanning
        self.scanner.is_scanning = True

        # Call stop multiple times from different threads
        def stop_scan():
            self.scanner.stop_scan()

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=stop_scan)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should not crash and scanning should be stopped
        self.assertFalse(self.scanner.is_scanning)

    def test_results_access_during_scan(self):
        """Test accessing results while scan is running"""
        self.scanner.results = [
            {'target': '127.0.0.1', 'port': 80, 'state': 'open', 'service': 'http'}
        ]

        # Should be able to access results safely
        results = self.scanner.get_results()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)

class TestMockScanning(unittest.TestCase):
    """Test scanning with mocked network operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    @patch('socket.socket')
    def test_mock_open_port(self, mock_socket):
        """Test scanning with mocked open port"""
        # Mock socket to simulate open port
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect_ex.return_value = 0  # Success
        mock_socket.return_value = mock_sock_instance

        result = self.scanner.scan_port("192.168.1.1", 80, timeout=1.0)

        self.assertIsNotNone(result)
        self.assertEqual(result['target'], '192.168.1.1')
        self.assertEqual(result['port'], 80)
        self.assertEqual(result['state'], 'open')

    @patch('socket.socket')
    def test_mock_closed_port(self, mock_socket):
        """Test scanning with mocked closed port"""
        # Mock socket to simulate closed port
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect_ex.return_value = 1  # Connection refused
        mock_socket.return_value = mock_sock_instance

        result = self.scanner.scan_port("192.168.1.1", 80, timeout=1.0)

        self.assertIsNone(result)

    @patch('subprocess.run')
    def test_mock_ping_success(self, mock_run):
        """Test ping with mocked successful response"""
        # Mock successful ping
        mock_run.return_value.returncode = 0

        result = ScanUtils.ping_host("192.168.1.1")
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_mock_ping_failure(self, mock_run):
        """Test ping with mocked failed response"""
        # Mock failed ping
        mock_run.return_value.returncode = 1

        result = ScanUtils.ping_host("192.168.1.1")
        self.assertFalse(result)

class TestConfigurationHandling(unittest.TestCase):
    """Test configuration loading and saving"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """Test default configuration"""
        from utils import ConfigUtils

        config = ConfigUtils.DEFAULT_CONFIG
        self.assertIn('scan', config)
        self.assertIn('ui', config)
        self.assertIn('output', config)

    @patch('builtins.open', new_callable=mock_open, read_data='{"scan": {"default_threads": 200}}')
    def test_config_loading(self, mock_file):
        """Test configuration loading"""
        from utils import ConfigUtils

        config = ConfigUtils.load_config("test_config.json")
        self.assertIn('scan', config)
        # Should merge with defaults
        self.assertIn('ui', config)

    def test_config_saving(self):
        """Test configuration saving"""
        from utils import ConfigUtils

        config = {"test": {"value": 123}}
        filename = os.path.join(self.temp_dir, "test_config.json")

        success = ConfigUtils.save_config(config, filename)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filename))

        # Verify saved content
        with open(filename, 'r') as f:
            loaded_config = json.load(f)
            self.assertEqual(loaded_config['test']['value'], 123)

class TestPerformanceOptimization(unittest.TestCase):
    """Test performance optimization utilities"""

    def test_thread_optimization(self):
        """Test thread count optimization"""
        from utils import PerformanceUtils

        # Small scan
        threads = PerformanceUtils.optimize_thread_count(1, 10)
        self.assertLessEqual(threads, 50)

        # Large scan
        threads = PerformanceUtils.optimize_thread_count(1000, 1000)
        self.assertGreater(threads, 100)

    def test_timeout_optimization(self):
        """Test timeout optimization"""
        from utils import PerformanceUtils

        timeout = PerformanceUtils.optimize_timeout('fast', 'local')
        self.assertGreater(timeout, 0)
        self.assertLess(timeout, 10)

    def test_scan_time_estimation(self):
        """Test scan time estimation"""
        from utils import PerformanceUtils

        estimate = PerformanceUtils.estimate_scan_time(10, 100, 50, 1.0)
        self.assertGreater(estimate, 0)
        self.assertIsInstance(estimate, float)

class TestExportFormats(unittest.TestCase):
    """Test different export formats"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_results = [
            {'target': '192.168.1.1', 'port': 80, 'state': 'open', 'service': 'http', 'protocol': 'tcp'},
            {'target': '192.168.1.1', 'port': 443, 'state': 'open', 'service': 'https', 'protocol': 'tcp'}
        ]

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_nmap_xml_export(self):
        """Test nmap XML export format"""
        from utils import ExportUtils

        filename = os.path.join(self.temp_dir, "test.xml")
        success = ExportUtils.export_to_nmap_xml(self.sample_results, {}, filename)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(filename))

        # Check XML content
        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn('<?xml', content)
            self.assertIn('192.168.1.1', content)
            self.assertIn('port protocol="tcp" portid="80"', content)

    def test_masscan_format_export(self):
        """Test masscan format export"""
        from utils import ExportUtils

        filename = os.path.join(self.temp_dir, "test.masscan")
        success = ExportUtils.export_to_masscan_format(self.sample_results, filename)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(filename))

        # Check masscan format
        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn('open tcp 80 192.168.1.1', content)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    def test_large_port_range(self):
        """Test handling of large port ranges"""
        # Test parsing large range without actually scanning
        try:
            ports = self.scanner.parse_port_range("1-65535")
            self.assertEqual(len(ports), 65535)
        except Exception as e:
            self.fail(f"Large port range parsing failed: {e}")

    def test_single_target_single_port(self):
        """Test minimal scan configuration"""
        result = self.scanner.start_scan(
            ["127.0.0.1"], [99999], "fast", 1, 0.1
        )
        self.assertIsInstance(result, list)

    def test_zero_timeout_handling(self):
        """Test handling of zero timeout"""
        # Very short timeout should not crash
        result = self.scanner.scan_port("127.0.0.1", 99999, timeout=0.001)
        self.assertIsNone(result)

    def test_network_unreachable(self):
        """Test handling of unreachable networks"""
        # Test unreachable IP range
        result = self.scanner.scan_port("10.255.255.254", 80, timeout=0.1)
        self.assertIsNone(result)

class TestPerformanceScaling(unittest.TestCase):
    """Test performance with different scaling scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PortScanner()

    def test_single_thread_performance(self):
        """Test single-threaded scanning"""
        start_time = time.time()
        self.scanner.start_scan(
            ["127.0.0.1"], [99998, 99999], "fast", 1, 0.1
        )
        elapsed = time.time() - start_time

        # Should complete in reasonable time
        self.assertLess(elapsed, 5.0)

    def test_multi_thread_performance(self):
        """Test multi-threaded scanning"""
        start_time = time.time()
        self.scanner.start_scan(
            ["127.0.0.1"], [99995, 99996, 99997, 99998, 99999], "fast", 10, 0.1
        )
        elapsed = time.time() - start_time

        # Should complete faster than single-threaded equivalent
        self.assertLess(elapsed, 5.0)

    def test_thread_count_scaling(self):
        """Test that more threads don't break anything"""
        # Test with various thread counts
        for threads in [1, 5, 10, 50]:
            with self.subTest(threads=threads):
                try:
                    self.scanner.start_scan(
                        ["127.0.0.1"], [99999], "fast", threads, 0.1
                    )
                except Exception as e:
                    self.fail(f"Scanning with {threads} threads failed: {e}")

if __name__ == '__main__':
    # Test runner with custom test discovery and reporting
    import argparse

    parser = argparse.ArgumentParser(description='MaScanner Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose test output')
    parser.add_argument('--pattern', '-p', default='test*.py',
                       help='Test file pattern')
    parser.add_argument('--module', '-m',
                       help='Run specific test module')
    parser.add_argument('--coverage', action='store_true',
                       help='Run with coverage analysis')

    args = parser.parse_args()

    # Configure test verbosity
    verbosity = 2 if args.verbose else 1

    if args.coverage:
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
            print("Running tests with coverage analysis...")
        except ImportError:
            print("Coverage package not available, running without coverage")
            args.coverage = False

    # Create test suite
    if args.module:
        # Run specific module
        suite = unittest.TestLoader().loadTestsFromName(args.module)
    else:
        # Discover all tests
        loader = unittest.TestLoader()
        suite = loader.discover('.', pattern=args.pattern)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Coverage reporting
    if args.coverage:
        cov.stop()
        cov.save()
        print("\nCoverage Report:")
        cov.report()

    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.split('Exception:')[-1].strip()}")

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
