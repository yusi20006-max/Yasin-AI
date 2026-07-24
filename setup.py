"""Setup script for YasinAI."""

from setuptools import setup, find_packages

setup(
    name="yasinai",
    version="1.0.0",
    description="Modular AI Platform",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "yasin=yasinai.cli.main:main",
        ],
    },
)
