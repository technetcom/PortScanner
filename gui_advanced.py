#!/usr/bin/env python3
"""
Advanced GUI module for MaScanner with enhanced features and improved layout
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import json
import csv
import socket
import ipaddress
from scanner import PortScanner

class AdvancedMaScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MaScanner Pro - Advanced Network Port Scanner")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Configure style
        self.setup_styles()

        # Scanner instance
        self.scanner = PortScanner()
        self.scan_thread = None
        self.is_scanning = False

        # Variables
        self.scan_progress = tk.DoubleVar()
        self.status_text = tk.StringVar(value="Ready")
        self.scan_time = tk.StringVar(value="00:00:00")
        self.targets_scanned = tk.IntVar(value=0)
        self.ports_found = tk.IntVar(value=0)

        # Scan statistics
        self.scan_start_time = None
        self.scan_stats = {
            'total_targets': 0,
            'total_ports': 0,
            'scanned_combinations': 0,
            'open_ports': 0,
            'live_hosts': set()
        }

        self.setup_gui()
        self.setup_menu()
        self.start_time_updater()

    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()

        # Configure some custom styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')

    def setup_menu(self):
        """Setup enhanced application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Targets...", command=self.load_targets)
        file_menu.add_command(label="Save Targets...", command=self.save_targets)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_command(label="Import Results...", command=self.import_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Scan menu
        scan_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Scan", menu=scan_menu)
        scan_menu.add_command(label="Start Scan", command=self.start_scan)
        scan_menu.add_command(label="Stop Scan", command=self.stop_scan)
        scan_menu.add_separator()
        scan_menu.add_command(label="Quick Scan (Top 100 Ports)", command=self.quick_scan)
        scan_menu.add_command(label="Full Scan (All Ports)", command=self.full_scan)
        scan_menu.add_separator()
        scan_menu.add_command(label="Ping Sweep", command=self.ping_sweep)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Port Lookup", command=self.show_port_lookup)
        tools_menu.add_command(label="Network Calculator", command=self.show_network_calc)
        tools_menu.add_command(label="DNS Lookup", command=self.show_dns_lookup)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear All Results", command=self.clear_results)
        tools_menu.add_command(label="Filter Results", command=self.show_filter_dialog)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Statistics Panel", command=self.toggle_stats_panel)
        view_menu.add_command(label="Show Log Panel", command=self.toggle_log_panel)
        view_menu.add_separator()
        view_menu.add_command(label="Collapse All Groups", command=self.collapse_all)
        view_menu.add_command(label="Expand All Groups", command=self.expand_all)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_gui(self):
        """Setup enhanced GUI with notebook tabs and better layout"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Main scan tab
        self.setup_main_tab()

        # Results tab
        self.setup_results_tab()

        # Statistics tab
        self.setup_statistics_tab()

        # Log tab
        self.setup_log_tab()

        # Status bar
        self.setup_status_bar()

    def setup_main_tab(self):
        """Setup main scanning configuration tab"""
        main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_frame, text="Scan Configuration")

        main_frame.columnconfigure(1, weight=1)

        # Target configuration section
        target_group = ttk.LabelFrame(main_frame, text="Target Configuration", padding="10")
        target_group.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        target_group.columnconfigure(1, weight=1)

        ttk.Label(target_group, text="Target(s):", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.target_entry = ttk.Entry(target_group, width=60, font=('Consolas', 10))
        self.target_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.target_entry.insert(0, "192.168.1.1-254")

        # Target examples
        examples_text = "Examples: 192.168.1.1 | 192.168.1.0/24 | 192.168.1.1-254 | example.com"
        ttk.Label(target_group, text=examples_text, foreground='gray').grid(row=1, column=1, columnspan=2, sticky=tk.W)

        # Quick target buttons
        quick_frame = ttk.Frame(target_group)
        quick_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(5, 0))

        ttk.Button(quick_frame, text="Local Network", command=self.set_local_network, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_frame, text="Localhost", command=self.set_localhost, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Load from File", command=self.load_targets_file, width=12).pack(side=tk.LEFT, padx=5)

        # Port configuration section
        port_group = ttk.LabelFrame(main_frame, text="Port Configuration", padding="10")
        port_group.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        port_group.columnconfigure(1, weight=1)

        ttk.Label(port_group, text="Port(s):", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.port_entry = ttk.Entry(port_group, width=60, font=('Consolas', 10))
        self.port_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.port_entry.insert(0, "22,80,443,3389,21,23,25,53,110,143,993,995")

        # Port presets
        preset_frame = ttk.Frame(port_group)
        preset_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(5, 0))

        ttk.Button(preset_frame, text="Top 100", command=lambda: self.set_port_preset("top100"), width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Top 1000", command=lambda: self.set_port_preset("top1000"), width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_frame, text="Web Ports", command=lambda: self.set_port_preset("web"), width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_frame, text="Database", command=lambda: self.set_port_preset("database"), width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_frame, text="All Ports", command=lambda: self.set_port_preset("all"), width=10).pack(side=tk.LEFT, padx=5)

        # Scan options section
        options_group = ttk.LabelFrame(main_frame, text="Scan Options", padding="10")
        options_group.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        options_group.columnconfigure(1, weight=1)

        # Scan type
        ttk.Label(options_group, text="Scan Type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.scan_type = ttk.Combobox(options_group, values=["fast", "SYN", "TCP", "UDP", "PING"], state="readonly", width=15)
        self.scan_type.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        self.scan_type.set("fast")

        # Advanced options in two columns
        ttk.Label(options_group, text="Threads:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.thread_count = tk.StringVar(value="100")
        thread_spin = tk.Spinbox(options_group, from_=1, to=1000, textvariable=self.thread_count, width=10)
        thread_spin.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))

        ttk.Label(options_group, text="Timeout (s):").grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=(0, 5))
        self.timeout = tk.StringVar(value="1.0")
        timeout_spin = tk.Spinbox(options_group, from_=0.1, to=10.0, increment=0.1, textvariable=self.timeout, width=10)
        timeout_spin.grid(row=1, column=3, sticky=tk.W, pady=(0, 5))

        # Rate limiting
        ttk.Label(options_group, text="Rate Limit:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.rate_limit = tk.StringVar(value="1000")
        rate_spin = tk.Spinbox(options_group, from_=1, to=10000, textvariable=self.rate_limit, width=10)
        rate_spin.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        ttk.Label(options_group, text="packets/sec").grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))

        # Additional options
        self.randomize_hosts = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_group, text="Randomize host order", variable=self.randomize_hosts).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        self.resolve_hostnames = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_group, text="Resolve hostnames", variable=self.resolve_hostnames).grid(row=3, column=2, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Control section
        control_group = ttk.LabelFrame(main_frame, text="Scan Control", padding="10")
        control_group.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        button_frame = ttk.Frame(control_group)
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(button_frame, text="🚀 Start Scan", command=self.start_scan, style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        self.pause_button = ttk.Button(button_frame, text="⏸ Pause", command=self.pause_scan, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_results).pack(side=tk.LEFT, padx=(0, 10))

        # Progress section
        progress_group = ttk.LabelFrame(main_frame, text="Scan Progress", padding="10")
        progress_group.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_group.columnconfigure(0, weight=1)

        # Progress bar with percentage
        progress_frame = ttk.Frame(progress_group)
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.scan_progress, maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1, padx=(5, 0))

        # Real-time statistics
        stats_frame = ttk.Frame(progress_group)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        ttk.Label(stats_frame, text="Elapsed:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.scan_time, font=('Consolas', 10)).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(stats_frame, text="Targets:").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.targets_scanned, font=('Consolas', 10)).grid(row=0, column=3, sticky=tk.W, padx=(5, 20))

        ttk.Label(stats_frame, text="Open Ports:").grid(row=0, column=4, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.ports_found, font=('Consolas', 10), foreground='green').grid(row=0, column=5, sticky=tk.W, padx=(5, 0))

    def setup_results_tab(self):
        """Setup enhanced results tab with filtering and grouping"""
        results_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(results_frame, text="Scan Results")

        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)

        # Filter and search frame
        filter_frame = ttk.LabelFrame(results_frame, text="Filter & Search", padding="5")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(2, weight=1)

        ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_results)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        ttk.Label(filter_frame, text="Show:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.filter_state = ttk.Combobox(filter_frame, values=["All", "Open", "Closed", "Filtered"], state="readonly", width=10)
        self.filter_state.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        self.filter_state.set("All")
        self.filter_state.bind('<<ComboboxSelected>>', lambda e: self.filter_results())

        ttk.Button(filter_frame, text="Group by Host", command=self.group_by_host).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Group by Service", command=self.group_by_service).grid(row=0, column=5, padx=5)

        # Results treeview with enhanced columns
        tree_frame = ttk.Frame(results_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('Target', 'Port', 'State', 'Service', 'Protocol', 'Version', 'Banner')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=20)

        # Configure columns
        self.results_tree.column('#0', width=30, minwidth=30, stretch=False)  # Tree column
        self.results_tree.heading('#0', text='')

        column_widths = {'Target': 130, 'Port': 60, 'State': 70, 'Service': 100, 'Protocol': 70, 'Version': 120, 'Banner': 200}
        for col in columns:
            self.results_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.results_tree.column(col, width=column_widths.get(col, 100), minwidth=50)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Context menu for results
        self.setup_context_menu()

    def setup_statistics_tab(self):
        """Setup statistics and analytics tab"""
        stats_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(stats_frame, text="Statistics")

        # Create sections for different statistics
        # Scan summary
        summary_group = ttk.LabelFrame(stats_frame, text="Scan Summary", padding="10")
        summary_group.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.summary_text = tk.Text(summary_group, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Top services
        services_group = ttk.LabelFrame(stats_frame, text="Top Services Found", padding="10")
        services_group.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.services_tree = ttk.Treeview(services_group, columns=('Service', 'Count', 'Percentage'), show='headings', height=10)
        self.services_tree.heading('Service', text='Service')
        self.services_tree.heading('Count', text='Count')
        self.services_tree.heading('Percentage', text='%')
        self.services_tree.pack(fill=tk.BOTH, expand=True)

        # Host summary
        hosts_group = ttk.LabelFrame(stats_frame, text="Host Summary", padding="10")
        hosts_group.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))

        self.hosts_tree = ttk.Treeview(hosts_group, columns=('Host', 'Open Ports', 'Services'), show='headings', height=10)
        self.hosts_tree.heading('Host', text='Host')
        self.hosts_tree.heading('Open Ports', text='Open Ports')
        self.hosts_tree.heading('Services', text='Services')
        self.hosts_tree.pack(fill=tk.BOTH, expand=True)

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.rowconfigure(1, weight=1)

    def setup_log_tab(self):
        """Setup logging and debug tab"""
        log_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(log_frame, text="Scan Log")

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)

        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)

        self.auto_scroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Auto-scroll", variable=self.auto_scroll).pack(side=tk.LEFT, padx=(20, 0))

        # Log text area
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_text_frame.columnconfigure(0, weight=1)
        log_text_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_text_frame, wrap=tk.WORD, font=('Consolas', 9), state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        log_scroll = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def setup_status_bar(self):
        """Setup enhanced status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

        # Status sections
        ttk.Label(status_frame, text="Status:", font=('Arial', 8)).pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT, padx=(5, 20))

        # Separator
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Statistics in status bar
        self.result_count_label = ttk.Label(status_frame, text="Results: 0", font=('Arial', 8))
        self.result_count_label.pack(side=tk.LEFT, padx=(5, 20))

        self.live_hosts_label = ttk.Label(status_frame, text="Live Hosts: 0", font=('Arial', 8))
        self.live_hosts_label.pack(side=tk.LEFT, padx=(0, 20))

        # Time display
        self.time_label = ttk.Label(status_frame, text=datetime.now().strftime("%H:%M:%S"), font=('Arial', 8))
        self.time_label.pack(side=tk.RIGHT)

    def setup_context_menu(self):
        """Setup context menu for results tree"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy IP", command=self.copy_ip)
        self.context_menu.add_command(label="Copy Port", command=self.copy_port)
        self.context_menu.add_command(label="Copy Row", command=self.copy_row)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Scan This Host", command=self.scan_selected_host)
        self.context_menu.add_command(label="Whois Lookup", command=self.whois_lookup)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove Entry", command=self.remove_selected)

        self.results_tree.bind("<Button-3>", self.show_context_menu)  # Right click

    def log_message(self, message, level="INFO"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)

        # Color coding for different log levels
        if level == "ERROR":
            self.log_text.tag_add("error", f"end-{len(formatted_message)}c", "end-1c")
            self.log_text.tag_config("error", foreground="red")
        elif level == "WARNING":
            self.log_text.tag_add("warning", f"end-{len(formatted_message)}c", "end-1c")
            self.log_text.tag_config("warning", foreground="orange")
        elif level == "SUCCESS":
            self.log_text.tag_add("success", f"end-{len(formatted_message)}c", "end-1c")
            self.log_text.tag_config("success", foreground="green")

        self.log_text.config(state=tk.DISABLED)

        if self.auto_scroll.get():
            self.log_text.see(tk.END)

    def set_port_preset(self, preset):
        """Set predefined port ranges"""
        presets = {
            "top100": "7,9,13,21-23,25-26,37,53,79-81,88,106,110-111,113,119,135,139,143-144,179,199,389,427,443-445,465,513-515,543-544,548,554,587,631,646,873,990,993,995,1025-1029,1110,1433,1720,1723,1755,1900,2000-2001,2049,2121,2717,3000,3128,3306,3389,3986,4899,5000,5009,5051,5060,5101,5190,5357,5432,5631,5666,5800,5900,6000-6001,6646,7070,8000,8008-8009,8080-8081,8443,8888,9100,9999-10000,32768,49152-49157",
            "top1000": "1-1000",
            "web": "80,443,8000,8008,8080,8081,8443,8888,9000,9080,9443",
            "database": "1433,1521,3306,5432,6379,27017,50000",
            "mail": "25,110,143,465,587,993,995",
            "remote": "22,23,3389,5900,5901",
            "all": "1-65535"
        }
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, presets.get(preset, ""))

    def set_local_network(self):
        """Set target to local network"""
        try:
            # Get local IP and assume /24 network
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            network = ".".join(local_ip.split(".")[:-1]) + ".0/24"
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, network)
        except Exception:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, "192.168.1.0/24")

    def set_localhost(self):
        """Set target to localhost"""
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, "127.0.0.1")

    def load_targets_file(self):
        """Load targets from file"""
        filename = filedialog.askopenfilename(
            title="Load Targets",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    targets = [line.strip() for line in f if line.strip()]
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, ",".join(targets))
                self.log_message(f"Loaded {len(targets)} targets from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load targets: {str(e)}")

    def show_context_menu(self, event):
        """Show context menu for results tree"""
        item = self.results_tree.identify_row(event.y)
        if item:
            self.results_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_ip(self):
        """Copy selected IP to clipboard"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            ip = self.results_tree.item(item)['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.log_message(f"Copied IP: {ip}")

    def copy_port(self):
        """Copy selected port to clipboard"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            port = self.results_tree.item(item)['values'][1]
            self.root.clipboard_clear()
            self.root.clipboard_append(str(port))
            self.log_message(f"Copied port: {port}")

    def copy_row(self):
        """Copy entire row to clipboard"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            values = self.results_tree.item(item)['values']
            row_text = "\t".join(str(v) for v in values)
            self.root.clipboard_clear()
            self.root.clipboard_append(row_text)
            self.log_message("Copied row to clipboard")

    def scan_selected_host(self):
        """Start new scan on selected host"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            target = self.results_tree.item(item)['values'][0]
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, target)
            self.notebook.select(0)  # Switch to main tab

    def whois_lookup(self):
        """Perform whois lookup on selected IP"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            target = self.results_tree.item(item)['values'][0]
            # This would open a dialog with whois information
            messagebox.showinfo("Whois Lookup", f"Whois lookup for {target}\n(Feature to be implemented)")

    def remove_selected(self):
        """Remove selected result"""
        selection = self.results_tree.selection()
        if selection:
            for item in selection:
                self.results_tree.delete(item)
            self.update_result_count()

    def filter_results(self, *args):
        """Filter results based on search and state"""
        search_term = self.search_var.get().lower()
        state_filter = self.filter_state.get()

        # This is a simplified filter implementation
        # In a real implementation, you'd hide/show tree items based on criteria
        pass

    def sort_treeview(self, column):
        """Sort treeview by column"""
        data = [(self.results_tree.item(child)['values'], child) for child in self.results_tree.get_children('')]

        # Determine sort order
        col_index = ['Target', 'Port', 'State', 'Service', 'Protocol', 'Version', 'Banner'].index(column)

        # Sort data
        if column == 'Port':
            data.sort(key=lambda x: int(x[0][col_index]) if str(x[0][col_index]).isdigit() else 0)
        else:
            data.sort(key=lambda x: str(x[0][col_index]).lower())

        # Rearrange items
        for index, (values, child) in enumerate(data):
            self.results_tree.move(child, '', index)

    def group_by_host(self):
        """Group results by host"""
        # Clear current tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Group results by host
        host_groups = {}
        for result in self.scanner.get_results():
            host = result['target']
            if host not in host_groups:
                host_groups[host] = []
            host_groups[host].append(result)

        # Add grouped items to tree
        for host, results in host_groups.items():
            host_item = self.results_tree.insert('', 'end', text=f"📡 {host} ({len(results)} ports)", values=('', '', '', '', '', '', ''))
            for result in results:
                self.results_tree.insert(host_item, 'end', values=(
                    result['target'], result['port'], result['state'],
                    result['service'], result.get('protocol', 'tcp'), '', ''
                ))

    def group_by_service(self):
        """Group results by service"""
        # Clear current tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Group results by service
        service_groups = {}
        for result in self.scanner.get_results():
            service = result['service']
            if service not in service_groups:
                service_groups[service] = []
            service_groups[service].append(result)

        # Add grouped items to tree
        for service, results in service_groups.items():
            service_item = self.results_tree.insert('', 'end', text=f"🔧 {service} ({len(results)} instances)", values=('', '', '', '', '', '', ''))
            for result in results:
                self.results_tree.insert(service_item, 'end', values=(
                    result['target'], result['port'], result['state'],
                    result['service'], result.get('protocol', 'tcp'), '', ''
                ))

    def start_time_updater(self):
        """Start the time updater for elapsed time"""
        def update_time():
            while True:
                if self.is_scanning and self.scan_start_time:
                    elapsed = time.time() - self.scan_start_time
                    hours, remainder = divmod(elapsed, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self.scan_time.set(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

                # Update clock
                current_time = datetime.now().strftime("%H:%M:%S")
                self.time_label.config(text=current_time)

                time.sleep(1)

        timer_thread = threading.Thread(target=update_time, daemon=True)
        timer_thread.start()

    def start_scan(self):
        """Enhanced start scan with better error handling and logging"""
        if not self.validate_inputs():
            return

        self.is_scanning = True
        self.scan_start_time = time.time()

        # Update UI state
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)

        self.status_text.set("Initializing scan...")
        self.scan_progress.set(0)
        self.scan_time.set("00:00:00")

        # Clear previous results
        self.clear_results()

        # Get parameters
        targets = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()
        scan_type = self.scan_type.get()
        max_workers = int(self.thread_count.get())
        timeout = float(self.timeout.get())

        # Log scan start
        self.log_message(f"Starting {scan_type} scan on {targets}", "INFO")
        self.log_message(f"Ports: {ports}", "INFO")
        self.log_message(f"Threads: {max_workers}, Timeout: {timeout}s", "INFO")

        # Start scan thread
        self.scan_thread = threading.Thread(
            target=self.run_scan,
            args=(targets, ports, scan_type, max_workers, timeout),
            daemon=True
        )
        self.scan_thread.start()

    def run_scan(self, targets, ports, scan_type, max_workers, timeout):
        """Enhanced scan execution with better progress tracking"""
        try:
            # Expand targets and ports
            target_list = self.scanner.expand_targets(targets)
            port_list = self.scanner.parse_port_range(ports)

            # Update scan statistics
            self.scan_stats['total_targets'] = len(target_list)
            self.scan_stats['total_ports'] = len(port_list)
            self.scan_stats['scanned_combinations'] = 0
            self.scan_stats['open_ports'] = 0
            self.scan_stats['live_hosts'].clear()

            total_combinations = len(target_list) * len(port_list)
            self.status_text.set(f"Scanning {len(target_list)} targets, {len(port_list)} ports ({total_combinations:,} combinations)...")

            # Start scan with enhanced callback
            results = self.scanner.start_scan(
                target_list, port_list, scan_type, max_workers, timeout,
                self.enhanced_scan_callback
            )

            if self.is_scanning:
                elapsed = time.time() - self.scan_start_time
                self.status_text.set(f"Scan completed in {elapsed:.1f}s. Found {len(results)} open ports.")
                self.log_message(f"Scan completed. {len(results)} open ports found in {elapsed:.1f} seconds", "SUCCESS")
                self.scan_progress.set(100)
                self.update_statistics()
            else:
                self.log_message("Scan stopped by user", "WARNING")
                self.status_text.set("Scan stopped by user.")

        except Exception as e:
            error_msg = f"Error during scan: {str(e)}"
            self.status_text.set(error_msg)
            self.log_message(error_msg, "ERROR")
            messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{str(e)}")
        finally:
            self.scan_finished()

    def enhanced_scan_callback(self, callback_type, data=None):
        """Enhanced callback with better progress tracking"""
        if callback_type == 'result':
            self.root.after(0, self.add_enhanced_result, data)
            self.scan_stats['open_ports'] += 1
            self.scan_stats['live_hosts'].add(data['target'])
        elif callback_type == 'progress':
            self.root.after(0, self.update_enhanced_progress, data)
        elif callback_type == 'error':
            self.root.after(0, lambda: self.log_message(f"Scan error: {data}", "ERROR"))

    def add_enhanced_result(self, result):
        """Add result with enhanced information"""
        # Add to main results tree
        self.results_tree.insert('', 'end', values=(
            result['target'],
            result['port'],
            result['state'],
            result['service'],
            result.get('protocol', 'tcp'),
            result.get('version', ''),
            result.get('banner', '')
        ))

        self.update_result_count()
        self.ports_found.set(self.scan_stats['open_ports'])
        self.targets_scanned.set(len(self.scan_stats['live_hosts']))

        # Log the finding
        self.log_message(f"Found open port: {result['target']}:{result['port']} ({result['service']})", "SUCCESS")

    def update_enhanced_progress(self, progress):
        """Update progress with percentage display"""
        self.scan_progress.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")

    def update_result_count(self):
        """Update result count display"""
        count = len(self.results_tree.get_children())
        self.result_count_label.config(text=f"Results: {count}")

    def update_statistics(self):
        """Update statistics tab with scan results"""
        # Update summary
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)

        elapsed = time.time() - self.scan_start_time if self.scan_start_time else 0
        summary = f"""Scan Summary:
Target Count: {self.scan_stats['total_targets']:,}
Port Count: {self.scan_stats['total_ports']:,}
Total Combinations: {self.scan_stats['total_targets'] * self.scan_stats['total_ports']:,}
Live Hosts: {len(self.scan_stats['live_hosts'])}
Open Ports Found: {self.scan_stats['open_ports']}
Elapsed Time: {elapsed:.2f} seconds
Scan Rate: {(self.scan_stats['total_targets'] * self.scan_stats['total_ports']) / max(elapsed, 0.1):.0f} ports/sec
"""
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)

    def quick_scan(self):
        """Start quick scan with top 100 ports"""
        self.set_port_preset("top100")
        self.scan_type.set("fast")
        self.thread_count.set("200")
        self.timeout.set("0.5")
        self.start_scan()

    def full_scan(self):
        """Start full port scan"""
        self.set_port_preset("all")
        self.scan_type.set("SYN")
        if messagebox.askyesno("Full Scan Warning",
                              "Full scan will scan all 65535 ports and may take a long time.\n"
                              "This scan requires administrator privileges.\n"
                              "Continue?"):
            self.start_scan()

    def pause_scan(self):
        """Pause/resume scan functionality"""
        # This would require more complex implementation with the scanner
        messagebox.showinfo("Feature", "Pause/Resume functionality will be implemented in future version")

    def ping_sweep(self):
        """Enhanced ping sweep with progress tracking"""
        if self.is_scanning:
            messagebox.showwarning("Warning", "A scan is already in progress")
            return

        targets = self.target_entry.get().strip()
        if not targets:
            messagebox.showerror("Error", "Please enter target IP addresses")
            return

        self.is_scanning = True
        self.scan_start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_text.set("Performing ping sweep...")
        self.log_message("Starting ping sweep", "INFO")

        def run_ping_sweep():
            try:
                target_list = self.scanner.expand_targets(targets)
                self.log_message(f"Ping sweep on {len(target_list)} targets", "INFO")
                live_hosts = self.scanner.ping_sweep(target_list, self.ping_callback)

                if self.is_scanning:
                    self.status_text.set(f"Ping sweep completed. {len(live_hosts)} hosts alive.")
                    self.log_message(f"Ping sweep completed. Found {len(live_hosts)} live hosts", "SUCCESS")

                    # Show results dialog
                    if live_hosts:
                        result_text = f"Live hosts found ({len(live_hosts)}):\n\n" + "\n".join(live_hosts)
                        self.show_text_dialog("Ping Sweep Results", result_text)
                    else:
                        messagebox.showinfo("Ping Sweep Results", "No live hosts found")
            except Exception as e:
                error_msg = f"Ping sweep error: {str(e)}"
                self.status_text.set(error_msg)
                self.log_message(error_msg, "ERROR")
            finally:
                self.scan_finished()

        threading.Thread(target=run_ping_sweep, daemon=True).start()

    def ping_callback(self, callback_type, data):
        """Handle ping sweep callbacks with logging"""
        if callback_type == 'ping_result':
            self.root.after(0, lambda: self.log_message(f"Live host: {data['target']}", "SUCCESS"))

    def stop_scan(self):
        """Stop current scan with cleanup"""
        self.is_scanning = False
        self.scanner.stop_scan()
        self.status_text.set("Stopping scan...")
        self.log_message("Scan stop requested", "WARNING")

    def scan_finished(self):
        """Handle scan completion with UI cleanup"""
        self.is_scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)

    def clear_results(self):
        """Clear all results and reset counters"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.scan_stats = {
            'total_targets': 0, 'total_ports': 0, 'scanned_combinations': 0,
            'open_ports': 0, 'live_hosts': set()
        }

        self.result_count_label.config(text="Results: 0")
        self.targets_scanned.set(0)
        self.ports_found.set(0)
        self.scan_progress.set(0)
        self.scan_time.set("00:00:00")
        self.status_text.set("Results cleared")
        self.log_message("Results cleared", "INFO")

    def clear_log(self):
        """Clear the log text area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Log saved to {filename}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {str(e)}")

    def validate_inputs(self):
        """Enhanced input validation with detailed feedback"""
        targets = self.target_entry.get().strip()
        ports = self.port_entry.get().strip()

        if not targets:
            messagebox.showerror("Error", "Please enter target IP addresses or hostnames")
            return False

        if not ports:
            messagebox.showerror("Error", "Please enter port numbers or ranges")
            return False

        # Validate targets
        target_list = [t.strip() for t in targets.split(',')]
        valid_targets = 0

        for target in target_list:
            if self.scanner.validate_target(target):
                valid_targets += 1
            else:
                self.log_message(f"Invalid target: {target}", "WARNING")

        if valid_targets == 0:
            messagebox.showerror("Error", "No valid targets specified")
            return False

        # Validate ports
        try:
            port_list = self.scanner.parse_port_range(ports)
            if not port_list:
                messagebox.showerror("Error", "No valid ports specified")
                return False

            if len(port_list) > 10000:
                if not messagebox.askyesno("Large Port Range",
                                         f"You specified {len(port_list)} ports. This may take a long time.\n"
                                         "Continue?"):
                    return False

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid port specification: {str(e)}")
            return False

        return True

    def show_text_dialog(self, title, text):
        """Show text in a dialog window"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x400")

        text_widget = tk.Text(dialog, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)

    def show_port_lookup(self):
        """Show port lookup tool"""
        self.port_lookup_dialog = tk.Toplevel(self.root)
        self.port_lookup_dialog.title("Port Lookup Tool")
        self.port_lookup_dialog.geometry("800x600")
        self.port_lookup_dialog.resizable(True, True)
        
        # Center the dialog
        self.port_lookup_dialog.transient(self.root)
        self.port_lookup_dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.port_lookup_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Port Lookup Tool", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Port Lookup Tab
        lookup_frame = ttk.Frame(notebook, padding="10")
        notebook.add(lookup_frame, text="Port Lookup")
        self.setup_port_lookup(lookup_frame)
        
        # Port Categories Tab
        categories_frame = ttk.Frame(notebook, padding="10")
        notebook.add(categories_frame, text="Port Categories")
        self.setup_port_categories(categories_frame)
        
        # Common Ports Tab
        common_frame = ttk.Frame(notebook, padding="10")
        notebook.add(common_frame, text="Common Ports")
        self.setup_common_ports(common_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close", 
                  command=self.port_lookup_dialog.destroy).pack(pady=(10, 0))

    def show_network_calc(self):
        """Show network calculator tool"""
        self.network_calc_dialog = tk.Toplevel(self.root)
        self.network_calc_dialog.title("Network Calculator")
        self.network_calc_dialog.geometry("700x600")
        self.network_calc_dialog.resizable(True, True)
        
        # Center the dialog
        self.network_calc_dialog.transient(self.root)
        self.network_calc_dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.network_calc_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Network Calculator", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # CIDR Calculator Tab
        cidr_frame = ttk.Frame(notebook, padding="10")
        notebook.add(cidr_frame, text="CIDR Calculator")
        self.setup_cidr_calculator(cidr_frame)
        
        # Subnet Calculator Tab
        subnet_frame = ttk.Frame(notebook, padding="10")
        notebook.add(subnet_frame, text="Subnet Calculator")
        self.setup_subnet_calculator(subnet_frame)
        
        # IP Range Calculator Tab
        range_frame = ttk.Frame(notebook, padding="10")
        notebook.add(range_frame, text="IP Range Calculator")
        self.setup_range_calculator(range_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close", 
                  command=self.network_calc_dialog.destroy).pack(pady=(10, 0))

    def setup_cidr_calculator(self, parent):
        """Setup CIDR calculator tab"""
        # Input section
        input_frame = ttk.LabelFrame(parent, text="CIDR Network Analysis", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # CIDR input
        ttk.Label(input_frame, text="CIDR Network (e.g., 192.168.1.0/24):").pack(anchor=tk.W)
        self.cidr_input = tk.StringVar()
        cidr_entry = ttk.Entry(input_frame, textvariable=self.cidr_input, width=30)
        cidr_entry.pack(fill=tk.X, pady=(5, 10))
        cidr_entry.bind('<KeyRelease>', lambda e: self.calculate_cidr())
        cidr_entry.bind('<Return>', lambda e: self.calculate_cidr())
        cidr_entry.bind('<Control-v>', lambda e: self.paste_from_clipboard(cidr_entry))
        
        # Calculate button
        ttk.Button(input_frame, text="Calculate", 
                  command=self.calculate_cidr).pack(pady=(0, 10))
        
        # Results section
        results_frame = ttk.LabelFrame(parent, text="Network Information", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text with scrollbar and copy button
        results_header_frame = ttk.Frame(results_frame)
        results_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(results_header_frame, text="Results:").pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = ttk.Frame(results_header_frame)
        export_frame.pack(side=tk.RIGHT)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self.export_results(self.cidr_results, "json", "cidr")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export XML", 
                  command=lambda: self.export_results(self.cidr_results, "xml", "cidr")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Copy Results", 
                  command=lambda: self.copy_to_clipboard(self.cidr_results)).pack(side=tk.LEFT)
        
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cidr_results = tk.Text(results_text_frame, wrap=tk.WORD, 
                                   font=('Courier', 9), height=15)
        cidr_scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, 
                                      command=self.cidr_results.yview)
        self.cidr_results.configure(yscrollcommand=cidr_scrollbar.set)
        
        # Bind keyboard shortcuts
        self.cidr_results.bind('<Control-c>', lambda e: self.copy_to_clipboard(self.cidr_results))
        self.cidr_results.bind('<Control-a>', lambda e: self.select_all_text(self.cidr_results))
        
        self.cidr_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cidr_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add help text
        help_text = """CIDR Calculator
================

Enter a CIDR network notation (e.g., 192.168.1.0/24) to analyze:
• Network address and broadcast address
• Usable IP range
• Number of hosts
• Subnet mask
• Wildcard mask
• Network class and type

Examples:
• 192.168.1.0/24     - Class C private network
• 10.0.0.0/8         - Class A private network
• 172.16.0.0/12      - Class B private network
• 8.8.8.0/24         - Public network
"""
        self.cidr_results.insert(tk.END, help_text)
        self.cidr_results.config(state=tk.DISABLED)

    def setup_subnet_calculator(self, parent):
        """Setup subnet calculator tab"""
        # Input section
        input_frame = ttk.LabelFrame(parent, text="Subnet Planning", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Network input
        ttk.Label(input_frame, text="Base Network (CIDR):").pack(anchor=tk.W)
        self.subnet_base = tk.StringVar()
        subnet_entry = ttk.Entry(input_frame, textvariable=self.subnet_base, width=30)
        subnet_entry.pack(fill=tk.X, pady=(5, 10))
        subnet_entry.bind('<Control-v>', lambda e: self.paste_from_clipboard(subnet_entry))
        
        # Number of subnets
        ttk.Label(input_frame, text="Number of Subnets Needed:").pack(anchor=tk.W)
        self.subnet_count = tk.StringVar()
        count_entry = ttk.Entry(input_frame, textvariable=self.subnet_count, width=10)
        count_entry.pack(anchor=tk.W, pady=(5, 10))
        count_entry.bind('<Control-v>', lambda e: self.paste_from_clipboard(count_entry))
        
        # Calculate button
        ttk.Button(input_frame, text="Calculate Subnets", 
                  command=self.calculate_subnets).pack(pady=(0, 10))
        
        # Results section
        results_frame = ttk.LabelFrame(parent, text="Subnet Breakdown", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text with scrollbar and copy button
        results_header_frame = ttk.Frame(results_frame)
        results_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(results_header_frame, text="Results:").pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = ttk.Frame(results_header_frame)
        export_frame.pack(side=tk.RIGHT)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self.export_results(self.subnet_results, "json", "subnet")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export XML", 
                  command=lambda: self.export_results(self.subnet_results, "xml", "subnet")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Copy Results", 
                  command=lambda: self.copy_to_clipboard(self.subnet_results)).pack(side=tk.LEFT)
        
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.subnet_results = tk.Text(results_text_frame, wrap=tk.WORD, 
                                     font=('Courier', 9), height=15)
        subnet_scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, 
                                        command=self.subnet_results.yview)
        self.subnet_results.configure(yscrollcommand=subnet_scrollbar.set)
        
        # Bind keyboard shortcuts
        self.subnet_results.bind('<Control-c>', lambda e: self.copy_to_clipboard(self.subnet_results))
        self.subnet_results.bind('<Control-a>', lambda e: self.select_all_text(self.subnet_results))
        
        self.subnet_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        subnet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add help text
        help_text = """Subnet Calculator
=================

Enter a base network and number of subnets needed.
The calculator will determine:
• Optimal subnet mask for each subnet
• Network addresses for each subnet
• Broadcast addresses for each subnet
• Usable IP ranges for each subnet
• Hosts per subnet

Example:
Base Network: 192.168.1.0/24
Subnets Needed: 4
Result: Four /26 subnets with 62 hosts each
"""
        self.subnet_results.insert(tk.END, help_text)
        self.subnet_results.config(state=tk.DISABLED)

    def setup_range_calculator(self, parent):
        """Setup IP range calculator tab"""
        # Input section
        input_frame = ttk.LabelFrame(parent, text="IP Range Analysis", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP range input
        ttk.Label(input_frame, text="IP Range (e.g., 192.168.1.1-192.168.1.100):").pack(anchor=tk.W)
        self.range_input = tk.StringVar()
        range_entry = ttk.Entry(input_frame, textvariable=self.range_input, width=40)
        range_entry.pack(fill=tk.X, pady=(5, 10))
        range_entry.bind('<KeyRelease>', lambda e: self.calculate_range())
        range_entry.bind('<Return>', lambda e: self.calculate_range())
        range_entry.bind('<Control-v>', lambda e: self.paste_from_clipboard(range_entry))
        
        # Calculate button
        ttk.Button(input_frame, text="Analyze Range", 
                  command=self.calculate_range).pack(pady=(0, 10))
        
        # Results section
        results_frame = ttk.LabelFrame(parent, text="Range Information", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text with scrollbar and copy button
        results_header_frame = ttk.Frame(results_frame)
        results_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(results_header_frame, text="Results:").pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = ttk.Frame(results_header_frame)
        export_frame.pack(side=tk.RIGHT)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self.export_results(self.range_results, "json", "range")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export XML", 
                  command=lambda: self.export_results(self.range_results, "xml", "range")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Copy Results", 
                  command=lambda: self.copy_to_clipboard(self.range_results)).pack(side=tk.LEFT)
        
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.range_results = tk.Text(results_text_frame, wrap=tk.WORD, 
                                    font=('Courier', 9), height=15)
        range_scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, 
                                       command=self.range_results.yview)
        self.range_results.configure(yscrollcommand=range_scrollbar.set)
        
        # Bind keyboard shortcuts
        self.range_results.bind('<Control-c>', lambda e: self.copy_to_clipboard(self.range_results))
        self.range_results.bind('<Control-a>', lambda e: self.select_all_text(self.range_results))
        
        self.range_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        range_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add help text
        help_text = """IP Range Calculator
===================

Enter an IP range to analyze:
• Total number of IPs in range
• First and last IP addresses
• Suggested CIDR notation
• Network class and type
• Broadcast and network addresses

Examples:
• 192.168.1.1-192.168.1.100
• 10.0.0.1-10.0.0.50
• 172.16.1.10-172.16.1.20

The calculator will determine the most
efficient CIDR representation for the range.
"""
        self.range_results.insert(tk.END, help_text)
        self.range_results.config(state=tk.DISABLED)

    def calculate_cidr(self):
        """Calculate CIDR network information"""
        cidr_input = self.cidr_input.get().strip()
        
        if not cidr_input:
            return
            
        try:
            import ipaddress
            
            # Parse the network
            network = ipaddress.ip_network(cidr_input, strict=False)
            
            # Calculate network information
            network_addr = str(network.network_address)
            broadcast_addr = str(network.broadcast_address)
            netmask = str(network.netmask)
            wildcard = str(network.hostmask)
            prefix_len = network.prefixlen
            num_hosts = network.num_addresses
            usable_hosts = num_hosts - 2 if num_hosts > 2 else 0
            first_host = str(network.network_address + 1) if usable_hosts > 0 else "N/A"
            last_host = str(network.broadcast_address - 1) if usable_hosts > 0 else "N/A"
            
            # Determine network class
            ip_obj = ipaddress.ip_address(network_addr)
            if isinstance(ip_obj, ipaddress.IPv4Address):
                first_octet = int(str(ip_obj).split('.')[0])
                if first_octet <= 126:
                    network_class = "A"
                elif first_octet <= 191:
                    network_class = "B"
                elif first_octet <= 223:
                    network_class = "C"
                elif first_octet <= 239:
                    network_class = "D (Multicast)"
                else:
                    network_class = "E (Experimental)"
            else:
                network_class = "IPv6"
            
            # Determine if private
            is_private = network.is_private
            is_loopback = network.is_loopback
            is_multicast = network.is_multicast
            is_link_local = network.is_link_local
            
            # Build results
            self.cidr_results.config(state=tk.NORMAL)
            self.cidr_results.delete(1.0, tk.END)
            
            results = f"""CIDR Network Analysis
=====================
Input: {cidr_input}

Network Information:
-------------------
Network Address:     {network_addr}
Broadcast Address:   {broadcast_addr}
Subnet Mask:         {netmask}
Wildcard Mask:       {wildcard}
Prefix Length:       /{prefix_len}
Total Addresses:     {num_hosts:,}
Usable Hosts:        {usable_hosts:,}

Host Range:
-----------
First Usable:        {first_host}
Last Usable:         {last_host}

Network Classification:
-----------------------
Class:               {network_class}
Private:             {'Yes' if is_private else 'No'}
Loopback:            {'Yes' if is_loopback else 'No'}
Multicast:           {'Yes' if is_multicast else 'No'}
Link Local:          {'Yes' if is_link_local else 'No'}

Binary Representation:
----------------------
Network Address:     {self._ip_to_binary(network_addr)}
Subnet Mask:         {self._ip_to_binary(netmask)}

Hex Representation:
-------------------
Network Address:     {self._ip_to_hex(network_addr)}
Subnet Mask:         {self._ip_to_hex(netmask)}
"""
            
            self.cidr_results.insert(tk.END, results)
            self.cidr_results.config(state=tk.DISABLED)
            self.cidr_results.see(1.0)
            
        except Exception as e:
            self.cidr_results.config(state=tk.NORMAL)
            self.cidr_results.delete(1.0, tk.END)
            self.cidr_results.insert(tk.END, f"Error: {str(e)}")
            self.cidr_results.config(state=tk.DISABLED)

    def calculate_subnets(self):
        """Calculate subnet breakdown"""
        base_network = self.subnet_base.get().strip()
        subnet_count = self.subnet_count.get().strip()
        
        if not base_network or not subnet_count:
            return
            
        try:
            import ipaddress
            import math
            
            # Parse inputs
            base_net = ipaddress.ip_network(base_network, strict=False)
            num_subnets = int(subnet_count)
            
            # Calculate required bits for subnets
            bits_needed = math.ceil(math.log2(num_subnets))
            new_prefix = base_net.prefixlen + bits_needed
            
            if new_prefix > 32:
                raise ValueError("Too many subnets requested for the base network")
            
            # Calculate subnet size
            subnet_size = 2 ** (32 - new_prefix)
            
            self.subnet_results.config(state=tk.NORMAL)
            self.subnet_results.delete(1.0, tk.END)
            
            results = f"""Subnet Planning Results
========================
Base Network:        {base_network}
Subnets Requested:   {num_subnets}
Bits Needed:         {bits_needed}
New Prefix:          /{new_prefix}
Hosts per Subnet:    {subnet_size - 2:,}

Subnet Breakdown:
================
"""
            
            # Generate each subnet
            current_network = base_net.network_address
            for i in range(num_subnets):
                subnet = ipaddress.ip_network(f"{current_network}/{new_prefix}", strict=False)
                
                results += f"""
Subnet {i + 1}:
  Network:     {subnet.network_address}
  Broadcast:   {subnet.broadcast_address}
  Range:       {subnet.network_address + 1} - {subnet.broadcast_address - 1}
  Hosts:       {subnet.num_addresses - 2:,}
  CIDR:        {subnet}
"""
                
                current_network += subnet_size
            
            # Summary
            results += f"""
Summary:
--------
Total Subnets:       {num_subnets}
Hosts per Subnet:    {subnet_size - 2:,}
Total Hosts:         {(subnet_size - 2) * num_subnets:,}
Wasted Addresses:    {base_net.num_addresses - (subnet_size * num_subnets):,}
"""
            
            self.subnet_results.insert(tk.END, results)
            self.subnet_results.config(state=tk.DISABLED)
            self.subnet_results.see(1.0)
            
        except Exception as e:
            self.subnet_results.config(state=tk.NORMAL)
            self.subnet_results.delete(1.0, tk.END)
            self.subnet_results.insert(tk.END, f"Error: {str(e)}")
            self.subnet_results.config(state=tk.DISABLED)

    def calculate_range(self):
        """Calculate IP range information"""
        range_input = self.range_input.get().strip()
        
        if not range_input:
            return
            
        try:
            import ipaddress
            import math
            
            # Parse IP range
            if '-' not in range_input:
                raise ValueError("Range must be in format: IP1-IP2")
            
            start_ip, end_ip = range_input.split('-', 1)
            start_ip = start_ip.strip()
            end_ip = end_ip.strip()
            
            # Convert to IP objects
            start_addr = ipaddress.ip_address(start_ip)
            end_addr = ipaddress.ip_address(end_ip)
            
            if start_addr > end_addr:
                raise ValueError("Start IP must be less than or equal to end IP")
            
            # Calculate range information
            total_ips = int(end_addr) - int(start_addr) + 1
            
            # Find optimal CIDR
            import math
            bits_needed = math.ceil(math.log2(total_ips))
            optimal_prefix = 32 - bits_needed
            
            # Try to find a network that contains this range
            optimal_network = None
            for prefix in range(optimal_prefix, 33):
                try:
                    # Find the network that contains start_ip
                    network = ipaddress.ip_network(f"{start_ip}/{prefix}", strict=False)
                    if end_addr <= network.broadcast_address:
                        optimal_network = network
                        break
                except:
                    continue
            
            self.range_results.config(state=tk.NORMAL)
            self.range_results.delete(1.0, tk.END)
            
            # Determine network class
            first_octet = int(str(start_addr).split('.')[0])
            if first_octet <= 126:
                network_class = "A"
            elif first_octet <= 191:
                network_class = "B"
            elif first_octet <= 223:
                network_class = "C"
            elif first_octet <= 239:
                network_class = "D (Multicast)"
            else:
                network_class = "E (Experimental)"
            
            results = f"""IP Range Analysis
=================
Range:               {range_input}
Start IP:            {start_addr}
End IP:              {end_addr}
Total IPs:           {total_ips:,}

Network Information:
-------------------
Network Class:       {network_class}
Private:             {'Yes' if start_addr.is_private else 'No'}
Loopback:            {'Yes' if start_addr.is_loopback else 'No'}
Multicast:           {'Yes' if start_addr.is_multicast else 'No'}
Link Local:          {'Yes' if start_addr.is_link_local else 'No'}

Binary Representation:
----------------------
Start IP:            {self._ip_to_binary(str(start_addr))}
End IP:              {self._ip_to_binary(str(end_addr))}

Hex Representation:
-------------------
Start IP:            {self._ip_to_hex(str(start_addr))}
End IP:              {self._ip_to_hex(str(end_addr))}
"""
            
            if optimal_network:
                results += f"""
Optimal CIDR Network:
--------------------
Network:             {optimal_network}
Network Address:     {optimal_network.network_address}
Broadcast Address:   {optimal_network.broadcast_address}
Subnet Mask:         {optimal_network.netmask}
Total Addresses:     {optimal_network.num_addresses:,}
Usable Hosts:        {optimal_network.num_addresses - 2:,}

Range Efficiency:
----------------
IPs in Range:        {total_ips:,}
IPs in Network:      {optimal_network.num_addresses:,}
Efficiency:          {(total_ips / optimal_network.num_addresses) * 100:.1f}%
Wasted IPs:          {optimal_network.num_addresses - total_ips:,}
"""
            
            self.range_results.insert(tk.END, results)
            self.range_results.config(state=tk.DISABLED)
            self.range_results.see(1.0)
            
        except Exception as e:
            self.range_results.config(state=tk.NORMAL)
            self.range_results.delete(1.0, tk.END)
            self.range_results.insert(tk.END, f"Error: {str(e)}")
            self.range_results.config(state=tk.DISABLED)

    def _ip_to_binary(self, ip_str):
        """Convert IP address to binary representation"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip_str)
            if isinstance(ip_obj, ipaddress.IPv4Address):
                return '.'.join(format(int(octet), '08b') for octet in str(ip_obj).split('.'))
            else:
                return ip_obj.exploded
        except:
            return "Invalid IP"

    def _ip_to_hex(self, ip_str):
        """Convert IP address to hexadecimal representation"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip_str)
            if isinstance(ip_obj, ipaddress.IPv4Address):
                return '.'.join(format(int(octet), '02X') for octet in str(ip_obj).split('.'))
            else:
                return ip_obj.exploded
        except:
            return "Invalid IP"

    def copy_to_clipboard(self, text_widget):
        """Copy text from a text widget to clipboard"""
        try:
            # Get selected text or all text if nothing is selected
            if text_widget.tag_ranges(tk.SEL):
                # Text is selected
                selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                # No text selected, copy all
                selected_text = text_widget.get(1.0, tk.END).strip()
            
            if selected_text:
                # Clear clipboard and set new content
                text_widget.clipboard_clear()
                text_widget.clipboard_append(selected_text)
                
                # Show brief feedback (optional)
                self.show_copy_feedback()
            else:
                messagebox.showwarning("Copy", "No text to copy")
                
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy text: {str(e)}")

    def paste_from_clipboard(self, entry_widget):
        """Paste text from clipboard to an entry widget"""
        try:
            # Get clipboard content
            clipboard_content = entry_widget.clipboard_get()
            
            if clipboard_content:
                # Clear current selection and insert clipboard content
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, clipboard_content)
                
                # Show brief feedback (optional)
                self.show_paste_feedback()
            else:
                messagebox.showwarning("Paste", "Clipboard is empty")
                
        except tk.TclError:
            messagebox.showwarning("Paste", "Clipboard is empty or contains non-text data")
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste text: {str(e)}")

    def select_all_text(self, text_widget):
        """Select all text in a text widget"""
        try:
            text_widget.tag_add(tk.SEL, "1.0", tk.END)
            text_widget.mark_set(tk.INSERT, "1.0")
            text_widget.see(tk.INSERT)
            return "break"  # Prevent default behavior
        except Exception:
            return None

    def show_copy_feedback(self):
        """Show brief feedback that copy operation succeeded"""
        # This is a simple feedback - you could enhance it with a status bar or toast notification
        pass

    def show_paste_feedback(self):
        """Show brief feedback that paste operation succeeded"""
        # This is a simple feedback - you could enhance it with a status bar or toast notification
        pass

    def export_results(self, text_widget, format_type, data_type):
        """Export results from text widget to JSON or XML file"""
        try:
            from tkinter import filedialog
            import json
            import xml.etree.ElementTree as ET
            from datetime import datetime
            
            # Get the text content
            content = text_widget.get(1.0, tk.END).strip()
            if not content:
                messagebox.showwarning("Export", "No content to export")
                return
            
            # Generate filename based on data type and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"mascanner_{data_type}_{timestamp}.{format_type}"
            
            # Ask user for file location
            if format_type == "json":
                filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
            else:  # xml
                filetypes = [("XML files", "*.xml"), ("All files", "*.*")]
            
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=filetypes,
                initialname=default_filename,
                title=f"Export {data_type.title()} Results"
            )
            
            if not filename:
                return  # User cancelled
            
            # Prepare data for export
            export_data = self.prepare_export_data(content, data_type, format_type)
            
            # Write file based on format
            if format_type == "json":
                self.export_to_json(export_data, filename)
            else:  # xml
                self.export_to_xml(export_data, filename)
            
            messagebox.showinfo("Export", f"Results exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")

    def prepare_export_data(self, content, data_type, format_type):
        """Prepare data structure for export"""
        from datetime import datetime
        
        base_data = {
            "export_info": {
                "tool": "MaScanner Advanced GUI",
                "data_type": data_type,
                "export_format": format_type,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            },
            "raw_content": content
        }
        
        # Parse content based on data type for structured export
        if data_type in ["cidr", "subnet", "range"]:
            base_data["parsed_data"] = self.parse_network_data(content, data_type)
        elif data_type in ["port", "categories", "common_ports"]:
            base_data["parsed_data"] = self.parse_port_data(content, data_type)
        
        return base_data

    def parse_network_data(self, content, data_type):
        """Parse network calculation results into structured data"""
        try:
            import ipaddress
            import re
            
            parsed = {"data_type": data_type}
            
            if data_type == "cidr":
                # Extract CIDR information
                lines = content.split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().replace(' ', '_').lower()
                        value = value.strip()
                        if key and value != 'N/A':
                            parsed[key] = value
                            
            elif data_type == "subnet":
                # Extract subnet information
                parsed["subnets"] = []
                lines = content.split('\n')
                current_subnet = {}
                for line in lines:
                    if line.strip().startswith('Subnet'):
                        if current_subnet:
                            parsed["subnets"].append(current_subnet)
                        current_subnet = {"name": line.strip()}
                    elif ':' in line and current_subnet:
                        key, value = line.strip().split(':', 1)
                        key = key.strip().replace(' ', '_').lower()
                        value = value.strip()
                        if key and value:
                            current_subnet[key] = value
                if current_subnet:
                    parsed["subnets"].append(current_subnet)
                    
            elif data_type == "range":
                # Extract range information
                lines = content.split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().replace(' ', '_').lower()
                        value = value.strip()
                        if key and value != 'N/A':
                            parsed[key] = value
            
            return parsed
            
        except Exception as e:
            return {"parse_error": str(e)}

    def parse_port_data(self, content, data_type):
        """Parse port information into structured data"""
        try:
            parsed = {"data_type": data_type}
            
            if data_type == "port":
                # Extract port information
                lines = content.split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().replace(' ', '_').lower()
                        value = value.strip()
                        if key and value:
                            parsed[key] = value
                            
            elif data_type in ["categories", "common_ports"]:
                # Extract reference information
                parsed["sections"] = []
                lines = content.split('\n')
                current_section = {}
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('=') and not line.startswith('-'):
                        if line.isupper() and ':' in line:
                            # New section header
                            if current_section:
                                parsed["sections"].append(current_section)
                            current_section = {"title": line, "items": []}
                        elif line.startswith('•') and current_section:
                            # Item in current section
                            current_section["items"].append(line[1:].strip())
                
                if current_section:
                    parsed["sections"].append(current_section)
            
            return parsed
            
        except Exception as e:
            return {"parse_error": str(e)}

    def export_to_json(self, data, filename):
        """Export data to JSON file"""
        import json
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def export_to_xml(self, data, filename):
        """Export data to XML file"""
        import xml.etree.ElementTree as ET
        from datetime import datetime
        
        # Create root element
        root = ET.Element("mascanner_export")
        
        # Add export info
        export_info = ET.SubElement(root, "export_info")
        for key, value in data["export_info"].items():
            elem = ET.SubElement(export_info, key)
            elem.text = str(value)
        
        # Add raw content
        raw_content = ET.SubElement(root, "raw_content")
        raw_content.text = data["raw_content"]
        
        # Add parsed data if available
        if "parsed_data" in data:
            parsed_data = ET.SubElement(root, "parsed_data")
            self.dict_to_xml(data["parsed_data"], parsed_data)
        
        # Create tree and write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)  # Pretty print
        tree.write(filename, encoding='utf-8', xml_declaration=True)

    def dict_to_xml(self, data, parent):
        """Convert dictionary to XML elements"""
        if isinstance(data, dict):
            for key, value in data.items():
                elem = ET.SubElement(parent, str(key).replace(' ', '_'))
                if isinstance(value, (dict, list)):
                    self.dict_to_xml(value, elem)
                else:
                    elem.text = str(value) if value is not None else ""
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item_elem = ET.SubElement(parent, "item")
                    self.dict_to_xml(item, item_elem)
                else:
                    elem = ET.SubElement(parent, "item")
                    elem.text = str(item) if item is not None else ""

    def setup_port_lookup(self, parent):
        """Setup port lookup tab"""
        # Input section
        input_frame = ttk.LabelFrame(parent, text="Port Information Lookup", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Port input
        ttk.Label(input_frame, text="Port Number:").pack(anchor=tk.W)
        self.port_input = tk.StringVar()
        port_entry = ttk.Entry(input_frame, textvariable=self.port_input, width=10)
        port_entry.pack(side=tk.LEFT, pady=(5, 10))
        port_entry.bind('<KeyRelease>', lambda e: self.lookup_port())
        port_entry.bind('<Return>', lambda e: self.lookup_port())
        port_entry.bind('<Control-v>', lambda e: self.paste_from_clipboard(port_entry))
        
        # Protocol selection
        ttk.Label(input_frame, text="Protocol:").pack(anchor=tk.W)
        self.protocol_var = tk.StringVar(value="tcp")
        protocol_combo = ttk.Combobox(input_frame, textvariable=self.protocol_var,
                                     values=["tcp", "udp", "tcp/udp"], state="readonly", width=10)
        protocol_combo.pack(side=tk.LEFT, padx=(10, 0), pady=(5, 10))
        
        # Lookup button
        ttk.Button(input_frame, text="Lookup", command=self.lookup_port).pack(side=tk.LEFT, padx=(10, 0), pady=(5, 10))
        
        # Results section
        results_frame = ttk.LabelFrame(parent, text="Port Information", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text with scrollbar and copy button
        results_header_frame = ttk.Frame(results_frame)
        results_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(results_header_frame, text="Results:").pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = ttk.Frame(results_header_frame)
        export_frame.pack(side=tk.RIGHT)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self.export_results(self.port_results, "json", "port")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export XML", 
                  command=lambda: self.export_results(self.port_results, "xml", "port")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Copy Results", 
                  command=lambda: self.copy_to_clipboard(self.port_results)).pack(side=tk.LEFT)
        
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.port_results = tk.Text(results_text_frame, wrap=tk.WORD, 
                                   font=('Courier', 9), height=15)
        port_scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, 
                                      command=self.port_results.yview)
        self.port_results.configure(yscrollcommand=port_scrollbar.set)
        
        # Bind keyboard shortcuts
        self.port_results.bind('<Control-c>', lambda e: self.copy_to_clipboard(self.port_results))
        self.port_results.bind('<Control-a>', lambda e: self.select_all_text(self.port_results))
        
        self.port_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        port_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add help text
        help_text = """Port Lookup Tool
================

Enter a port number (1-65535) to get information about:
• Service name and description
• Protocol (TCP/UDP)
• Common usage
• Security notes
• Related ports

Examples:
• 80     - HTTP web server
• 443    - HTTPS secure web server
• 22     - SSH secure shell
• 25     - SMTP mail server
• 53     - DNS name server
• 3389   - RDP remote desktop

The tool supports both TCP and UDP protocols.
"""
        self.port_results.insert(tk.END, help_text)
        self.port_results.config(state=tk.DISABLED)

    def setup_port_categories(self, parent):
        """Setup port categories tab"""
        # Categories section
        categories_frame = ttk.LabelFrame(parent, text="Port Categories", padding="10")
        categories_frame.pack(fill=tk.BOTH, expand=True)
        
        # Categories text with scrollbar and copy button
        categories_header_frame = ttk.Frame(categories_frame)
        categories_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(categories_header_frame, text="Reference:").pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = ttk.Frame(categories_header_frame)
        export_frame.pack(side=tk.RIGHT)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self.export_results(self.categories_results, "json", "categories")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export XML", 
                  command=lambda: self.export_results(self.categories_results, "xml", "categories")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Copy Reference", 
                  command=lambda: self.copy_to_clipboard(self.categories_results)).pack(side=tk.LEFT)
        
        categories_text_frame = ttk.Frame(categories_frame)
        categories_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.categories_results = tk.Text(categories_text_frame, wrap=tk.WORD, 
                                         font=('Courier', 9), height=20)
        categories_scrollbar = ttk.Scrollbar(categories_text_frame, orient=tk.VERTICAL, 
                                            command=self.categories_results.yview)
        self.categories_results.configure(yscrollcommand=categories_scrollbar.set)
        
        # Bind keyboard shortcuts
        self.categories_results.bind('<Control-c>', lambda e: self.copy_to_clipboard(self.categories_results))
        self.categories_results.bind('<Control-a>', lambda e: self.select_all_text(self.categories_results))
        
        self.categories_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        categories_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load categories
        self.load_port_categories()

    def setup_common_ports(self, parent):
        """Setup common ports tab"""
        # Common ports section
        common_frame = ttk.LabelFrame(parent, text="Common Ports Reference", padding="10")
        common_frame.pack(fill=tk.BOTH, expand=True)
        
        # Common ports text with scrollbar and copy button
        common_header_frame = ttk.Frame(common_frame)
        common_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(common_header_frame, text="Reference:").pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = ttk.Frame(common_header_frame)
        export_frame.pack(side=tk.RIGHT)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self.export_results(self.common_results, "json", "common_ports")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export XML", 
                  command=lambda: self.export_results(self.common_results, "xml", "common_ports")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Copy Reference", 
                  command=lambda: self.copy_to_clipboard(self.common_results)).pack(side=tk.LEFT)
        
        common_text_frame = ttk.Frame(common_frame)
        common_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.common_results = tk.Text(common_text_frame, wrap=tk.WORD, 
                                     font=('Courier', 9), height=20)
        common_scrollbar = ttk.Scrollbar(common_text_frame, orient=tk.VERTICAL, 
                                        command=self.common_results.yview)
        self.common_results.configure(yscrollcommand=common_scrollbar.set)
        
        # Bind keyboard shortcuts
        self.common_results.bind('<Control-c>', lambda e: self.copy_to_clipboard(self.common_results))
        self.common_results.bind('<Control-a>', lambda e: self.select_all_text(self.common_results))
        
        self.common_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        common_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load common ports
        self.load_common_ports()

    def lookup_port(self):
        """Lookup port information"""
        port_str = self.port_input.get().strip()
        protocol = self.protocol_var.get()
        
        if not port_str:
            return
            
        try:
            port_num = int(port_str)
            if port_num < 1 or port_num > 65535:
                raise ValueError("Port must be between 1 and 65535")
                
            # Get port information
            port_info = self.get_port_info(port_num, protocol)
            
            # Display results
            self.port_results.config(state=tk.NORMAL)
            self.port_results.delete(1.0, tk.END)
            
            results = f"""Port Information
================
Port: {port_num}
Protocol: {protocol.upper()}

{port_info}
"""
            
            self.port_results.insert(tk.END, results)
            self.port_results.config(state=tk.DISABLED)
            self.port_results.see(1.0)
            
        except ValueError as e:
            self.port_results.config(state=tk.NORMAL)
            self.port_results.delete(1.0, tk.END)
            self.port_results.insert(tk.END, f"Error: {str(e)}")
            self.port_results.config(state=tk.DISABLED)

    def get_port_info(self, port, protocol):
        """Get detailed port information"""
        # Comprehensive port database
        port_db = {
            1: {"name": "tcpmux", "desc": "TCP Port Service Multiplexer", "category": "System", "notes": "Legacy service multiplexer"},
            7: {"name": "echo", "desc": "Echo Protocol", "category": "System", "notes": "Echo service for testing connectivity"},
            9: {"name": "discard", "desc": "Discard Protocol", "category": "System", "notes": "Discards all received data"},
            13: {"name": "daytime", "desc": "Daytime Protocol", "category": "System", "notes": "Returns current date and time"},
            17: {"name": "qotd", "desc": "Quote of the Day", "category": "System", "notes": "Returns a quote or message"},
            19: {"name": "chargen", "desc": "Character Generator", "category": "System", "notes": "Generates continuous character stream"},
            20: {"name": "ftp-data", "desc": "FTP Data Transfer", "category": "File Transfer", "notes": "FTP data connection"},
            21: {"name": "ftp", "desc": "File Transfer Protocol", "category": "File Transfer", "notes": "Standard FTP control connection"},
            22: {"name": "ssh", "desc": "Secure Shell", "category": "Remote Access", "notes": "Encrypted remote login and command execution"},
            23: {"name": "telnet", "desc": "Telnet", "category": "Remote Access", "notes": "Unencrypted remote login (insecure)"},
            25: {"name": "smtp", "desc": "Simple Mail Transfer Protocol", "category": "Email", "notes": "Email server communication"},
            37: {"name": "time", "desc": "Time Protocol", "category": "System", "notes": "Returns time since 1900-01-01"},
            43: {"name": "whois", "desc": "WHOIS Protocol", "category": "Network", "notes": "Domain and IP information lookup"},
            49: {"name": "tacacs", "desc": "TACACS", "category": "Authentication", "notes": "Terminal Access Controller Access Control System"},
            53: {"name": "dns", "desc": "Domain Name System", "category": "Network", "notes": "Domain name resolution"},
            67: {"name": "dhcp", "desc": "DHCP Server", "category": "Network", "notes": "Dynamic Host Configuration Protocol server"},
            68: {"name": "dhcp", "desc": "DHCP Client", "category": "Network", "notes": "Dynamic Host Configuration Protocol client"},
            69: {"name": "tftp", "desc": "Trivial File Transfer Protocol", "category": "File Transfer", "notes": "Simple file transfer protocol"},
            70: {"name": "gopher", "desc": "Gopher Protocol", "category": "Web", "notes": "Legacy information retrieval protocol"},
            79: {"name": "finger", "desc": "Finger Protocol", "category": "System", "notes": "User information lookup (security risk)"},
            80: {"name": "http", "desc": "Hypertext Transfer Protocol", "category": "Web", "notes": "Standard web server protocol"},
            88: {"name": "kerberos", "desc": "Kerberos", "category": "Authentication", "notes": "Network authentication protocol"},
            110: {"name": "pop3", "desc": "Post Office Protocol v3", "category": "Email", "notes": "Email retrieval protocol"},
            111: {"name": "rpcbind", "desc": "RPC Portmapper", "category": "System", "notes": "Remote Procedure Call port mapper"},
            113: {"name": "ident", "desc": "Identification Protocol", "category": "Authentication", "notes": "User identification service"},
            119: {"name": "nntp", "desc": "Network News Transfer Protocol", "category": "News", "notes": "News server communication"},
            123: {"name": "ntp", "desc": "Network Time Protocol", "category": "System", "notes": "Time synchronization protocol"},
            135: {"name": "msrpc", "desc": "Microsoft RPC", "category": "System", "notes": "Microsoft Remote Procedure Call"},
            137: {"name": "netbios-ns", "desc": "NetBIOS Name Service", "category": "Network", "notes": "NetBIOS name resolution"},
            138: {"name": "netbios-dgm", "desc": "NetBIOS Datagram Service", "category": "Network", "notes": "NetBIOS datagram service"},
            139: {"name": "netbios-ssn", "desc": "NetBIOS Session Service", "category": "Network", "notes": "NetBIOS session service"},
            143: {"name": "imap", "desc": "Internet Message Access Protocol", "category": "Email", "notes": "Email access and management"},
            161: {"name": "snmp", "desc": "Simple Network Management Protocol", "category": "Network", "notes": "Network device monitoring"},
            162: {"name": "snmptrap", "desc": "SNMP Trap", "category": "Network", "notes": "SNMP event notifications"},
            179: {"name": "bgp", "desc": "Border Gateway Protocol", "category": "Routing", "notes": "Internet routing protocol"},
            389: {"name": "ldap", "desc": "Lightweight Directory Access Protocol", "category": "Directory", "notes": "Directory service protocol"},
            443: {"name": "https", "desc": "HTTP Secure", "category": "Web", "notes": "Encrypted web server protocol"},
            445: {"name": "smb", "desc": "Server Message Block", "category": "File Sharing", "notes": "Windows file and printer sharing"},
            465: {"name": "smtps", "desc": "SMTP over SSL", "category": "Email", "notes": "Encrypted SMTP"},
            514: {"name": "syslog", "desc": "Syslog", "category": "Logging", "notes": "System logging protocol"},
            515: {"name": "lpd", "desc": "Line Printer Daemon", "category": "Printing", "notes": "Print service protocol"},
            587: {"name": "submission", "desc": "SMTP Submission", "category": "Email", "notes": "Email submission protocol"},
            636: {"name": "ldaps", "desc": "LDAP over SSL", "category": "Directory", "notes": "Encrypted LDAP"},
            993: {"name": "imaps", "desc": "IMAP over SSL", "category": "Email", "notes": "Encrypted IMAP"},
            995: {"name": "pop3s", "desc": "POP3 over SSL", "category": "Email", "notes": "Encrypted POP3"},
            1433: {"name": "mssql", "desc": "Microsoft SQL Server", "category": "Database", "notes": "Microsoft SQL Server database"},
            1521: {"name": "oracle", "desc": "Oracle Database", "category": "Database", "notes": "Oracle database server"},
            3306: {"name": "mysql", "desc": "MySQL Database", "category": "Database", "notes": "MySQL database server"},
            3389: {"name": "rdp", "desc": "Remote Desktop Protocol", "category": "Remote Access", "notes": "Windows remote desktop"},
            5432: {"name": "postgresql", "desc": "PostgreSQL Database", "category": "Database", "notes": "PostgreSQL database server"},
            5900: {"name": "vnc", "desc": "Virtual Network Computing", "category": "Remote Access", "notes": "Remote desktop protocol"},
            6379: {"name": "redis", "desc": "Redis Database", "category": "Database", "notes": "Redis in-memory database"},
            8080: {"name": "http-alt", "desc": "HTTP Alternative", "category": "Web", "notes": "Alternative HTTP port"},
            8443: {"name": "https-alt", "desc": "HTTPS Alternative", "category": "Web", "notes": "Alternative HTTPS port"},
            9200: {"name": "elasticsearch", "desc": "Elasticsearch", "category": "Search", "notes": "Elasticsearch search engine"},
            27017: {"name": "mongodb", "desc": "MongoDB Database", "category": "Database", "notes": "MongoDB NoSQL database"},
        }
        
        if port in port_db:
            info = port_db[port]
            result = f"""Service Name:     {info['name']}
Description:      {info['desc']}
Category:         {info['category']}
Protocol:         {protocol.upper()}
Notes:            {info['notes']}

Security Considerations:
• Ensure proper firewall rules are in place
• Use encryption when possible (SSL/TLS)
• Regularly update and patch services
• Monitor for unauthorized access attempts"""
        else:
            # Check if it's a well-known port range
            if 1 <= port <= 1023:
                result = f"""Service:          Unknown (Well-known port)
Protocol:         {protocol.upper()}
Port Range:       Well-known ports (1-1023)
Notes:            Reserved for system services
Security:         Requires root privileges to bind"""
            elif 1024 <= port <= 49151:
                result = f"""Service:          Unknown (Registered port)
Protocol:         {protocol.upper()}
Port Range:       Registered ports (1024-49151)
Notes:            Available for registration with IANA
Security:         May be used by legitimate applications"""
            else:
                result = f"""Service:          Unknown (Dynamic port)
Protocol:         {protocol.upper()}
Port Range:       Dynamic/Private ports (49152-65535)
Notes:            Available for temporary use
Security:         Commonly used for client connections"""
        
        return result

    def load_port_categories(self):
        """Load port categories information"""
        categories_text = """Port Categories Reference
===========================

WELL-KNOWN PORTS (1-1023)
-------------------------
System Services:
• 1 (tcpmux)      - TCP Port Service Multiplexer
• 7 (echo)        - Echo Protocol
• 9 (discard)     - Discard Protocol
• 13 (daytime)    - Daytime Protocol
• 19 (chargen)    - Character Generator
• 37 (time)       - Time Protocol
• 111 (rpcbind)   - RPC Portmapper
• 123 (ntp)       - Network Time Protocol

File Transfer:
• 20 (ftp-data)   - FTP Data Transfer
• 21 (ftp)        - File Transfer Protocol
• 69 (tftp)       - Trivial File Transfer Protocol

Remote Access:
• 22 (ssh)        - Secure Shell
• 23 (telnet)     - Telnet
• 3389 (rdp)      - Remote Desktop Protocol
• 5900 (vnc)      - Virtual Network Computing

Email Services:
• 25 (smtp)       - Simple Mail Transfer Protocol
• 110 (pop3)      - Post Office Protocol v3
• 143 (imap)      - Internet Message Access Protocol
• 465 (smtps)     - SMTP over SSL
• 587 (submission)- SMTP Submission
• 993 (imaps)     - IMAP over SSL
• 995 (pop3s)     - POP3 over SSL

Web Services:
• 80 (http)       - Hypertext Transfer Protocol
• 443 (https)     - HTTP Secure
• 8080 (http-alt) - HTTP Alternative
• 8443 (https-alt)- HTTPS Alternative

Network Services:
• 53 (dns)        - Domain Name System
• 67/68 (dhcp)    - Dynamic Host Configuration Protocol
• 161 (snmp)      - Simple Network Management Protocol
• 179 (bgp)       - Border Gateway Protocol

Authentication:
• 49 (tacacs)     - TACACS
• 88 (kerberos)   - Kerberos
• 113 (ident)     - Identification Protocol

Directory Services:
• 389 (ldap)      - Lightweight Directory Access Protocol
• 636 (ldaps)     - LDAP over SSL

Database Services:
• 1433 (mssql)    - Microsoft SQL Server
• 1521 (oracle)   - Oracle Database
• 3306 (mysql)    - MySQL Database
• 5432 (postgresql)- PostgreSQL Database
• 6379 (redis)    - Redis Database
• 27017 (mongodb) - MongoDB Database

File Sharing:
• 445 (smb)       - Server Message Block
• 515 (lpd)       - Line Printer Daemon

REGISTERED PORTS (1024-49151)
-----------------------------
• Available for registration with IANA
• Used by applications and services
• Examples: Custom applications, middleware

DYNAMIC PORTS (49152-65535)
---------------------------
• Available for temporary use
• Commonly used for client connections
• Ephemeral ports for outbound connections

SECURITY NOTES:
--------------
• Well-known ports (1-1023) require root privileges
• Many services have security implications
• Use encryption (SSL/TLS) when possible
• Implement proper firewall rules
• Regular security updates and monitoring
"""
        
        self.categories_results.insert(tk.END, categories_text)
        self.categories_results.config(state=tk.DISABLED)

    def load_common_ports(self):
        """Load common ports reference"""
        common_text = """Common Ports Quick Reference
============================

WEB SERVICES:
-------------
80    HTTP         - Standard web server
443   HTTPS        - Encrypted web server
8080  HTTP-ALT     - Alternative HTTP port
8443  HTTPS-ALT    - Alternative HTTPS port

EMAIL SERVICES:
---------------
25    SMTP         - Mail server (outbound)
587   SUBMISSION   - Mail submission
110   POP3         - Mail retrieval
995   POP3S        - POP3 over SSL
143   IMAP         - Mail access
993   IMAPS        - IMAP over SSL

FILE TRANSFER:
--------------
21    FTP          - File Transfer Protocol
22    SFTP         - SSH File Transfer Protocol
69    TFTP         - Trivial File Transfer Protocol

REMOTE ACCESS:
--------------
22    SSH          - Secure Shell
23    TELNET       - Telnet (insecure)
3389  RDP          - Windows Remote Desktop
5900  VNC          - Virtual Network Computing

DATABASE SERVICES:
------------------
1433  MSSQL        - Microsoft SQL Server
1521  ORACLE       - Oracle Database
3306  MYSQL        - MySQL Database
5432  POSTGRESQL   - PostgreSQL Database
6379  REDIS        - Redis Database
27017 MONGODB      - MongoDB Database

NETWORK SERVICES:
-----------------
53    DNS          - Domain Name System
67/68 DHCP         - Dynamic Host Configuration
161   SNMP         - Network Management
179   BGP          - Border Gateway Protocol
389   LDAP         - Directory Service
636   LDAPS        - LDAP over SSL

SECURITY & AUTHENTICATION:
--------------------------
49    TACACS       - Terminal Access Controller
88    KERBEROS     - Network Authentication
113   IDENT        - Identification Protocol

MICROSOFT SERVICES:
-------------------
135   MSRPC        - Microsoft RPC
137   NETBIOS-NS   - NetBIOS Name Service
138   NETBIOS-DGM  - NetBIOS Datagram
139   NETBIOS-SSN  - NetBIOS Session
445   SMB          - Server Message Block

GAMING PORTS:
-------------
27015 CS:GO        - Counter-Strike: Global Offensive
25565 MINECRAFT    - Minecraft Server
7777  ARK          - ARK: Survival Evolved
27036 STEAM        - Steam Client

MEDIA STREAMING:
---------------
1935  RTMP         - Real-Time Messaging Protocol
554   RTSP         - Real-Time Streaming Protocol
8080  HTTP-STREAM  - HTTP Streaming

DEVELOPMENT TOOLS:
------------------
3000  NODE         - Node.js Development
4200  ANGULAR      - Angular Development Server
5000  FLASK        - Flask Development Server
8000  DJANGO       - Django Development Server
9000  PHP-MY-ADMIN - phpMyAdmin

MONITORING & LOGGING:
---------------------
514   SYSLOG       - System Logging
9200  ELASTICSEARCH- Search Engine
9300  ELASTICSEARCH- Elasticsearch Cluster

SECURITY SCANNING NOTES:
------------------------
• Ports 1-1023: Well-known ports (require root)
• Ports 1024-49151: Registered ports
• Ports 49152-65535: Dynamic/Private ports
• Always scan with proper authorization
• Use encrypted protocols when possible
• Implement proper firewall rules
"""
        
        self.common_results.insert(tk.END, common_text)
        self.common_results.config(state=tk.DISABLED)

    def show_dns_lookup(self):
        """Show DNS lookup tool"""
        self.dns_lookup_dialog = tk.Toplevel(self.root)
        self.dns_lookup_dialog.title("DNS Lookup Tool")
        self.dns_lookup_dialog.geometry("600x500")
        self.dns_lookup_dialog.resizable(True, True)
        
        # Center the dialog
        self.dns_lookup_dialog.transient(self.root)
        self.dns_lookup_dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dns_lookup_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="DNS Lookup Tool", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="DNS Query", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Hostname/IP input
        ttk.Label(input_frame, text="Hostname or IP Address:").pack(anchor=tk.W)
        self.dns_input = tk.StringVar()
        dns_entry = ttk.Entry(input_frame, textvariable=self.dns_input, width=40)
        dns_entry.pack(fill=tk.X, pady=(5, 10))
        dns_entry.bind('<Return>', lambda e: self.perform_dns_lookup())
        
        # Lookup type selection
        type_frame = ttk.Frame(input_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="Lookup Type:").pack(side=tk.LEFT)
        self.dns_type = tk.StringVar(value="A")
        type_combo = ttk.Combobox(type_frame, textvariable=self.dns_type, 
                                 values=["A", "AAAA", "CNAME", "MX", "NS", "PTR", "TXT", "SOA", "All"],
                                 state="readonly", width=10)
        type_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        lookup_btn = ttk.Button(button_frame, text="Lookup", 
                               command=self.perform_dns_lookup)
        lookup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear", 
                              command=self.clear_dns_results)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        copy_btn = ttk.Button(button_frame, text="Copy Results", 
                             command=self.copy_dns_results)
        copy_btn.pack(side=tk.LEFT)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text widget with scrollbar
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.dns_results = tk.Text(results_text_frame, wrap=tk.WORD, 
                                  font=('Courier', 9), height=15)
        dns_scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, 
                                     command=self.dns_results.yview)
        self.dns_results.configure(yscrollcommand=dns_scrollbar.set)
        
        self.dns_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dns_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.dns_status = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.dns_status, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=(10, 0))
        
        # Close button
        ttk.Button(main_frame, text="Close", 
                  command=self.dns_lookup_dialog.destroy).pack(pady=(10, 0))
        
        # Focus on input field
        dns_entry.focus_set()
        
        # Add some example text
        self.dns_results.insert(tk.END, "DNS Lookup Tool\n")
        self.dns_results.insert(tk.END, "=" * 50 + "\n\n")
        self.dns_results.insert(tk.END, "Enter a hostname (e.g., google.com) or IP address (e.g., 8.8.8.8)\n")
        self.dns_results.insert(tk.END, "and select the lookup type, then click 'Lookup'.\n\n")
        self.dns_results.insert(tk.END, "Available lookup types:\n")
        self.dns_results.insert(tk.END, "• A      - IPv4 address\n")
        self.dns_results.insert(tk.END, "• AAAA   - IPv6 address\n")
        self.dns_results.insert(tk.END, "• CNAME  - Canonical name\n")
        self.dns_results.insert(tk.END, "• MX     - Mail exchange\n")
        self.dns_results.insert(tk.END, "• NS     - Name server\n")
        self.dns_results.insert(tk.END, "• PTR    - Pointer (reverse DNS)\n")
        self.dns_results.insert(tk.END, "• TXT    - Text record\n")
        self.dns_results.insert(tk.END, "• SOA    - Start of authority\n")
        self.dns_results.insert(tk.END, "• All    - All available records\n\n")
        self.dns_results.config(state=tk.DISABLED)

    def perform_dns_lookup(self):
        """Perform DNS lookup in a separate thread"""
        query = self.dns_input.get().strip()
        lookup_type = self.dns_type.get()
        
        if not query:
            self.dns_status.set("Error: Please enter a hostname or IP address")
            return
            
        self.dns_status.set("Performing DNS lookup...")
        
        # Run in separate thread to avoid blocking GUI
        def dns_worker():
            try:
                results = self.do_dns_lookup(query, lookup_type)
                
                # Update GUI in main thread
                self.dns_lookup_dialog.after(0, lambda: self.display_dns_results(query, lookup_type, results))
                
            except Exception as e:
                self.dns_lookup_dialog.after(0, lambda: self.dns_status.set(f"Error: {str(e)}"))
        
        threading.Thread(target=dns_worker, daemon=True).start()

    def do_dns_lookup(self, query, lookup_type):
        """Perform actual DNS lookup"""
        import socket
        
        # Check if dnspython is available
        try:
            import dns.resolver
            import dns.reversename
            use_dnspython = True
        except ImportError:
            use_dnspython = False
        
        results = []
        
        try:
            if lookup_type == "All":
                # Perform all lookups
                for record_type in ["A", "AAAA", "CNAME", "MX", "NS", "PTR", "TXT", "SOA"]:
                    try:
                        if use_dnspython:
                            type_results = self._lookup_record(query, record_type)
                        else:
                            type_results = self._lookup_record_fallback(query, record_type)
                        if type_results:
                            results.extend(type_results)
                    except Exception as e:
                        results.append(f"Error looking up {record_type}: {str(e)}")
            else:
                if use_dnspython:
                    results = self._lookup_record(query, lookup_type)
                else:
                    results = self._lookup_record_fallback(query, lookup_type)
                
        except Exception as e:
            results = [f"DNS lookup failed: {str(e)}"]
            
        return results

    def _lookup_record(self, query, record_type):
        """Lookup specific DNS record type"""
        import socket
        import dns.resolver
        import dns.reversename
        
        results = []
        
        try:
            if record_type == "PTR":
                # For PTR, query must be an IP address
                if not self._is_ip_address(query):
                    return [f"PTR lookup requires an IP address, got: {query}"]
                
                # Convert IP to reverse DNS format
                try:
                    reversed_dns = dns.reversename.from_address(query)
                    answers = dns.resolver.resolve(reversed_dns, "PTR")
                    for rdata in answers:
                        results.append(f"PTR: {str(rdata)}")
                except Exception as e:
                    return [f"PTR lookup failed: {str(e)}"]
            
            elif record_type == "A":
                # IPv4 lookup
                try:
                    answers = dns.resolver.resolve(query, "A")
                    for rdata in answers:
                        results.append(f"A: {str(rdata)}")
                except Exception as e:
                    # Fallback to socket.gethostbyname
                    try:
                        ip = socket.gethostbyname(query)
                        results.append(f"A: {ip}")
                    except Exception as e2:
                        return [f"A lookup failed: {str(e)}"]
            
            elif record_type == "AAAA":
                # IPv6 lookup
                try:
                    answers = dns.resolver.resolve(query, "AAAA")
                    for rdata in answers:
                        results.append(f"AAAA: {str(rdata)}")
                except Exception as e:
                    return [f"AAAA lookup failed: {str(e)}"]
            
            else:
                # Other record types
                try:
                    answers = dns.resolver.resolve(query, record_type)
                    for rdata in answers:
                        if record_type == "MX":
                            results.append(f"MX: {rdata.preference} {str(rdata.exchange)}")
                        elif record_type == "SOA":
                            results.append(f"SOA: {str(rdata.mname)} {str(rdata.rname)}")
                        else:
                            results.append(f"{record_type}: {str(rdata)}")
                except Exception as e:
                    return [f"{record_type} lookup failed: {str(e)}"]
                    
        except Exception as e:
            return [f"DNS lookup error: {str(e)}"]
            
        return results if results else [f"No {record_type} records found"]

    def _lookup_record_fallback(self, query, record_type):
        """Fallback DNS lookup using basic socket operations (when dnspython not available)"""
        import socket
        
        results = []
        
        try:
            if record_type == "A":
                # IPv4 lookup using socket
                try:
                    ip = socket.gethostbyname(query)
                    results.append(f"A: {ip}")
                except socket.gaierror as e:
                    return [f"A lookup failed: {str(e)}"]
            
            elif record_type == "AAAA":
                # IPv6 lookup (limited support without dnspython)
                try:
                    info = socket.getaddrinfo(query, None, socket.AF_INET6)
                    for item in info:
                        if item[0] == socket.AF_INET6:
                            ipv6 = item[4][0]
                            results.append(f"AAAA: {ipv6}")
                except socket.gaierror as e:
                    return [f"AAAA lookup failed: {str(e)}"]
            
            elif record_type == "PTR":
                # Reverse DNS lookup
                if not self._is_ip_address(query):
                    return [f"PTR lookup requires an IP address, got: {query}"]
                
                try:
                    hostname = socket.gethostbyaddr(query)[0]
                    results.append(f"PTR: {hostname}")
                except socket.herror as e:
                    return [f"PTR lookup failed: {str(e)}"]
            
            else:
                # For other record types, inform user that dnspython is needed
                return [f"{record_type} lookup requires dnspython library (pip install dnspython)"]
                
        except Exception as e:
            return [f"DNS lookup error: {str(e)}"]
            
        return results if results else [f"No {record_type} records found"]

    def _is_ip_address(self, text):
        """Check if text is a valid IP address"""
        import socket
        try:
            socket.inet_aton(text)  # IPv4
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, text)  # IPv6
                return True
            except socket.error:
                return False

    def display_dns_results(self, query, lookup_type, results):
        """Display DNS lookup results in the GUI"""
        self.dns_results.config(state=tk.NORMAL)
        self.dns_results.delete(1.0, tk.END)
        
        # Header
        self.dns_results.insert(tk.END, f"DNS Lookup Results\n")
        self.dns_results.insert(tk.END, "=" * 50 + "\n")
        self.dns_results.insert(tk.END, f"Query: {query}\n")
        self.dns_results.insert(tk.END, f"Type: {lookup_type}\n")
        self.dns_results.insert(tk.END, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.dns_results.insert(tk.END, "-" * 50 + "\n\n")
        
        # Results
        if results:
            for result in results:
                self.dns_results.insert(tk.END, f"{result}\n")
        else:
            self.dns_results.insert(tk.END, "No results found.\n")
        
        self.dns_results.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.dns_results.config(state=tk.DISABLED)
        
        # Scroll to top
        self.dns_results.see(1.0)
        
        # Update status
        result_count = len([r for r in results if not r.startswith("Error") and not r.startswith("No ")])
        self.dns_status.set(f"Found {result_count} record(s)")

    def clear_dns_results(self):
        """Clear DNS lookup results"""
        self.dns_results.config(state=tk.NORMAL)
        self.dns_results.delete(1.0, tk.END)
        self.dns_results.insert(tk.END, "DNS Lookup Tool\n")
        self.dns_results.insert(tk.END, "=" * 50 + "\n\n")
        self.dns_results.insert(tk.END, "Enter a hostname or IP address and select lookup type.\n")
        self.dns_results.config(state=tk.DISABLED)
        self.dns_status.set("Ready")

    def copy_dns_results(self):
        """Copy DNS results to clipboard"""
        try:
            results_text = self.dns_results.get(1.0, tk.END)
            self.dns_lookup_dialog.clipboard_clear()
            self.dns_lookup_dialog.clipboard_append(results_text)
            self.dns_status.set("Results copied to clipboard")
        except Exception as e:
            self.dns_status.set(f"Copy failed: {str(e)}")

    def show_filter_dialog(self):
        """Show advanced filter dialog"""
        messagebox.showinfo("Filter Results", "Advanced filtering will be implemented in future version")

    def toggle_stats_panel(self):
        """Toggle statistics panel visibility"""
        pass  # Already visible as tab

    def toggle_log_panel(self):
        """Toggle log panel visibility"""
        pass  # Already visible as tab

    def collapse_all(self):
        """Collapse all tree groups"""
        def collapse_recursive(item):
            self.results_tree.item(item, open=False)
            for child in self.results_tree.get_children(item):
                collapse_recursive(child)

        for item in self.results_tree.get_children():
            collapse_recursive(item)

    def expand_all(self):
        """Expand all tree groups"""
        def expand_recursive(item):
            self.results_tree.item(item, open=True)
            for child in self.results_tree.get_children(item):
                expand_recursive(child)

        for item in self.results_tree.get_children():
            expand_recursive(item)

    def show_help(self):
        """Show user guide"""
        help_text = """MaScanner Pro User Guide

Keyboard Shortcuts:
Ctrl+S - Start Scan
Ctrl+T - Stop Scan
Ctrl+E - Export Results
Ctrl+C - Clear Results
F5 - Refresh View

Target Formats:
• Single IP: 192.168.1.1
• IP Range: 192.168.1.1-254
• CIDR: 192.168.1.0/24
• Hostname: example.com
• Multiple: 192.168.1.1,192.168.1.5

Port Formats:
• Single: 80
• Range: 1-1000
• List: 22,80,443
• Mixed: 22,80-90,443

Scan Types:
• Fast - High-speed TCP connect
• SYN - Stealth SYN scan (requires admin)
• TCP - Full TCP connect
• UDP - UDP port scan
• PING - Host discovery only
"""
        self.show_text_dialog("User Guide", help_text)

    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """Keyboard Shortcuts:

Ctrl+S - Start Scan
Ctrl+T - Stop Scan
Ctrl+E - Export Results
Ctrl+L - Load Targets
Ctrl+C - Clear Results
Ctrl+F - Filter Results
F5 - Refresh View
F1 - Show Help
Escape - Stop Current Scan
"""
        self.show_text_dialog("Keyboard Shortcuts", shortcuts_text)

    def show_about(self):
        """Enhanced about dialog"""
        about_text = """MaScanner Pro v1.0
Advanced Network Port Scanner

A high-performance, feature-rich network port scanner with GUI interface,
inspired by masscan and nmap.

Key Features:
✓ Multi-threaded concurrent scanning
✓ Multiple target and port formats
✓ Real-time progress tracking
✓ Advanced filtering and grouping
✓ Export to multiple formats
✓ Comprehensive logging
✓ Ping sweep capability
✓ Service detection
✓ Cross-platform compatibility

Developed with Python, tkinter, and python-nmap.

⚠️ Use responsibly and only on networks you own or have permission to scan.
"""
        self.show_text_dialog("About MaScanner Pro", about_text)

    def load_targets(self):
        """Load targets from file"""
        self.load_targets_file()

    def save_targets(self):
        """Save current targets to file"""
        targets = self.target_entry.get().strip()
        if not targets:
            messagebox.showwarning("Warning", "No targets to save")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Targets",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                target_list = [t.strip() for t in targets.split(',')]
                with open(filename, 'w') as f:
                    for target in target_list:
                        f.write(f"{target}\n")
                self.log_message(f"Saved {len(target_list)} targets to {filename}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save targets: {str(e)}")

    def export_results(self):
        """Enhanced export with more options"""
        if not self.results_tree.get_children():
            messagebox.showwarning("Warning", "No results to export")
            return

        # Enhanced export dialog would go here
        # For now, use the basic export from main.py
        pass

    def import_results(self):
        """Import previously saved results"""
        filename = filedialog.askopenfilename(
            title="Import Results",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        data = json.load(f)
                        results = data.get('results', [])
                        for result in results:
                            self.add_enhanced_result(result)
                elif filename.endswith('.csv'):
                    with open(filename, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            result = {
                                'target': row['Target'],
                                'port': int(row['Port']),
                                'state': row['State'],
                                'service': row['Service'],
                                'protocol': row.get('Protocol', 'tcp')
                            }
                            self.add_enhanced_result(result)

                self.log_message(f"Imported results from {filename}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import results: {str(e)}")

    def on_closing(self):
        """Enhanced closing handler"""
        if self.is_scanning:
            if messagebox.askokcancel("Quit", "A scan is in progress. Do you want to quit?"):
                self.stop_scan()
                time.sleep(0.5)  # Give time for cleanup
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main entry point for advanced GUI"""
    root = tk.Tk()
    app = AdvancedMaScannerGUI(root)

    # Bind keyboard shortcuts
    root.bind('<Control-s>', lambda e: app.start_scan())
    root.bind('<Control-t>', lambda e: app.stop_scan())
    root.bind('<Control-e>', lambda e: app.export_results())
    root.bind('<Control-l>', lambda e: app.load_targets())
    root.bind('<Control-c>', lambda e: app.clear_results())
    root.bind('<F5>', lambda e: app.filter_results())
    root.bind('<F1>', lambda e: app.show_help())
    root.bind('<Escape>', lambda e: app.stop_scan())

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
