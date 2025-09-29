"""
Setup script for ccusage GUI
A Windows GUI application for analyzing Claude Code usage data
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = []
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove comments from individual lines
                req = line.split("#")[0].strip()
                if req:
                    requirements.append(req)
        return requirements

setup(
    name="ccusage-gui",
    version="1.0.0",
    author="Budgulick",
    author_email="",
    description="A Windows GUI application for analyzing Claude Code usage data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Budgulick/ccusage_gui",
    project_urls={
        "Bug Tracker": "https://github.com/Budgulick/ccusage_gui/issues",
        "Original CLI Tool": "https://github.com/ryoppippi/ccusage",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "gui-advanced": [
            "PyQt6>=6.5.0",
            "PyQt6-tools>=6.5.0",
        ],
        "visualization": [
            "matplotlib>=3.7.0",
            "plotly>=5.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ccusage-gui=main:main",
        ],
        "gui_scripts": [
            "ccusage-gui-windowed=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ccusage_gui": [
            "*.json",
            "*.txt",
            "assets/*",
        ],
    },
    keywords=[
        "claude",
        "claude-code",
        "usage",
        "analytics",
        "gui",
        "windows",
        "token",
        "cost",
        "monitoring",
    ],
    zip_safe=False,
)