"""
Sunona Voice AI - API Routes Package

All API route modules for the Sunona platform.
"""

# Import routers for easier access
try:
    from sunona.api.routes.billing import router as billing_router
except ImportError:
    billing_router = None

from sunona.api.routes.agents import router as agents_router
from sunona.api.routes.calls import router as calls_router

try:
    from sunona.api.routes.analytics import router as analytics_router
except ImportError:
    analytics_router = None

from sunona.api.routes.health import router as health_router

# Export for sunona/api/__init__.py to allow legacy imports if needed
# Note: sunona/api/__init__.py uses "from sunona.api.routes import agents, calls, analytics, campaigns"
# Since campaigns is missing, we'll need to fix that too.

__all__ = [
    "billing_router",
    "agents_router",
    "calls_router",
    "analytics_router",
    "health_router",
]
