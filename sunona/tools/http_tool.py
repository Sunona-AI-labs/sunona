"""
Sunona Voice AI - HTTP Tool

Tool for making HTTP API calls from LLM agents.
Supports GET, POST, PUT, DELETE with authentication and custom headers.

Features:
- Async HTTP requests with connection pooling
- Multiple authentication methods (Bearer, API Key, Basic)
- Request/response logging
- Timeout handling
- JSON request/response support
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None

from sunona.tools.base_tool import BaseTool, ToolResult, ToolParameter, ParameterType

logger = logging.getLogger(__name__)


class HTTPTool(BaseTool):
    """
    HTTP API calling tool for external integrations.
    
    Allows LLM agents to make HTTP requests to external APIs,
    enabling integration with any REST service.
    
    Example:
        ```python
        tool = HTTPTool(
            name="get_user_data",
            description="Fetch user data from the API",
            base_url="https://api.example.com",
            default_headers={"Authorization": "Bearer token123"}
        )
        
        result = await tool.execute(
            method="GET",
            endpoint="/users/123"
        )
        ```
    """
    
    def __init__(
        self,
        name: str = "http_request",
        description: str = "Make an HTTP request to an external API",
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        auth_type: Optional[str] = None,  # 'bearer', 'api_key', 'basic'
        auth_token: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        timeout: float = 30.0,
        **kwargs
    ):
        """
        Initialize the HTTP tool.
        
        Args:
            name: Tool name for function calling
            description: Tool description
            base_url: Base URL for all requests
            default_headers: Headers to include in all requests
            auth_type: Authentication type ('bearer', 'api_key', 'basic')
            auth_token: Authentication token/key
            api_key_header: Header name for API key auth
            timeout: Request timeout in seconds
        """
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "httpx is required for HTTPTool. "
                "Install with: pip install httpx"
            )
        
        super().__init__(**kwargs)
        
        self.name = name
        self.description = description
        self.base_url = base_url or ""
        self.default_headers = default_headers or {}
        self.auth_type = auth_type
        self.auth_token = auth_token
        self.api_key_header = api_key_header
        self.timeout = timeout
        
        # Define parameters for function calling
        self.parameters = [
            ToolParameter(
                name="method",
                type=ParameterType.STRING,
                description="HTTP method (GET, POST, PUT, DELETE, PATCH)",
                required=True,
                enum=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),
            ToolParameter(
                name="endpoint",
                type=ParameterType.STRING,
                description="API endpoint path (e.g., '/users/123')",
                required=True
            ),
            ToolParameter(
                name="body",
                type=ParameterType.OBJECT,
                description="Request body for POST/PUT/PATCH requests",
                required=False
            ),
            ToolParameter(
                name="query_params",
                type=ParameterType.OBJECT,
                description="URL query parameters",
                required=False
            ),
            ToolParameter(
                name="headers",
                type=ParameterType.OBJECT,
                description="Additional request headers",
                required=False
            ),
        ]
        
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on auth type."""
        if not self.auth_type or not self.auth_token:
            return {}
        
        if self.auth_type == "bearer":
            return {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_type == "api_key":
            return {self.api_key_header: self.auth_token}
        elif self.auth_type == "basic":
            import base64
            encoded = base64.b64encode(self.auth_token.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        
        return {}
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5)
            )
        return self._client
    
    async def execute(
        self,
        method: str,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ToolResult:
        """
        Execute an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path
            body: Request body for POST/PUT/PATCH
            query_params: URL query parameters
            headers: Additional request headers
            
        Returns:
            ToolResult with response data
        """
        try:
            client = await self._get_client()
            
            # Build URL
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if self.base_url else endpoint
            
            # Build headers
            request_headers = {
                "Content-Type": "application/json",
                **self.default_headers,
                **self._get_auth_headers(),
                **(headers or {})
            }
            
            # Make request
            method = method.upper()
            
            if method == "GET":
                response = await client.get(
                    url,
                    params=query_params,
                    headers=request_headers
                )
            elif method == "POST":
                response = await client.post(
                    url,
                    json=body,
                    params=query_params,
                    headers=request_headers
                )
            elif method == "PUT":
                response = await client.put(
                    url,
                    json=body,
                    params=query_params,
                    headers=request_headers
                )
            elif method == "DELETE":
                response = await client.delete(
                    url,
                    params=query_params,
                    headers=request_headers
                )
            elif method == "PATCH":
                response = await client.patch(
                    url,
                    json=body,
                    params=query_params,
                    headers=request_headers
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported HTTP method: {method}"
                )
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            # Check for success
            if 200 <= response.status_code < 300:
                return ToolResult(
                    success=True,
                    data=response_data,
                    metadata={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response_data}",
                    metadata={
                        "status_code": response.status_code,
                        "response": response_data,
                    }
                )
                
        except httpx.TimeoutException:
            return ToolResult(success=False, error="Request timed out")
        except httpx.ConnectError as e:
            return ToolResult(success=False, error=f"Connection error: {e}")
        except Exception as e:
            logger.error(f"HTTP request error: {e}")
            return ToolResult(success=False, error=str(e))
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class WebhookTool(HTTPTool):
    """
    Specialized HTTP tool for triggering webhooks.
    
    Simplifies webhook calls with a fixed URL and method.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        webhook_url: str,
        method: str = "POST",
        **kwargs
    ):
        """
        Initialize webhook tool.
        
        Args:
            name: Tool name
            description: Tool description
            webhook_url: Webhook URL to call
            method: HTTP method (default POST)
        """
        super().__init__(name=name, description=description, **kwargs)
        
        self.webhook_url = webhook_url
        self.webhook_method = method.upper()
        
        # Simplify parameters for webhook
        self.parameters = [
            ToolParameter(
                name="payload",
                type=ParameterType.OBJECT,
                description="Data to send to the webhook",
                required=False
            ),
        ]
    
    async def execute(self, payload: Optional[Dict[str, Any]] = None, **kwargs) -> ToolResult:
        """Execute the webhook call."""
        return await super().execute(
            method=self.webhook_method,
            endpoint=self.webhook_url,
            body=payload
        )
