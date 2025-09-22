#!/usr/bin/env python3
"""
Setup script for MaScanner - Network Port Scanner GUI
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Filter out built-in modules
                if line not in ['tkinter', 'threading', 'socket', 'ipaddress', 'concurrent.futures']:
                    requirements.append(line)
    return requirements

setup(
    name="mascanner",
    version="1.0.0",
    author="Assistant",
    author_email="assistant@example.com",
    description="A high-performance network port scanner with GUI interface, inspired by masscan",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mascanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "mascanner=main:main",
        ],
        "gui_scripts": [
            "mascanner-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mascanner": [
            "*.ico",
            "*.png",
        ],
    },
    keywords="port scanner, network security, masscan, nmap, gui, tkinter",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mascanner/issues",
        "Source": "https://github.com/yourusername/mascanner",
        "Documentation": "https://github.com/yourusername/mascanner/wiki",
    },
    zip_safe=False,
)
