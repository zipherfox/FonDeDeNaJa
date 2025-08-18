"""
Main entry point for FonDeDeNaJa - OMR Checker compatibility layer
"""
# Import from the actual main module
from OMRChecker_main import entry_point_for_args

# Re-export for backwards compatibility
__all__ = ['entry_point_for_args']