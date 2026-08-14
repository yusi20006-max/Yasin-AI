"""
Yasin-AI Service Layer

Thin facades that sit between public contracts (`yasinai.contracts`) and
internal implementation packages (`knowledge_platform`, `yasinai.providers`).

Consumers may import from here or from contracts; they must not import
internal packages directly.
"""

from yasinai.services.knowledge_service import KnowledgeService
from yasinai.services.generation_service import GenerationService

__all__ = [
    "KnowledgeService",
    "GenerationService",
]
