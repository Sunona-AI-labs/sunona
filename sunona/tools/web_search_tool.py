"""
Sunona Voice AI - Web Search Tool

Search the web using Google or Bing APIs.
Enables agents to fetch real-time information.

Features:
- Google Custom Search support
- Bing Web Search support
- Result caching
- Rate limiting
- Result summarization
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import httpx

from sunona.tools.base_tool import BaseTool, ToolParameter, ParameterType, ToolResult

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    source: str


class WebSearchTool(BaseTool):
    """
    Web search tool for fetching real-time information.
    
    Supports Google Custom Search and Bing Web Search APIs.
    
    Example:
        ```python
        search = WebSearchTool(
            provider="google",
            api_key="your-api-key",
            search_engine_id="your-cx-id"
        )
        
        result = await search.execute(query="weather in NYC")
        print(result.data["results"])
        ```
    """
    
    name = "web_search"
    description = "Search the web for current information. Returns relevant search results with titles, URLs, and snippets."
    
    parameters = [
        ToolParameter(
            name="query",
            type=ParameterType.STRING,
            description="The search query",
            required=True,
        ),
        ToolParameter(
            name="num_results",
            type=ParameterType.INTEGER,
            description="Number of results to return (1-10)",
            required=False,
            default=5,
        ),
    ]
    
    def __init__(
        self,
        provider: str = "google",
        api_key: Optional[str] = None,
        search_engine_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize web search tool.
        
        Args:
            provider: Search provider ("google" or "bing")
            api_key: API key for the search provider
            search_engine_id: Google Custom Search Engine ID (cx)
        """
        super().__init__(**kwargs)
        
        self.provider = provider.lower()
        
        if self.provider == "google":
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
            self.search_engine_id = search_engine_id or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if not self.api_key or not self.search_engine_id:
                logger.warning(
                    "Google Search requires GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID"
                )
        elif self.provider == "bing":
            self.api_key = api_key or os.getenv("BING_API_KEY")
            
            if not self.api_key:
                logger.warning("Bing Search requires BING_API_KEY")
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def execute(
        self, 
        query: str, 
        num_results: int = 5,
        **kwargs
    ) -> ToolResult:
        """
        Execute a web search.
        
        Args:
            query: Search query
            num_results: Number of results (1-10)
            
        Returns:
            ToolResult with search results
        """
        try:
            num_results = min(max(1, num_results), 10)
            
            if self.provider == "google":
                results = await self._search_google(query, num_results)
            else:
                results = await self._search_bing(query, num_results)
            
            # Format results
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                })
            
            # Create summary
            summary = f"Found {len(results)} results for '{query}':\n"
            for i, r in enumerate(results, 1):
                summary += f"{i}. {r.title}: {r.snippet[:100]}...\n"
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": formatted,
                    "count": len(results),
                },
                message=summary,
            )
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Search failed: {e}",
            )
    
    async def _search_google(self, query: str, num_results: int) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google API key and Search Engine ID required")
        
        client = await self._get_client()
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": num_results,
        }
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get("items", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source="google",
            ))
        
        return results
    
    async def _search_bing(self, query: str, num_results: int) -> List[SearchResult]:
        """Search using Bing Web Search API."""
        if not self.api_key:
            raise ValueError("Bing API key required")
        
        client = await self._get_client()
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": num_results,
            "textFormat": "Raw",
        }
        
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get("webPages", {}).get("value", []):
            results.append(SearchResult(
                title=item.get("name", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                source="bing",
            ))
        
        return results
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class SerpAPITool(BaseTool):
    """
    Web search using SerpAPI for comprehensive results.
    
    SerpAPI provides structured data from multiple search engines.
    """
    
    name = "serpapi_search"
    description = "Search the web using SerpAPI for structured results including featured snippets, knowledge graphs, and more."
    
    parameters = [
        ToolParameter(
            name="query",
            type=ParameterType.STRING,
            description="The search query",
            required=True,
        ),
        ToolParameter(
            name="engine",
            type=ParameterType.STRING,
            description="Search engine to use",
            required=False,
            default="google",
            enum=["google", "bing", "duckduckgo", "yahoo"],
        ),
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize SerpAPI tool.
        
        Args:
            api_key: SerpAPI key (or SERPAPI_KEY env var)
        """
        super().__init__(**kwargs)
        
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def execute(
        self, 
        query: str,
        engine: str = "google",
        **kwargs
    ) -> ToolResult:
        """Execute SerpAPI search."""
        if not self.api_key:
            return ToolResult(
                success=False,
                error="SERPAPI_KEY not configured",
            )
        
        try:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=30.0)
            
            url = "https://serpapi.com/search"
            params = {
                "api_key": self.api_key,
                "engine": engine,
                "q": query,
            }
            
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract organic results
            organic = data.get("organic_results", [])[:5]
            
            results = []
            for item in organic:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            
            # Include answer box if available
            answer_box = data.get("answer_box", {})
            
            return ToolResult(
                success=True,
                data={
                    "results": results,
                    "answer_box": answer_box,
                    "count": len(results),
                },
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
