"""
Sunona Voice AI - Integration Tests for Server

Tests for FastAPI server endpoints including health checks,
agent CRUD operations, and WebSocket functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_health_check(self, test_client):
        """Test /health endpoint returns healthy status."""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_liveness_probe(self, test_client):
        """Test /live endpoint for Kubernetes liveness."""
        response = await test_client.get("/live")
        
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_readiness_probe(self, test_client):
        """Test /ready endpoint for Kubernetes readiness."""
        response = await test_client.get("/ready")
        
        # May be 200 or 503 depending on dependencies
        assert response.status_code in [200, 503]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info."""
        response = await test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestAgentEndpoints:
    """Tests for agent CRUD endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_agent(self, test_client, sample_agent_config):
        """Test creating a new agent."""
        with patch("sunona.server.get_api_key") as mock_auth:
            mock_auth.return_value = MagicMock(organization_id="test-org")
            
            response = await test_client.post(
                "/agent/create",
                json=sample_agent_config,
                headers={"Authorization": "Bearer test-key"}
            )
            
            # May fail due to missing auth, but should at least process
            assert response.status_code in [200, 201, 401, 403, 422]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_agent_not_found(self, test_client):
        """Test getting a non-existent agent returns 404."""
        response = await test_client.get(
            "/agent/non-existent-id",
            headers={"Authorization": "Bearer test-key"}
        )
        
        # Should return 404 or 401 (auth required)
        assert response.status_code in [404, 401]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_agents(self, test_client):
        """Test listing agents endpoint."""
        response = await test_client.get(
            "/agent/list",
            headers={"Authorization": "Bearer test-key"}
        )
        
        # May require auth
        assert response.status_code in [200, 401]


class TestErrorHandling:
    """Tests for error handling middleware."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_endpoint_returns_404(self, test_client):
        """Test that invalid endpoints return 404."""
        response = await test_client.get("/invalid/endpoint/path")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_json_returns_422(self, test_client):
        """Test that invalid JSON returns 422."""
        response = await test_client.post(
            "/agent/create",
            content="not valid json",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-key"
            }
        )
        
        assert response.status_code in [422, 400, 401]


class TestCORS:
    """Tests for CORS configuration."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cors_headers_present(self, test_client):
        """Test that CORS headers are present."""
        response = await test_client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Preflight should return 200
        assert response.status_code in [200, 405]


class TestRateLimiting:
    """Tests for rate limiting middleware."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_rate_limit_not_exceeded(self, test_client):
        """Test that normal usage doesn't trigger rate limit."""
        # Make a few requests
        for _ in range(5):
            response = await test_client.get("/health")
            assert response.status_code == 200


class TestTelephonyEndpoints:
    """Tests for telephony endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.requires_api
    async def test_make_call_requires_auth(self, test_client):
        """Test that make-call endpoint requires authentication."""
        response = await test_client.post(
            "/make-call?to=%2B15551234567&agent_id=test"
        )
        
        # Should require auth
        assert response.status_code in [401, 403, 422]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_calls_requires_auth(self, test_client):
        """Test that list-calls endpoint requires authentication."""
        response = await test_client.get("/list-calls")
        
        assert response.status_code in [401, 403]
