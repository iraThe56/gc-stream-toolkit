"""
Globular Cluster Stream Toolkit

A toolkit for generating and analyzing stellar streams from globular clusters
using Gala galactic dynamics library.
"""

from .clusters import Cluster, get_cluster, list_available_clusters
from .imports import setup_imports, quick_imports, inject_imports

__version__ = "0.1.0"
__author__ = "Ira Evetts"

# Make key functions available at package level
__all__ = [
    "Cluster",
    "get_cluster",
    "list_available_clusters",
    "setup_imports",
    "quick_imports",
    "inject_imports"
]