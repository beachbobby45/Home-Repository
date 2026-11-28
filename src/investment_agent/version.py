"""Application version — single source of truth for dashboard and API."""

from __future__ import annotations

__version__ = "0.9.14"
__release_name__ = "dec paper 15k · Jan 2027 seed"
__release_tag__ = "v0.9.14-dec-15k"


def version_info() -> dict[str, str]:
    return {
        "version": __version__,
        "release": __release_name__,
        "tag": __release_tag__,
        "label": f"v{__version__} · {__release_name__}",
    }
