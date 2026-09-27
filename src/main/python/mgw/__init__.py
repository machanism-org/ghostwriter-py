# @guidance: updated this file acording files in this folder.
"""
Python interface to the Machai Ghostwriter command-line processor.

The :func:`gw`, :func:`gdp`, and :func:`adw` functions are re-exported here
so callers can use the package as the default entry points::

    from mgw import gw
    from mgw import adw, gdp

The implementation is imported lazily.  This keeps package initialization
lightweight and is important when the implementation is executed with
``python -m``: importing the submodule while initializing this package would
make ``runpy`` find it in ``sys.modules`` before it had a chance to execute it.
"""

__all__ = ["gw", "gdp", "adw"]


def __getattr__(name: str):
    """Resolve a public wrapper function only when it is requested."""
    if name in {"gw", "gdp", "adw"}:
        from .ghostwriter import adw, gdp, gw

        return {"gw": gw, "gdp": gdp, "adw": adw}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
