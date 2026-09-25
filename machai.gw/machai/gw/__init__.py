"""
Python interface to the Machai Ghostwriter command-line processor.

The :func:`gw` function is re-exported here so callers can use the package
as the default entry point::

    from machai.gw import gw
"""

from .ghostwriter import gw

__all__ = ["gw"]
