"""
Sunona Voice AI - Website Knowledge Base Builder

Automatically scrapes a business website and builds a knowledge base.
Users just drop their URL and the system learns about their business.
"""

import asyncio
import logging
import re
import time
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import web scraping libraries
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not available, install with: pip install httpx")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.warning("beautifulsoup4 not available, install with: pip install beautifulsoup4")


@dataclass
class WebPage:
    """Scraped web page data."""
    url: str
    title: str = ""
    content: str = ""
    headings: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    meta_description: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class BusinessInfo:
    """Extracted business information."""
    name: str = ""
    description: str = ""
    products_services: List[str] = field(default_factory=list)
    contact_email: str = ""
    contact_phone: str = ""
    address: str = ""
    faq: List[Dict[str, str]] = field(default_factory=list)
    pricing: List[str] = field(default_factory=list)
    about: str = ""
    policies: List[str] = field(default_factory=list)


@dataclass
class WebsiteKnowledge:
    """Complete knowledge base from website."""
    domain: str
    pages: List[WebPage] = field(default_factory=list)
    business_info: BusinessInfo = field(default_factory=BusinessInfo)
    full_content: str = ""
    keywords: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def page_count(self) -> int:
        return len(self.pages)


class WebsiteKnowledgeBuilder:
    """
    Scrapes a website and builds a knowledge base for voice AI.
    
    Users simply provide their website URL and the system:
    1. Crawls the website (up to 50 pages)
    2. Extracts business information
    3. Builds FAQ from content
    4. Creates searchable knowledge base
    
    Example:
        ```python
        builder = WebsiteKnowledgeBuilder()
        
        # Just provide the URL
        knowledge = await builder.build_from_url("https://www.example.com")
        
        # Now you have:
        # - Business name, description
        # - Products/services list
        # - Contact info
        # - FAQ automatically generated
        # - Full searchable content
        ```
    """
    
    # Pages to prioritize for scraping
    PRIORITY_PAGES = [
        "/", "/about", "/about-us", "/contact", "/contact-us",
        "/faq", "/help", "/support", "/pricing", "/products",
        "/services", "/terms", "/privacy", "/policy",
    ]
    
    # Maximum pages to scrape
    MAX_PAGES = 50
    
    def __init__(self):
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx required: pip install httpx")
        if not BS4_AVAILABLE:
            raise ImportError("beautifulsoup4 required: pip install beautifulsoup4")
    
    async def build_from_url(
        self,
        url: str,
        max_pages: int = 30,
        include_subpages: bool = True,
    ) -> WebsiteKnowledge:
        """
        Build knowledge base from a website URL.
        
        Args:
            url: Website URL (e.g., https://www.example.com)
            max_pages: Maximum pages to scrape
            include_subpages: Whether to follow internal links
            
        Returns:
            WebsiteKnowledge with all extracted information
        """
        # Normalize URL
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        parsed = urlparse(url)
        domain = parsed.netloc
        base_url = f"{parsed.scheme}://{domain}"
        
        logger.info(f"🌐 Starting website scan: {domain}")
        
        # Initialize knowledge
        knowledge = WebsiteKnowledge(domain=domain)
        
        # Scrape pages
        scraped_urls: Set[str] = set()
        urls_to_scrape = [base_url + p for p in self.PRIORITY_PAGES]
        urls_to_scrape.insert(0, url)  # Start with provided URL
        
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "SunonaAI/1.0 (Knowledge Builder)"},
        ) as client:
            
            while urls_to_scrape and len(scraped_urls) < min(max_pages, self.MAX_PAGES):
                current_url = urls_to_scrape.pop(0)
                
                # Skip if already scraped or external
                if current_url in scraped_urls:
                    continue
                if not current_url.startswith(base_url):
                    continue
                
                try:
                    page = await self._scrape_page(client, current_url)
                    if page:
                        knowledge.pages.append(page)
                        scraped_urls.add(current_url)
                        
                        # Add discovered links
                        if include_subpages:
                            for link in page.links:
                                full_link = urljoin(base_url, link)
                                if full_link.startswith(base_url) and full_link not in scraped_urls:
                                    urls_to_scrape.append(full_link)
                        
                        logger.info(f"✅ Scraped: {current_url} ({len(scraped_urls)}/{max_pages})")
                
                except Exception as e:
                    logger.warning(f"Failed to scrape {current_url}: {e}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
        
        # Extract business info
        knowledge.business_info = self._extract_business_info(knowledge.pages)
        
        # Build full content for RAG
        knowledge.full_content = self._build_full_content(knowledge)
        
        # Extract keywords
        knowledge.keywords = self._extract_keywords(knowledge.full_content)
        
        logger.info(f"✅ Website scan complete: {len(knowledge.pages)} pages")
        
        return knowledge
    
    async def _scrape_page(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> Optional[WebPage]:
        """Scrape a single page."""
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return None
            
            # Only process HTML
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts, styles, etc.
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Extract data
            title = soup.title.string if soup.title else ""
            
            # Get meta description
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")
            
            # Get headings
            headings = []
            for h in soup.find_all(["h1", "h2", "h3"]):
                text = h.get_text(strip=True)
                if text:
                    headings.append(text)
            
            # Get main content
            content = soup.get_text(separator=" ", strip=True)
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content)
            
            # Get internal links
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/") or urlparse(url).netloc in href:
                    links.append(href)
            
            return WebPage(
                url=url,
                title=title,
                content=content[:10000],  # Limit content length
                headings=headings,
                links=links[:50],  # Limit links
                meta_description=meta_desc,
            )
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_business_info(self, pages: List[WebPage]) -> BusinessInfo:
        """Extract business information from pages."""
        info = BusinessInfo()
        
        all_content = " ".join(p.content for p in pages)
        all_headings = []
        for p in pages:
            all_headings.extend(p.headings)
        
        # Business name (usually in title of homepage)
        if pages:
            home = pages[0]
            if home.title:
                # Remove common suffixes
                name = re.sub(r'\s*[-|–]\s*.*$', '', home.title)
                info.name = name.strip()
        
        # Description from meta or first paragraph
        for p in pages:
            if p.meta_description:
                info.description = p.meta_description
                break
        
        # Find contact info using regex
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', all_content)
        if email_match:
            info.contact_email = email_match.group()
        
        phone_match = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}', all_content)
        if phone_match:
            info.contact_phone = phone_match.group()
        
        # Extract products/services from headings
        product_keywords = ["product", "service", "solution", "offering", "feature"]
        for heading in all_headings:
            if any(kw in heading.lower() for kw in product_keywords):
                info.products_services.append(heading)
        
        # Extract FAQ
        faq_pages = [p for p in pages if "faq" in p.url.lower() or "help" in p.url.lower()]
        for page in faq_pages:
            # Simple FAQ extraction from headings
            for i, heading in enumerate(page.headings):
                if "?" in heading:
                    info.faq.append({
                        "question": heading,
                        "answer": "",  # Would need more parsing
                    })
        
        # Extract about content
        about_pages = [p for p in pages if "about" in p.url.lower()]
        if about_pages:
            info.about = about_pages[0].content[:1000]
        
        return info
    
    def _build_full_content(self, knowledge: WebsiteKnowledge) -> str:
        """Build searchable content from all pages."""
        sections = []
        
        # Add business info
        if knowledge.business_info.name:
            sections.append(f"Business Name: {knowledge.business_info.name}")
        if knowledge.business_info.description:
            sections.append(f"Description: {knowledge.business_info.description}")
        if knowledge.business_info.contact_email:
            sections.append(f"Email: {knowledge.business_info.contact_email}")
        if knowledge.business_info.contact_phone:
            sections.append(f"Phone: {knowledge.business_info.contact_phone}")
        
        # Add page content
        for page in knowledge.pages:
            section = f"\n--- {page.title} ---\n{page.content}"
            sections.append(section)
        
        return "\n\n".join(sections)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            if word not in ["that", "this", "with", "from", "have", "will", "your", "about"]:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:50]]
    
    def generate_system_prompt(self, knowledge: WebsiteKnowledge) -> str:
        """
        Generate a system prompt for the voice AI based on website knowledge.
        
        This configures the AI to answer questions about the business.
        """
        bi = knowledge.business_info
        
        prompt = f"""You are a helpful AI assistant for {bi.name or 'this business'}.

ABOUT THE BUSINESS:
{bi.description or 'A professional business serving customers.'}

CONTACT INFORMATION:
- Email: {bi.contact_email or 'Not available'}
- Phone: {bi.contact_phone or 'Not available'}

PRODUCTS/SERVICES:
{chr(10).join('- ' + p for p in bi.products_services[:10]) or '- Please ask about specific services'}

KEY INFORMATION:
{bi.about[:500] if bi.about else 'Please visit our website for more details.'}

INSTRUCTIONS:
1. Answer customer questions using the information above
2. Be helpful, friendly, and professional
3. If you don't know something, offer to transfer to a human agent
4. Keep responses concise for voice conversation
5. If the question is outside your knowledge, say "Let me connect you with a team member who can help."
"""
        return prompt


# Convenience function
async def build_knowledge_from_website(url: str) -> WebsiteKnowledge:
    """
    Build knowledge base from a website URL.
    
    Just provide the URL and get complete business knowledge!
    
    Example:
        knowledge = await build_knowledge_from_website("www.example.com")
        print(knowledge.business_info.name)
    """
    builder = WebsiteKnowledgeBuilder()
    return await builder.build_from_url(url)
