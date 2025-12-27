"""
SIGNAL-FLARE: Post-Exploitation Breach Confirmation
"""

__version__ = "1.1.0"
__author__ = "SIGNAL-FLARE Contributors"
__license__ = "MIT"


# Import so users can do: from signal_flare import FlareGenerator

from .generator import FlareGenerator

__all__ = ["FlareGenerator", "__version__"]
