"""YasinAI Modular AI Platform."""

from yasinai.contracts import GenerationRequest
from yasinai.services import GenerationService

__version__ = "1.1.4"

__all__ = [
    "GenerationRequest",
    "GenerationService",
    "__version__",
]
