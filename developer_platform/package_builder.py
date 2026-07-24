"""
Package Builder for YasinAI Developer Platform.
Bundles modules, agents, and plugins into deployable artifacts.
"""

from yasinai.deployment.package_builder import PackageBuilder as DeploymentPackageBuilder


class PackageBuilder(DeploymentPackageBuilder):
    """
    Manages packaging of plugins, agents, and platform integrations for distribution.
    Shared with the Deployment System.
    """
    pass
