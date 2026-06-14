"""MISP CLI - Command-line interface for MISP."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("misp-cli")
except PackageNotFoundError:
    __version__ = "unknown"
