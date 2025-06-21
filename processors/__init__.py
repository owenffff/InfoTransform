"""
Processors for handling different file types
"""

from .vision import VisionProcessor
from .audio import AudioProcessor

__all__ = ['VisionProcessor', 'AudioProcessor']
