"""
Nexus RFD Protocol - Reality-First Development System

Prevents AI hallucination and ensures spec-driven development through
concrete reality checkpoints and validation.
"""

__version__ = "1.0.0"
__author__ = "RFD Protocol Team"
__email__ = "rfd@nexus.dev"

from rfd import RFD
from build import BuildEngine
from validation import ValidationEngine  
from spec import SpecEngine
from session import SessionManager

__all__ = [
    "RFD",
    "BuildEngine", 
    "ValidationEngine",
    "SpecEngine",
    "SessionManager"
]