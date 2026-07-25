"""
Package Builder for YasinAI Developer Platform.
Bundles modules, agents, and plugins into deployable artifacts.
"""

from yasinai.deployment.package_builder import PackageBuilder

# Thin re-export to keep backwards compatibility without redundant subclassing.
__all__ = ["PackageBuilder"]
