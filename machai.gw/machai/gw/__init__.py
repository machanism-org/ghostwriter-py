"""
Python interface to the Machai Ghostwriter command-line processor.

The :func:`gw` function is re-exported here so callers can use the package
as the default entry point::

    from machai.gw import gw

The implementation is imported lazily.  This is important when
``machai.gw.ghostwriter`` is executed with ``python -m``: importing the
submodule while initializing this package would make ``runpy`` find it in
``sys.modules`` before it had a chance to execute it.
"""

__all__ = ["gw"]


def __getattr__(name: str):
    """Resolve the public wrapper function only when it is requested."""
    if name == "gw":
        from .ghostwriter import gw

        return gw
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
