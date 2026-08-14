"""
Yasin-AI Service Layer

Thin facades that sit between public contracts (`yasinai.contracts`) and
internal implementation packages (`knowledge_platform`, etc.).

Consumers may import from here or from contracts; they must not import
internal packages directly.
"""

from yasinai.services.knowledge_service import KnowledgeService

__all__ = [
    "KnowledgeService",
]
