"""
Ecosystem integration reference clients.

Policy (decided Phase 4, documented Phase 5): these classes are public,
tested, supported **reference/convenience wrappers** around
`yasinai.contracts` / `yasinai.services` — they are NOT the mandatory or
exclusive consumer integration path. Consuming `yasinai.contracts` and
`yasinai.services` directly is equally supported and is, in practice, the
path every current real integration (YasinRelay, YasinFeed, YasinPress)
uses. Use whichever fits your consumer's existing patterns.

What both paths share, and must continue to share: external Yasin
products consume Yasin-AI **only** through public contracts and service
facades — never through `knowledge_platform`, `developer_platform`, or
provider SDKs directly.
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
