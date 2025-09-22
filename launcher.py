#!/usr/bin/env python3
"""
MaScanner Launcher - Choose between Basic and Advanced GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import subprocess

class MaScannerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MaScanner - Choose Interface")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # Add menu bar for window options
        self.menu_bar = tk.Menu(self.root)
        window_menu = tk.Menu(self.menu_bar, tearoff=0)
        window_menu.add_command(label="Maximize", command=self.maximize_window)
        window_menu.add_command(label="Restore Size", command=self.restore_size)
        self.menu_bar.add_cascade(label="Window", menu=window_menu)
        self.root.config(menu=self.menu_bar)

        # Store default size for restore
        self.default_geometry = "500x400"

        # Center the window
        self.center_window()

        self.setup_gui()

    def center_window(self):
        """Center the launcher window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def maximize_window(self):
        """Maximize the launcher window"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            try:
                self.root.state('zoomed')
            except:
                pass
        elif system == "Linux":
            try:
                self.root.attributes('-zoomed', True)
            except:
                # Fallback: set to screen size
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        else:  # macOS
            try:
                self.root.state('zoomed')
            except:
                pass

    def restore_size(self):
        """Restore window to default size"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            try:
                self.root.state('normal')
            except:
                pass
        elif system == "Linux":
            try:
                self.root.attributes('-zoomed', False)
            except:
                pass
        else:  # macOS
            try:
                self.root.state('normal')
            except:
                pass
                
        self.root.geometry(self.default_geometry)
        self.center_window()

    def setup_gui(self):
        """Setup launcher GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="MaScanner",
            font=('Arial', 24, 'bold')
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = ttk.Label(
            main_frame,
            text="Network Port Scanner",
            font=('Arial', 12)
        )
        subtitle_label.pack(pady=(0, 30))

        # Add maximize button
        maximize_btn = ttk.Button(main_frame, text="Maximize Window", command=self.maximize_window)
        maximize_btn.pack(pady=(0, 10))

        # Interface selection
        selection_frame = ttk.LabelFrame(main_frame, text="Choose Interface", padding="20")
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Basic GUI option
        basic_frame = ttk.Frame(selection_frame)
        basic_frame.pack(fill=tk.X, pady=(0, 15))

        basic_button = ttk.Button(
            basic_frame,
            text="🔍 Basic Interface",
            command=self.launch_basic,
            width=25
        )
        basic_button.pack(side=tk.LEFT)

        basic_desc = ttk.Label(
            basic_frame,
            text="Simple, lightweight interface for quick scans",
            font=('Arial', 9),
            foreground='gray'
        )
        basic_desc.pack(side=tk.LEFT, padx=(10, 0))

        # Advanced GUI option
        advanced_frame = ttk.Frame(selection_frame)
        advanced_frame.pack(fill=tk.X, pady=(0, 15))

        advanced_button = ttk.Button(
            advanced_frame,
            text="⚙️ Advanced Interface",
            command=self.launch_advanced,
            width=25
        )
        advanced_button.pack(side=tk.LEFT)

        advanced_desc = ttk.Label(
            advanced_frame,
            text="Feature-rich interface with tabs, statistics, and logging",
            font=('Arial', 9),
            foreground='gray'
        )
        advanced_desc.pack(side=tk.LEFT, padx=(10, 0))

        # Command line option
        cli_frame = ttk.Frame(selection_frame)
        cli_frame.pack(fill=tk.X, pady=(0, 15))

        cli_button = ttk.Button(
            cli_frame,
            text="💻 Command Line",
            command=self.show_cli_help,
            width=25
        )
        cli_button.pack(side=tk.LEFT)

        cli_desc = ttk.Label(
            cli_frame,
            text="Run from terminal for scripting and automation",
            font=('Arial', 9),
            foreground='gray'
        )
        cli_desc.pack(side=tk.LEFT, padx=(10, 0))

        # Separator
        ttk.Separator(selection_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # System requirements check
        req_frame = ttk.Frame(selection_frame)
        req_frame.pack(fill=tk.X)

        ttk.Label(req_frame, text="System Check:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        # Check Python version
        python_version = f"Python {sys.version.split()[0]}"
        python_status = "✓" if sys.version_info >= (3, 6) else "✗"
        python_color = "green" if python_status == "✓" else "red"

        python_label = ttk.Label(req_frame, text=f"{python_status} {python_version}", foreground=python_color)
        python_label.pack(anchor=tk.W, padx=(10, 0))

        # Check nmap
        nmap_status, nmap_version = self.check_nmap()
        nmap_color = "green" if nmap_status == "✓" else "red"

        nmap_label = ttk.Label(req_frame, text=f"{nmap_status} {nmap_version}", foreground=nmap_color)
        nmap_label.pack(anchor=tk.W, padx=(10, 0))

        # Check python-nmap
        try:
            import nmap as python_nmap
            pynmap_status = "✓ python-nmap installed"
            pynmap_color = "green"
        except ImportError:
            pynmap_status = "✗ python-nmap not installed"
            pynmap_color = "red"

        pynmap_label = ttk.Label(req_frame, text=pynmap_status, foreground=pynmap_color)
        pynmap_label.pack(anchor=tk.W, padx=(10, 0))

        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Install Dependencies", command=self.install_deps).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="About", command=self.show_about).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT)

    def check_nmap(self):
        """Check if nmap is installed and get version"""
        try:
            result = subprocess.run(['nmap', '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return "✓", version_line
            else:
                return "✗", "nmap not found"
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return "✗", "nmap not installed or not in PATH"

    def launch_basic(self):
        """Launch basic GUI interface"""
        try:
            self.root.withdraw()  # Hide launcher

            # Import and run basic GUI
            from main import MaScannerGUI

            gui_root = tk.Toplevel()
            gui_root.withdraw()  # Hide until setup is complete

            app = MaScannerGUI(gui_root)

            # Show the GUI window
            gui_root.deiconify()
            gui_root.focus_force()

            # Handle closing to show launcher again
            def on_gui_close():
                gui_root.destroy()
                self.root.deiconify()

            gui_root.protocol("WM_DELETE_WINDOW", on_gui_close)

        except ImportError as e:
            messagebox.showerror("Error", f"Failed to launch basic interface:\n{str(e)}")
            self.root.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch basic interface:\n{str(e)}")
            self.root.deiconify()

    def launch_advanced(self):
        """Launch advanced GUI interface"""
        try:
            self.root.withdraw()  # Hide launcher

            # Import and run advanced GUI
            from gui_advanced import AdvancedMaScannerGUI

            gui_root = tk.Toplevel()
            gui_root.withdraw()  # Hide until setup is complete

            app = AdvancedMaScannerGUI(gui_root)

            # Show the GUI window
            gui_root.deiconify()
            gui_root.focus_force()

            # Handle closing to show launcher again
            def on_gui_close():
                gui_root.destroy()
                self.root.deiconify()

            gui_root.protocol("WM_DELETE_WINDOW", on_gui_close)

        except ImportError as e:
            messagebox.showerror("Error", f"Failed to launch advanced interface:\n{str(e)}")
            self.root.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch advanced interface:\n{str(e)}")
            self.root.deiconify()

    def show_cli_help(self):
        """Show command line usage help"""
        cli_help = """Command Line Usage:

Basic Interface:
python main.py

Advanced Interface:
python gui_advanced.py

Direct Scanner (CLI):
python scanner.py <targets> <ports>

Examples:
python main.py
python gui_advanced.py

For command-line only scanning, you can also use nmap directly:
nmap -p 22,80,443 192.168.1.1-254

Note: Some scan types require administrator/root privileges.
"""

        # Create help dialog
        help_window = tk.Toplevel(self.root)
        help_window.title("Command Line Help")
        help_window.geometry("600x400")
        help_window.resizable(False, False)

        # Center the help window
        help_window.transient(self.root)
        help_window.grab_set()

        text_widget = tk.Text(help_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(1.0, cli_help)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)

    def install_deps(self):
        """Show dependency installation instructions"""
        install_text = """Installing Dependencies:

1. Install nmap:
   Ubuntu/Debian: sudo apt-get install nmap
   CentOS/RHEL:   sudo yum install nmap
   macOS:         brew install nmap
   Windows:       Download from https://nmap.org/download.html

2. Install Python dependencies:
   pip install -r requirements.txt

   Or manually:
   pip install python-nmap

3. Verify installation:
   nmap --version
   python -c "import nmap; print('python-nmap OK')"

Note: Some features require administrator/root privileges.
"""

        # Create install dialog
        install_window = tk.Toplevel(self.root)
        install_window.title("Installation Guide")
        install_window.geometry("600x400")
        install_window.resizable(False, False)

        install_window.transient(self.root)
        install_window.grab_set()

        text_widget = tk.Text(install_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(1.0, install_text)
        text_widget.config(state=tk.DISABLED)

        button_frame = ttk.Frame(install_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Install pip Dependencies",
                  command=self.auto_install_pip).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close",
                  command=install_window.destroy).pack(side=tk.LEFT, padx=5)

    def auto_install_pip(self):
        """Automatically install pip dependencies"""
        try:
            # Run pip install in a separate process
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

            if result.returncode == 0:
                messagebox.showinfo("Success", "Dependencies installed successfully!")
            else:
                messagebox.showerror("Error", f"Failed to install dependencies:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install dependencies:\n{str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """MaScanner v1.0
Network Port Scanner Suite

A comprehensive network scanning toolkit with multiple interfaces:

• Basic GUI - Simple, fast interface for quick scans
• Advanced GUI - Feature-rich interface with statistics and logging
• Command Line - For scripting and automation

Inspired by masscan and built with Python.

⚠️ Important Notice:
This tool is for authorized network testing only.
Only scan networks you own or have explicit permission to test.
Unauthorized network scanning may violate laws and policies.

The authors are not responsible for misuse of this software.

Features:
✓ High-performance concurrent scanning
✓ Multiple target formats (IP, CIDR, ranges)
✓ Various scan types (TCP, SYN, UDP)
✓ Real-time progress tracking
✓ Export capabilities
✓ Cross-platform compatibility

Requirements:
• Python 3.6+
• nmap installed
• python-nmap package

For support and updates, visit:
https://github.com/yourusername/mascanner
"""

        # Create about dialog
        about_window = tk.Toplevel(self.root)
        about_window.title("About MaScanner")
        about_window.geometry("500x600")
        about_window.resizable(False, False)

        about_window.transient(self.root)
        about_window.grab_set()

        # Add logo/icon area (placeholder)
        logo_frame = ttk.Frame(about_window)
        logo_frame.pack(pady=20)

        # Use text representation since we don't have an actual logo
        logo_text = """
    ███╗   ███╗ █████╗ ███████╗ ██████╗ █████╗ ███╗   ███╗███╗   ██╗███████╗██████╗
    ████╗ ████║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗ ████║████╗  ██║██╔════╝██╔══██╗
    ██╔████╔██║███████║███████╗██║     ███████║██╔████╔██║██╔██╗ ██║█████╗  ██████╔╝
    ██║╚██╔╝██║██╔══██║╚════██║██║     ██╔══██║██║╚██╔╝██║██║╚██╗██║██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║██║  ██║███████║╚██████╗██║  ██║██║ ╚═╝ ██║██║ ╚████║███████╗██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
        """

        logo_label = ttk.Label(logo_frame, text=logo_text, font=('Courier', 8))
        logo_label.pack()

        # About text
        text_widget = tk.Text(about_window, wrap=tk.WORD, height=20, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        text_widget.insert(1.0, about_text)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)

    def launch_basic(self):
        """Launch basic GUI interface"""
        try:
            # Close launcher and start basic GUI
            self.root.destroy()

            # Import and run basic interface
            import main
            main.main()

        except ImportError as e:
            messagebox.showerror("Error", f"Failed to launch basic interface:\n{str(e)}\n\nMake sure main.py exists in the same directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch basic interface:\n{str(e)}")

    def launch_advanced(self):
        """Launch advanced GUI interface"""
        try:
            # Close launcher and start advanced GUI
            self.root.destroy()

            # Import and run advanced interface
            import gui_advanced
            gui_advanced.main()

        except ImportError as e:
            messagebox.showerror("Error", f"Failed to launch advanced interface:\n{str(e)}\n\nMake sure gui_advanced.py exists in the same directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch advanced interface:\n{str(e)}")

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []

    # Check for required modules
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")

    try:
        import nmap
    except ImportError:
        missing_deps.append("python-nmap")

    # Check for nmap binary
    try:
        result = subprocess.run(['nmap', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            missing_deps.append("nmap (binary)")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing_deps.append("nmap (binary)")

    return missing_deps

def show_dependency_error(missing_deps):
    """Show error dialog for missing dependencies"""
    root = tk.Tk()
    root.withdraw()

    error_message = f"""Missing Dependencies:

The following required components are missing:
{chr(10).join(f"• {dep}" for dep in missing_deps)}

Installation Instructions:

1. Install nmap:
   Ubuntu/Debian: sudo apt-get install nmap
   CentOS/RHEL:   sudo yum install nmap
   macOS:         brew install nmap
   Windows:       Download from https://nmap.org/download.html

2. Install Python packages:
   pip install -r requirements.txt

Please install the missing dependencies and try again.
"""

    messagebox.showerror("Missing Dependencies", error_message)
    root.destroy()

def main():
    """Main launcher entry point"""
    # Check dependencies first
    missing_deps = check_dependencies()

    if missing_deps:
        show_dependency_error(missing_deps)
        return 1

    # Create and run launcher
    root = tk.Tk()
    app = MaScannerLauncher(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", root.quit)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user")
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
