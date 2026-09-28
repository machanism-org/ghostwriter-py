# @guidance: updated this file acording files in this folder.
__all__ = ["gw", "gdp", "adw"]


def __getattr__(name: str):
    """Resolve a public wrapper function only when it is requested."""
    if name in {"gw", "gdp", "adw"}:
        from ._ghostwriter import adw, gdp, gw

        return {"gw": gw, "gdp": gdp, "adw": adw}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
