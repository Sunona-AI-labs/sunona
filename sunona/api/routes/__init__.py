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

# New API routers
try:
    from sunona.api.routes.campaigns import router as campaigns_router
except ImportError:
    campaigns_router = None

try:
    from sunona.api.routes.phone_numbers import router as phone_numbers_router
except ImportError:
    phone_numbers_router = None

try:
    from sunona.api.routes.knowledge import router as knowledge_router
except ImportError:
    knowledge_router = None

try:
    from sunona.api.routes.dashboard import router as dashboard_router
except ImportError:
    dashboard_router = None

try:
    from sunona.api.routes.organizations import router as organizations_router
except ImportError:
    organizations_router = None

try:
    from sunona.api.routes.playground import router as playground_router
except ImportError:
    playground_router = None

__all__ = [
    "billing_router",
    "agents_router",
    "calls_router",
    "analytics_router",
    "health_router",
    "campaigns_router",
    "phone_numbers_router",
    "knowledge_router",
    "dashboard_router",
    "organizations_router",
    "playground_router",
]
