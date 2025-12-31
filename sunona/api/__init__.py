"""
Sunona Voice AI - Dashboard API Package

REST API endpoints for dashboard integration.

Features:
- Agent CRUD operations
- Call logs and history
- Analytics endpoints
- Campaign management
- Authentication
- Playground (no-code tools)
- WebRTC browser calling
- Multi-tenant organizations
"""

from sunona.api.routes import agents, calls
try:
    from sunona.api.routes import analytics
except ImportError:
    analytics = None
from sunona.api.auth import require_auth

# Import new routes
try:
    from sunona.api.routes import playground, webrtc_routes, organizations
except ImportError:
    playground = None
    webrtc_routes = None
    organizations = None

__all__ = [
    "agents",
    "calls",
    "analytics",
    "require_auth",
    "playground",
    "webrtc_routes",
    "organizations",
]

