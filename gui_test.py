#!/usr/bin/env python3
"""
Simple GUI Test for MaScanner - Test basic GUI functionality without nmap dependency
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

class SimplePortScanner:
    """Simplified port scanner using only standard library"""

    def __init__(self):
        self.results = []
        self.is_scanning = False

    def validate_ip(self, ip_str):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    def parse_ports(self, port_str):
        """Parse port specification"""
        ports = []
        if not port_str.strip():
            return [22, 80, 443, 3389]  # Default ports

        for part in port_str.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if start <= end and 1 <= start <= 65535 and 1 <= end <= 65535:
                        ports.extend(range(start, min(end + 1, start + 100)))  # Limit range for demo
                except ValueError:
                    continue
            else:
                try:
                    port = int(part)
                    if 1 <= port <= 65535:
                        ports.append(port)
                except ValueError:
                    continue

        return sorted(list(set(ports)))

    def expand_targets(self, target_str):
        """Expand target string to list of IPs"""
        targets = []

        for target in target_str.split(','):
            target = target.strip()

            if '/' in target:  # CIDR
                try:
                    network = ipaddress.ip_network(target, strict=False)
                    # Limit to first 20 hosts for demo
                    host_list = list(network.hosts())[:20]
                    targets.extend([str(ip) for ip in host_list])
                except ValueError:
                    continue
            elif '-' in target:  # Range
                try:
                    start_ip, end_part = target.split('-')
                    start_parts = start_ip.strip().split('.')
                    end_num = int(end_part.strip())
                    start_num = int(start_parts[3])
                    base = '.'.join(start_parts[:3])

                    # Limit range for demo
                    for i in range(start_num, min(end_num + 1, start_num + 20)):
                        targets.append(f"{base}.{i}")
                except (ValueError, IndexError):
                    continue
            else:  # Single IP
                if self.validate_ip(target):
                    targets.append(target)

        return targets

    def scan_port(self, host, port, timeout=1.0):
        """Scan single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                service_map = {
                    21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
                    53: 'dns', 80: 'http', 110: 'pop3', 143: 'imap',
                    443: 'https', 993: 'imaps', 995: 'pop3s',
                    3389: 'rdp', 3306: 'mysql', 5432: 'postgresql'
                }
                service = service_map.get(port, 'unknown')

                return {
                    'target': host,
                    'port': port,
                    'state': 'open',
                    'service': service
                }
        except Exception:
            pass

        return None

    def start_scan(self, targets, ports, max_workers=50, timeout=1.0, callback=None):
        """Start concurrent scan"""
        self.results = []
        self.is_scanning = True

        total_scans = len(targets) * len(ports)
        completed_scans = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_scan = {}

            for target in targets:
                for port in ports:
                    if not self.is_scanning:
                        break
                    future = executor.submit(self.scan_port, target, port, timeout)
                    future_to_scan[future] = (target, port)

            for future in as_completed(future_to_scan):
                if not self.is_scanning:
                    break

                result = future.result()
                completed_scans += 1

                if result:
                    self.results.append(result)
                    if callback:
                        callback('result', result)

                progress = (completed_scans / total_scans) * 100
                if callback:
                    callback('progress', progress)

        return self.results

    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False

class SimpleGUI:
    """Simple GUI for MaScanner testing"""

    def __init__(self, root):
        self.root = root
        self.root.title("MaScanner - Simple GUI Test")
        self.root.geometry("800x600")

        self.scanner = SimplePortScanner()
        self.scan_thread = None
        self.is_scanning = False

        # Variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")

        self.setup_gui()

    def setup_gui(self):
        """Setup GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="MaScanner - Network Port Scanner",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Target input
        ttk.Label(main_frame, text="Target(s):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.target_entry = ttk.Entry(main_frame, width=50)
        self.target_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.target_entry.insert(0, "127.0.0.1")

        # Port input
        ttk.Label(main_frame, text="Port(s):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.port_entry.insert(0, "22,80,443,3389,8080")

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Scan Options", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))

        ttk.Label(options_frame, text="Threads:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.threads_var = tk.StringVar(value="50")
        thread_spin = tk.Spinbox(options_frame, from_=1, to=200, textvariable=self.threads_var, width=10)
        thread_spin.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(options_frame, text="Timeout:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.timeout_var = tk.StringVar(value="1.0")
        timeout_spin = tk.Spinbox(options_frame, from_=0.1, to=5.0, increment=0.1,
                                 textvariable=self.timeout_var, width=10)
        timeout_spin.grid(row=0, column=3, sticky=tk.W)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))

        self.start_button = ttk.Button(button_frame, text="🚀 Start Scan",
                                      command=self.start_scan)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Scan",
                                     command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_results).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Export", command=self.export_results).pack(side=tk.LEFT, padx=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="5")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results treeview
        columns = ('Target', 'Port', 'State', 'Service')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)

        # Configure columns
        for col in columns:
            self.results_tree.heading(col, text=col)

        self.results_tree.column('Target', width=150)
        self.results_tree.column('Port', width=80)
        self.results_tree.column('State', width=80)
        self.results_tree.column('Service', width=120)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        tree_scroll_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        self.result_count_label = ttk.Label(status_frame, text="Results: 0")
        self.result_count_label.grid(row=0, column=2, sticky=tk.E)

    def validate_inputs(self):
        """Validate user inputs"""
        targets = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()

        if not targets:
            messagebox.showerror("Error", "Please enter target IP addresses")
            return False

        if not ports:
            messagebox.showerror("Error", "Please enter port numbers")
            return False

        # Basic target validation
        target_list = self.scanner.expand_targets(targets)
        if not target_list:
            messagebox.showerror("Error", "No valid targets found")
            return False

        # Basic port validation
        port_list = self.scanner.parse_ports(ports)
        if not port_list:
            messagebox.showerror("Error", "No valid ports found")
            return False

        # Warn about large scans
        total_scans = len(target_list) * len(port_list)
        if total_scans > 1000:
            if not messagebox.askyesno("Large Scan Warning",
                                     f"This will perform {total_scans:,} port checks.\n"
                                     f"This may take a while. Continue?"):
                return False

        return True

    def start_scan(self):
        """Start scanning process"""
        if not self.validate_inputs():
            return

        self.is_scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Preparing scan...")
        self.progress_var.set(0)

        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Get parameters
        targets = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()
        threads = int(self.threads_var.get())
        timeout = float(self.timeout_var.get())

        # Start scan in thread
        self.scan_thread = threading.Thread(
            target=self.run_scan,
            args=(targets, ports, threads, timeout),
            daemon=True
        )
        self.scan_thread.start()

    def run_scan(self, targets, ports, threads, timeout):
        """Run the actual scan"""
        try:
            target_list = self.scanner.expand_targets(targets)
            port_list = self.scanner.parse_ports(ports)

            self.status_var.set(f"Scanning {len(target_list)} targets, {len(port_list)} ports...")

            # Start scan with callback
            results = self.scanner.start_scan(
                target_list, port_list, threads, timeout, self.scan_callback
            )

            if self.is_scanning:
                self.status_var.set(f"Scan completed. Found {len(results)} open ports.")
                self.progress_var.set(100)
            else:
                self.status_var.set("Scan stopped by user.")

        except Exception as e:
            self.status_var.set(f"Scan error: {str(e)}")
            messagebox.showerror("Error", f"Scan failed:\n{str(e)}")
        finally:
            self.scan_finished()

    def scan_callback(self, callback_type, data):
        """Handle scan callbacks"""
        if callback_type == 'result':
            self.root.after(0, self.add_result, data)
        elif callback_type == 'progress':
            self.root.after(0, self.update_progress, data)

    def add_result(self, result):
        """Add result to treeview"""
        self.results_tree.insert('', 'end', values=(
            result['target'],
            result['port'],
            result['state'],
            result['service']
        ))

        # Update count
        count = len(self.results_tree.get_children())
        self.result_count_label.config(text=f"Results: {count}")

    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_var.set(progress)

    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False
        self.scanner.stop_scan()
        self.status_var.set("Stopping scan...")

    def scan_finished(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def clear_results(self):
        """Clear all results"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.result_count_label.config(text="Results: 0")
        self.progress_var.set(0)
        self.status_var.set("Results cleared")

    def export_results(self):
        """Export results to file"""
        if not self.results_tree.get_children():
            messagebox.showwarning("Warning", "No results to export")
            return

        try:
            # Simple text export
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"mascanner_results_{timestamp}.txt"

            with open(filename, 'w') as f:
                f.write("MaScanner Scan Results\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")

                for item in self.results_tree.get_children():
                    values = self.results_tree.item(item)['values']
                    f.write(f"Target: {values[0]}\n")
                    f.write(f"Port: {values[1]}\n")
                    f.write(f"State: {values[2]}\n")
                    f.write(f"Service: {values[3]}\n")
                    f.write("-" * 30 + "\n")

            messagebox.showinfo("Export Complete", f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")

def main():
    """Main function"""
    print("Starting MaScanner Simple GUI Test...")

    # Check tkinter availability
    try:
        root = tk.Tk()
        root.withdraw()  # Hide initially

        # Test basic tkinter functionality
        test_label = ttk.Label(root, text="Test")
        test_button = ttk.Button(root, text="Test")

        print("✅ tkinter is working correctly")

        # Show GUI
        root.deiconify()
        scanner = SimplePortScanner()
        app = SimpleGUI(root)

        # Add some example text
        info_text = """
MaScanner Simple GUI Test

This is a simplified version of MaScanner that works without nmap.
It demonstrates the core GUI functionality and basic port scanning.

Instructions:
1. Enter target IPs (e.g., 127.0.0.1 or 192.168.1.1-5)
2. Enter ports (e.g., 22,80,443 or 80-90)
3. Adjust threads and timeout if needed
4. Click 'Start Scan' to begin
5. Results will appear in the table below

Example targets:
• 127.0.0.1 (localhost)
• 192.168.1.1-10 (IP range)
• 10.0.0.0/29 (CIDR notation)

Example ports:
• 22,80,443 (common ports)
• 80-90 (port range)
• 22,80-85,443 (mixed format)

Note: This test version uses basic TCP connect scanning.
For full features, install nmap and use the complete version.
        """

        # Create info dialog
        def show_info():
            messagebox.showinfo("MaScanner Test Info", info_text)

        # Add info button
        ttk.Button(app.root, text="ℹ️ Info", command=show_info).place(x=10, y=10)

        # Handle window closing
        def on_closing():
            if app.is_scanning:
                if messagebox.askokcancel("Quit", "A scan is in progress. Quit anyway?"):
                    app.stop_scan()
                    root.destroy()
            else:
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 GUI started successfully!")
        print("Close the GUI window when done testing.")

        # Start GUI event loop
        root.mainloop()

        print("👋 GUI test completed")

    except ImportError as e:
        print(f"❌ tkinter not available: {e}")
        print("Install tkinter:")
        print("  Ubuntu: sudo apt-get install python3-tk")
        print("  CentOS: sudo yum install tkinter")
        print("  macOS: brew install python-tk")
        return 1

    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 GUI test interrupted")
        sys.exit(0)
