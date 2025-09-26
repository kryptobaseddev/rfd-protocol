#!/usr/bin/env python3
"""
Setup configuration for RFD Protocol package
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="rfd-protocol",
    version="5.1.0",
    author="RFD Protocol Team",
    author_email="team@rfd-protocol.dev",
    description="Reality-First Development Protocol - Prevents AI hallucination and ensures spec-driven development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rfd-protocol/rfd",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "questionary>=1.10.0",
        "python-frontmatter>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "ruff",
            "mypy",
            "build",
            "twine",
        ]
    },
    entry_points={
        "console_scripts": [
            "rfd=rfd.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rfd": ["templates/*.md", "templates/*.yml"],
    },
)
