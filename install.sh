#!/bin/bash

# MaScanner Installation Script
# Automated setup for MaScanner Network Port Scanner

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
    ███╗   ███╗ █████╗ ███████╗ ██████╗ █████╗ ███╗   ███╗███╗   ██╗███████╗██████╗
    ████╗ ████║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗ ████║████╗  ██║██╔════╝██╔══██╗
    ██╔████╔██║███████║███████╗██║     ███████║██╔████╔██║██╔██╗ ██║█████╗  ██████╔╝
    ██║╚██╔╝██║██╔══██║╚════██║██║     ██╔══██║██║╚██╔╝██║██║╚██╗██║██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║██║  ██║███████║╚██████╗██║  ██║██║ ╚═╝ ██║██║ ╚████║███████╗██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝

    MaScanner Installation Script
    High-Performance Network Port Scanner
EOF
    echo -e "${NC}"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            OS="ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            OS="centos"
        elif command -v dnf >/dev/null 2>&1; then
            OS="fedora"
        elif command -v pacman >/dev/null 2>&1; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    print_status "Checking Python installation..."

    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed!"
        return 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 6 ]; then
        print_success "Python $PYTHON_VERSION found"
        return 0
    else
        print_error "Python 3.6+ required, found $PYTHON_VERSION"
        return 1
    fi
}

# Function to install nmap
install_nmap() {
    print_status "Installing nmap..."

    case $OS in
        "ubuntu")
            sudo apt-get update
            sudo apt-get install -y nmap
            ;;
        "centos")
            sudo yum install -y nmap
            ;;
        "fedora")
            sudo dnf install -y nmap
            ;;
        "arch")
            sudo pacman -S --noconfirm nmap
            ;;
        "macos")
            if command_exists brew; then
                brew install nmap
            else
                print_error "Homebrew not found. Please install nmap manually from https://nmap.org/download.html"
                return 1
            fi
            ;;
        *)
            print_error "Unsupported OS for automatic nmap installation"
            print_status "Please install nmap manually from https://nmap.org/download.html"
            return 1
            ;;
    esac
}

# Function to check if nmap is installed
check_nmap() {
    print_status "Checking nmap installation..."

    if command_exists nmap; then
        NMAP_VERSION=$(nmap --version | head -n1 | cut -d' ' -f3)
        print_success "nmap $NMAP_VERSION found"
        return 0
    else
        print_warning "nmap not found"

        read -p "Do you want to install nmap automatically? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_nmap
            if command_exists nmap; then
                print_success "nmap installed successfully"
                return 0
            else
                print_error "nmap installation failed"
                return 1
            fi
        else
            print_error "nmap is required for MaScanner to work"
            return 1
        fi
    fi
}

# Function to install Python packages
install_python_packages() {
    print_status "Installing Python packages..."

    # Check if pip is available
    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        print_error "pip is not installed!"
        return 1
    fi

    # Upgrade pip first
    print_status "Upgrading pip..."
    $PIP_CMD install --upgrade pip

    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_status "Installing packages from requirements.txt..."
        $PIP_CMD install -r requirements.txt
    else
        print_status "Installing python-nmap manually..."
        $PIP_CMD install python-nmap==0.7.1
    fi

    print_success "Python packages installed successfully"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."

    # Check Python imports
    $PYTHON_CMD -c "
import sys
try:
    import tkinter
    print('✓ tkinter available')
except ImportError:
    print('✗ tkinter not available')
    sys.exit(1)

try:
    import nmap
    print('✓ python-nmap available')
except ImportError:
    print('✗ python-nmap not available')
    sys.exit(1)

try:
    import threading
    import socket
    import ipaddress
    import concurrent.futures
    print('✓ Standard library modules available')
except ImportError as e:
    print(f'✗ Missing standard library module: {e}')
    sys.exit(1)

print('✓ All Python dependencies verified')
"

    if [ $? -eq 0 ]; then
        print_success "Python dependencies verified"
    else
        print_error "Python dependency verification failed"
        return 1
    fi

    # Check nmap command
    if nmap --version >/dev/null 2>&1; then
        print_success "nmap command verified"
    else
        print_error "nmap command verification failed"
        return 1
    fi

    # Test basic functionality
    print_status "Testing basic functionality..."
    $PYTHON_CMD -c "
from scanner import PortScanner
scanner = PortScanner()
print('✓ Scanner module loads correctly')

# Test target validation
if scanner.validate_target('127.0.0.1'):
    print('✓ Target validation works')
else:
    print('✗ Target validation failed')

# Test port parsing
try:
    ports = scanner.parse_port_range('80,443')
    if ports:
        print('✓ Port parsing works')
    else:
        print('✗ Port parsing failed')
except Exception as e:
    print(f'✗ Port parsing error: {e}')
"

    if [ $? -eq 0 ]; then
        print_success "Basic functionality test passed"
    else
        print_error "Basic functionality test failed"
        return 1
    fi
}

# Function to create desktop shortcut (Linux)
create_desktop_shortcut() {
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "linux" ]]; then
        read -p "Create desktop shortcut? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            DESKTOP_FILE="$HOME/Desktop/MaScanner.desktop"
            CURRENT_DIR=$(pwd)

            cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MaScanner
Comment=Network Port Scanner
Exec=python3 "$CURRENT_DIR/launcher.py"
Icon=network-wired
Terminal=false
Categories=Network;Security;
EOF

            chmod +x "$DESKTOP_FILE"
            print_success "Desktop shortcut created: $DESKTOP_FILE"
        fi
    fi
}

# Function to create launch scripts
create_launch_scripts() {
    print_status "Creating launch scripts..."

    # Create basic launcher script
    cat > "run_mascanner.sh" << EOF
#!/bin/bash
# MaScanner Launcher Script

cd "\$(dirname "\$0")"

# Check if Python 3 is available
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found!"
    exit 1
fi

# Check if GUI is requested
if [ "\$1" = "gui" ] || [ "\$1" = "advanced" ]; then
    echo "Starting MaScanner GUI..."
    \$PYTHON_CMD launcher.py
elif [ "\$1" = "basic" ]; then
    echo "Starting MaScanner Basic GUI..."
    \$PYTHON_CMD main.py
elif [ "\$1" = "cli" ]; then
    shift
    echo "Starting MaScanner CLI..."
    \$PYTHON_CMD cli.py "\$@"
else
    echo "MaScanner - Network Port Scanner"
    echo ""
    echo "Usage:"
    echo "  \$0 gui        - Start GUI launcher"
    echo "  \$0 basic      - Start basic GUI"
    echo "  \$0 advanced   - Start advanced GUI"
    echo "  \$0 cli <args> - Start CLI mode"
    echo ""
    echo "Examples:"
    echo "  \$0 gui"
    echo "  \$0 cli 192.168.1.1 -p 22,80,443"
    echo "  \$0 cli --help"
    echo ""
    echo "Starting GUI launcher by default..."
    \$PYTHON_CMD launcher.py
fi
EOF

    chmod +x run_mascanner.sh
    print_success "Launch script created: run_mascanner.sh"

    # Create Windows batch file
    cat > "run_mascanner.bat" << 'EOF'
@echo off
REM MaScanner Launcher Script for Windows

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found!
    pause
    exit /b 1
)

REM Check arguments
if "%1"=="gui" goto GUI
if "%1"=="basic" goto BASIC
if "%1"=="advanced" goto ADVANCED
if "%1"=="cli" goto CLI

echo MaScanner - Network Port Scanner
echo.
echo Usage:
echo   %0 gui        - Start GUI launcher
echo   %0 basic      - Start basic GUI
echo   %0 advanced   - Start advanced GUI
echo   %0 cli ^<args^> - Start CLI mode
echo.
echo Starting GUI launcher by default...
goto GUI

:GUI
echo Starting MaScanner GUI...
python launcher.py
goto END

:BASIC
echo Starting MaScanner Basic GUI...
python main.py
goto END

:ADVANCED
echo Starting MaScanner Advanced GUI...
python gui_advanced.py
goto END

:CLI
shift
echo Starting MaScanner CLI...
python cli.py %*
goto END

:END
pause
EOF

    print_success "Windows batch file created: run_mascanner.bat"
}

# Function to set permissions
set_permissions() {
    print_status "Setting file permissions..."

    # Make Python files executable
    chmod +x *.py 2>/dev/null || true

    # Make shell scripts executable
    chmod +x *.sh 2>/dev/null || true

    print_success "File permissions set"
}

# Function to run post-installation tests
run_tests() {
    print_status "Running post-installation tests..."

    # Test basic GUI launch (just import, don't show)
    $PYTHON_CMD -c "
try:
    import main
    print('✓ Basic GUI can be imported')
except Exception as e:
    print(f'✗ Basic GUI import failed: {e}')
    exit(1)
" || return 1

    # Test advanced GUI launch (just import, don't show)
    $PYTHON_CMD -c "
try:
    import gui_advanced
    print('✓ Advanced GUI can be imported')
except Exception as e:
    print(f'✗ Advanced GUI import failed: {e}')
    exit(1)
" || return 1

    # Test CLI
    $PYTHON_CMD cli.py --help >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "CLI interface test passed"
    else
        print_warning "CLI interface test failed"
    fi

    print_success "Post-installation tests completed"
}

# Main installation function
main() {
    print_banner

    print_status "Starting MaScanner installation..."
    print_status "Detected OS: $OS"

    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -f "scanner.py" ]; then
        print_error "Installation must be run from the MaScanner directory"
        print_error "Make sure main.py and scanner.py are present"
        exit 1
    fi

    # Check Python
    if ! check_python; then
        print_error "Python check failed"
        exit 1
    fi

    # Check/install nmap
    if ! check_nmap; then
        print_error "nmap check failed"
        exit 1
    fi

    # Install Python packages
    if ! install_python_packages; then
        print_error "Python package installation failed"
        exit 1
    fi

    # Verify installation
    if ! verify_installation; then
        print_error "Installation verification failed"
        exit 1
    fi

    # Set permissions
    set_permissions

    # Create launch scripts
    create_launch_scripts

    # Create desktop shortcut
    create_desktop_shortcut

    # Run tests
    if ! run_tests; then
        print_warning "Some tests failed, but installation might still work"
    fi

    print_success "MaScanner installation completed successfully!"
    echo
    print_status "You can now run MaScanner using:"
    echo "  ./run_mascanner.sh gui      # GUI launcher"
    echo "  ./run_mascanner.sh basic    # Basic GUI"
    echo "  ./run_mascanner.sh advanced # Advanced GUI"
    echo "  ./run_mascanner.sh cli      # Command line"
    echo
    echo "Or directly:"
    echo "  $PYTHON_CMD launcher.py     # GUI launcher"
    echo "  $PYTHON_CMD main.py         # Basic GUI"
    echo "  $PYTHON_CMD gui_advanced.py # Advanced GUI"
    echo "  $PYTHON_CMD cli.py --help   # CLI help"
    echo
    print_warning "Important: Use this tool responsibly and only scan networks you own or have permission to test!"
}

# Function to show help
show_help() {
    cat << EOF
MaScanner Installation Script

Usage: $0 [OPTIONS]

OPTIONS:
    --help, -h          Show this help message
    --skip-nmap         Skip nmap installation check
    --skip-tests        Skip post-installation tests
    --quiet, -q         Quiet mode (minimal output)
    --force             Force installation even if dependencies exist

EXAMPLES:
    $0                  # Normal installation
    $0 --skip-nmap      # Install without checking nmap
    $0 --quiet          # Quiet installation

REQUIREMENTS:
    - Python 3.6 or higher
    - pip (Python package manager)
    - nmap (network scanning tool)
    - Internet connection (for package downloads)

SUPPORTED OPERATING SYSTEMS:
    - Ubuntu/Debian (apt-get)
    - CentOS/RHEL (yum)
    - Fedora (dnf)
    - Arch Linux (pacman)
    - macOS (brew)
    - Windows (manual)

For manual installation instructions, see README.md

EOF
}

# Parse command line arguments
SKIP_NMAP=false
SKIP_TESTS=false
QUIET=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --skip-nmap)
            SKIP_NMAP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Detect OS
detect_os

# Suppress output if quiet mode
if [ "$QUIET" = true ]; then
    exec >/dev/null 2>&1
fi

# Check for existing installation
if [ "$FORCE" = false ] && command_exists nmap && $PYTHON_CMD -c "import nmap" 2>/dev/null; then
    print_warning "MaScanner dependencies appear to be already installed"
    read -p "Continue with installation anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
fi

# Run main installation
main

# Exit with success
exit 0
