#!/usr/bin/env python3
"""
MaScanner - A GUI Port Scanner similar to masscan
Author: Assistant
Description: High-performance network port scanner with GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
from datetime import datetime
import json
import csv
from scanner import PortScanner

class MaScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MaScanner - Network Port Scanner")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Scanner instance
        self.scanner = PortScanner()
        self.scan_thread = None
        self.is_scanning = False

        # Variables
        self.scan_progress = tk.DoubleVar()
        self.status_text = tk.StringVar(value="Ready")

        self.setup_gui()
        self.setup_menu()

    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Ping Sweep", command=self.ping_sweep)
        tools_menu.add_command(label="Clear Results", command=self.clear_results)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_gui(self):
        """Setup main GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)

        # Target configuration
        ttk.Label(main_frame, text="Target(s):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.target_entry = ttk.Entry(main_frame, width=50)
        self.target_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.target_entry.insert(0, "192.168.1.1-254")

        # Port configuration
        ttk.Label(main_frame, text="Port(s):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.port_entry.insert(0, "22,80,443,3389,21,23,25,53,110,143,993,995")

        # Scan type
        ttk.Label(main_frame, text="Scan Type:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.scan_type = ttk.Combobox(main_frame, values=["fast", "SYN", "TCP", "UDP"], state="readonly")
        self.scan_type.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.scan_type.set("fast")

        # Advanced options frame
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Options", padding="5")
        advanced_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        advanced_frame.columnconfigure(1, weight=1)

        # Thread count
        ttk.Label(advanced_frame, text="Threads:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.thread_count = tk.StringVar(value="100")
        thread_spin = tk.Spinbox(advanced_frame, from_=1, to=1000, textvariable=self.thread_count, width=10)
        thread_spin.grid(row=0, column=1, sticky=tk.W)

        # Timeout
        ttk.Label(advanced_frame, text="Timeout (s):").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.timeout = tk.StringVar(value="1")
        timeout_spin = tk.Spinbox(advanced_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.timeout, width=10)
        timeout_spin.grid(row=0, column=3, sticky=tk.W)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))

        self.start_button = ttk.Button(button_frame, text="Start Scan", command=self.start_scan)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.scan_progress, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="5")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results treeview
        columns = ('Target', 'Port', 'State', 'Service', 'Protocol')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)

        # Define column headings and widths
        self.results_tree.heading('Target', text='Target')
        self.results_tree.heading('Port', text='Port')
        self.results_tree.heading('State', text='State')
        self.results_tree.heading('Service', text='Service')
        self.results_tree.heading('Protocol', text='Protocol')

        self.results_tree.column('Target', width=150)
        self.results_tree.column('Port', width=80)
        self.results_tree.column('State', width=80)
        self.results_tree.column('Service', width=100)
        self.results_tree.column('Protocol', width=80)

        # Scrollbars for treeview
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
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text)
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        self.result_count_label = ttk.Label(status_frame, text="Results: 0")
        self.result_count_label.grid(row=0, column=2, sticky=tk.E)

    def validate_inputs(self):
        """Validate user inputs before scanning"""
        targets = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()

        if not targets:
            messagebox.showerror("Error", "Please enter target IP addresses or hostnames")
            return False

        if not ports:
            messagebox.showerror("Error", "Please enter port numbers or ranges")
            return False

        # Validate at least one target
        target_list = [t.strip() for t in targets.split(',')]
        valid_targets = []

        for target in target_list:
            if self.scanner.validate_target(target):
                valid_targets.append(target)
            else:
                messagebox.showwarning("Warning", f"Invalid target: {target}")

        if not valid_targets:
            messagebox.showerror("Error", "No valid targets specified")
            return False

        # Validate ports
        try:
            port_list = self.scanner.parse_port_range(ports)
            if not port_list:
                messagebox.showerror("Error", "No valid ports specified")
                return False
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid port specification: {str(e)}")
            return False

        return True

    def start_scan(self):
        """Start the scanning process"""
        if not self.validate_inputs():
            return

        self.is_scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_text.set("Preparing scan...")
        self.scan_progress.set(0)

        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Get scan parameters
        targets = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()
        scan_type = self.scan_type.get()
        max_workers = int(self.thread_count.get())
        timeout = float(self.timeout.get())

        # Start scan in separate thread
        self.scan_thread = threading.Thread(
            target=self.run_scan,
            args=(targets, ports, scan_type, max_workers, timeout),
            daemon=True
        )
        self.scan_thread.start()

    def run_scan(self, targets, ports, scan_type, max_workers, timeout):
        """Run the actual scan"""
        try:
            # Expand targets and ports
            target_list = self.scanner.expand_targets(targets)
            port_list = self.scanner.parse_port_range(ports)

            self.status_text.set(f"Scanning {len(target_list)} targets, {len(port_list)} ports...")

            # Start scan
            results = self.scanner.start_scan(
                target_list,
                port_list,
                scan_type,
                max_workers,
                timeout,
                self.scan_callback
            )

            if self.is_scanning:
                self.status_text.set(f"Scan completed. Found {len(results)} open ports.")
                self.scan_progress.set(100)
            else:
                self.status_text.set("Scan stopped by user.")

        except Exception as e:
            self.status_text.set(f"Error during scan: {str(e)}")
            messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{str(e)}")
        finally:
            self.scan_finished()

    def scan_callback(self, callback_type, data=None):
        """Handle callbacks from scanner"""
        if callback_type == 'result':
            # Add result to tree (thread-safe)
            self.root.after(0, self.add_result_to_tree, data)
        elif callback_type == 'progress':
            # Update progress bar
            self.root.after(0, self.update_progress, data)
        elif callback_type == 'error':
            self.root.after(0, lambda: self.status_text.set(f"Error: {data}"))
        elif isinstance(callback_type, str) and callback_type.startswith("Starting"):
            self.root.after(0, lambda: self.status_text.set(callback_type))

    def add_result_to_tree(self, result):
        """Add scan result to the treeview"""
        protocol = result.get('protocol', 'tcp')
        self.results_tree.insert('', 'end', values=(
            result['target'],
            result['port'],
            result['state'],
            result['service'],
            protocol
        ))

        # Update result count
        count = len(self.results_tree.get_children())
        self.result_count_label.config(text=f"Results: {count}")

    def update_progress(self, progress):
        """Update progress bar"""
        self.scan_progress.set(progress)

    def stop_scan(self):
        """Stop the current scan"""
        self.is_scanning = False
        self.scanner.stop_scan()
        self.status_text.set("Stopping scan...")

    def scan_finished(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def clear_results(self):
        """Clear all scan results"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.result_count_label.config(text="Results: 0")
        self.scan_progress.set(0)
        self.status_text.set("Results cleared")

    def ping_sweep(self):
        """Perform ping sweep on targets"""
        if self.is_scanning:
            messagebox.showwarning("Warning", "A scan is already in progress")
            return

        targets = self.target_entry.get().strip()
        if not targets:
            messagebox.showerror("Error", "Please enter target IP addresses")
            return

        # Start ping sweep in separate thread
        self.is_scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_text.set("Performing ping sweep...")

        def run_ping_sweep():
            try:
                target_list = self.scanner.expand_targets(targets)
                live_hosts = self.scanner.ping_sweep(target_list, self.ping_callback)

                if self.is_scanning:
                    self.status_text.set(f"Ping sweep completed. {len(live_hosts)} hosts alive.")
                    messagebox.showinfo("Ping Sweep Results",
                                      f"Found {len(live_hosts)} live hosts:\n" +
                                      "\n".join(live_hosts[:10]) +
                                      ("..." if len(live_hosts) > 10 else ""))
            except Exception as e:
                self.status_text.set(f"Ping sweep error: {str(e)}")
            finally:
                self.scan_finished()

        threading.Thread(target=run_ping_sweep, daemon=True).start()

    def ping_callback(self, callback_type, data):
        """Handle ping sweep callbacks"""
        if callback_type == 'ping_result':
            self.root.after(0, lambda: self.status_text.set(f"Found live host: {data['target']}"))

    def export_results(self):
        """Export scan results to file"""
        if not self.results_tree.get_children():
            messagebox.showwarning("Warning", "No results to export")
            return

        # Get file path from user
        filetypes = [
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]

        filename = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".txt",
            filetypes=filetypes
        )

        if not filename:
            return

        try:
            # Collect results from treeview
            results = []
            for item in self.results_tree.get_children():
                values = self.results_tree.item(item)['values']
                results.append({
                    'target': values[0],
                    'port': values[1],
                    'state': values[2],
                    'service': values[3],
                    'protocol': values[4]
                })

            # Determine format from extension
            if filename.endswith('.csv'):
                self.export_csv(filename, results)
            elif filename.endswith('.json'):
                self.export_json(filename, results)
            else:
                self.export_txt(filename, results)

            messagebox.showinfo("Export Successful", f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")

    def export_txt(self, filename, results):
        """Export results as text file"""
        with open(filename, 'w') as f:
            f.write("MaScanner Scan Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for result in results:
                f.write(f"Target: {result['target']}\n")
                f.write(f"Port: {result['port']}\n")
                f.write(f"State: {result['state']}\n")
                f.write(f"Service: {result['service']}\n")
                f.write(f"Protocol: {result['protocol']}\n")
                f.write("-" * 40 + "\n")

    def export_csv(self, filename, results):
        """Export results as CSV file"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Target', 'Port', 'State', 'Service', 'Protocol'])

            for result in results:
                writer.writerow([
                    result['target'],
                    result['port'],
                    result['state'],
                    result['service'],
                    result['protocol']
                ])

    def export_json(self, filename, results):
        """Export results as JSON file"""
        export_data = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'tool': 'MaScanner',
                'total_results': len(results)
            },
            'results': results
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

    def show_about(self):
        """Show about dialog"""
        about_text = """MaScanner v1.0

A high-performance network port scanner with GUI interface,
inspired by masscan.

Features:
• Fast concurrent port scanning
• Multiple target formats (IP, CIDR, ranges)
• Various scan types (TCP, SYN, UDP)
• Ping sweep functionality
• Export results to multiple formats
• Customizable threading and timeouts

Developed using Python and tkinter.
"""
        messagebox.showinfo("About MaScanner", about_text)

    def on_closing(self):
        """Handle application closing"""
        if self.is_scanning:
            if messagebox.askokcancel("Quit", "A scan is in progress. Do you want to quit?"):
                self.stop_scan()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = MaScannerGUI(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Set application icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass  # Icon file not found, use default

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
