"""
RFD Protocol - Reality-First Development

A protocol that prevents AI hallucination in software development by enforcing
concrete reality checkpoints.
"""

__version__ = "5.5.0"
__author__ = "RFD Team"
__email__ = "team@rfd-protocol.dev"
__description__ = "Reality-First Development Protocol"

from .build import BuildEngine
from .rfd import RFD
from .session import SessionManager
from .spec import SpecEngine
from .validation import ValidationEngine

__all__ = ["RFD", "BuildEngine", "ValidationEngine", "SpecEngine", "SessionManager"]
