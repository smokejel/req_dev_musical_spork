"""
Setup configuration for Requirements Decomposition Agentic Workflow.

This setup.py file allows the project to be installed in development mode,
making the 'src' package importable from anywhere in the project.

Installation:
    pip install -e .

This enables imports like:
    from src.state import create_initial_state
    from src.agents.base_agent import BaseAgent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the requirements.txt file
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="req-dev-musical-spork",
    version="0.1.0",
    description="LangGraph-based requirements decomposition system using multi-agent workflow",
    author="Your Name",
    python_requires=">=3.11",
    packages=find_packages(include=["src", "src.*", "config", "config.*"]),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            # Future CLI entry point (Phase 4)
            # "req-decompose=main:cli",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
