"""
Ecosystem integration reference clients (Phase 4).

These modules show how external Yasin products should consume Yasin-AI
**only** through public contracts and service facades — never through
`knowledge_platform`, `developer_platform`, or provider SDKs.
"""

from yasinai.integration.agent_client import YasinAgentClient
from yasinai.integration.cli_client import YasinCLIClient
from yasinai.integration.feed_client import YasinFeedClient
from yasinai.integration.hub_client import YasinHubClient
from yasinai.integration.press_client import YasinPressClient
from yasinai.integration.relay_client import YasinRelayClient

__all__ = [
    "YasinAgentClient",
    "YasinCLIClient",
    "YasinFeedClient",
    "YasinHubClient",
    "YasinPressClient",
    "YasinRelayClient",
]
