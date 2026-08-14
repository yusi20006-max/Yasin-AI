"""
Ecosystem integration reference clients (Phase 4).

These modules show how external Yasin products should consume Yasin-AI
**only** through public contracts and service facades — never through
`knowledge_platform`, `developer_platform`, or provider SDKs.
"""

from yasinai.integration.agent_client import YasinAgentClient

__all__ = [
    "YasinAgentClient",
]
