"""
Sunona Voice AI - Universal Knowledge Base Builder

Builds knowledge base from ANY source:
- Website URLs
- Raw text
- PDF documents
- Word documents
- Text files
- JSON/CSV data

Automatically generates an optimized AI agent based on the content.
"""

import asyncio
import logging
import re
import io
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Type of knowledge source."""
    WEBSITE = "website"
    TEXT = "text"
    PDF = "pdf"
    DOCUMENT = "document"  # Word, etc.
    JSON = "json"
    CSV = "csv"
    FILE = "file"


@dataclass
class KnowledgeChunk:
    """A chunk of knowledge with metadata."""
    content: str
    source: str
    source_type: SourceType
    title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    @property
    def word_count(self) -> int:
        return len(self.content.split())


@dataclass
class BusinessKnowledge:
    """Complete business knowledge base."""
    name: str = "My Business"
    description: str = ""
    industry: str = ""
    
    # Contact info
    email: str = ""
    phone: str = ""
    website: str = ""
    address: str = ""
    
    # Business hours
    hours: str = ""
    
    # Products/Services
    products: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    
    # Pricing
    pricing: List[Dict[str, Any]] = field(default_factory=list)
    
    # FAQ
    faq: List[Dict[str, str]] = field(default_factory=list)
    
    # Policies
    policies: Dict[str, str] = field(default_factory=dict)
    
    # Custom knowledge chunks
    chunks: List[KnowledgeChunk] = field(default_factory=list)
    
    # Full searchable content
    full_text: str = ""
    
    # Keywords
    keywords: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_chunks(self) -> int:
        return len(self.chunks)
    
    @property
    def total_words(self) -> int:
        return sum(c.word_count for c in self.chunks)


class UniversalKnowledgeBuilder:
    """
    Builds knowledge base from any source.
    
    Accepts:
    - Website URLs (auto-scrapes)
    - Raw text
    - PDF files
    - Word documents (.docx)
    - Text files (.txt)
    - JSON files
    - CSV files
    
    Example:
        ```python
        builder = UniversalKnowledgeBuilder()
        
        # Add from different sources
        await builder.add_website("https://example.com")
        builder.add_text("Our business hours are 9am-5pm...")
        await builder.add_file("business_info.pdf")
        await builder.add_file("faq.txt")
        
        # Build the knowledge base
        knowledge = builder.build()
        
        # Auto-generate AI agent
        agent = builder.generate_agent(knowledge)
        ```
    """
    
    # Chunk size for splitting large documents
    CHUNK_SIZE = 1000  # words
    CHUNK_OVERLAP = 100  # words
    
    def __init__(self, business_name: str = "My Business"):
        self.business_name = business_name
        self._chunks: List[KnowledgeChunk] = []
        self._raw_sources: List[Dict] = []
    
    # ==================== Source Adders ====================
    
    def add_text(
        self,
        text: str,
        title: str = "General Information",
        metadata: Optional[Dict] = None,
    ) -> "UniversalKnowledgeBuilder":
        """
        Add raw text to knowledge base.
        
        Args:
            text: Raw text content
            title: Optional title/category
            metadata: Optional metadata
        """
        # Split into chunks if large
        chunks = self._split_text(text)
        
        for i, chunk in enumerate(chunks):
            self._chunks.append(KnowledgeChunk(
                content=chunk,
                source="text_input",
                source_type=SourceType.TEXT,
                title=f"{title} (Part {i+1})" if len(chunks) > 1 else title,
                metadata=metadata or {},
            ))
        
        self._raw_sources.append({
            "type": "text",
            "content": text[:500],  # Preview
            "added_at": datetime.now().isoformat(),
        })
        
        logger.info(f"Added text: {len(text)} chars -> {len(chunks)} chunks")
        return self
    
    async def add_website(
        self,
        url: str,
        max_pages: int = 30,
    ) -> "UniversalKnowledgeBuilder":
        """
        Add content from a website.
        
        Args:
            url: Website URL to scrape
            max_pages: Maximum pages to scrape
        """
        try:
            from sunona.knowledge.website_builder import WebsiteKnowledgeBuilder
            
            builder = WebsiteKnowledgeBuilder()
            website_knowledge = await builder.build_from_url(url, max_pages)
            
            # Convert to chunks
            for page in website_knowledge.pages:
                self._chunks.append(KnowledgeChunk(
                    content=page.content,
                    source=page.url,
                    source_type=SourceType.WEBSITE,
                    title=page.title,
                    metadata={"headings": page.headings},
                ))
            
            # Store business info if found
            bi = website_knowledge.business_info
            if bi.name:
                self.business_name = bi.name
            
            self._raw_sources.append({
                "type": "website",
                "url": url,
                "pages": len(website_knowledge.pages),
                "added_at": datetime.now().isoformat(),
            })
            
            logger.info(f"Added website: {url} -> {len(website_knowledge.pages)} pages")
            
        except ImportError:
            logger.warning("Website builder not available")
        except Exception as e:
            logger.error(f"Failed to add website: {e}")
        
        return self
    
    async def add_file(
        self,
        file_path: Union[str, Path],
        title: Optional[str] = None,
    ) -> "UniversalKnowledgeBuilder":
        """
        Add content from a file (PDF, DOCX, TXT, JSON, CSV).
        
        Args:
            file_path: Path to file
            title: Optional title override
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return self
        
        extension = path.suffix.lower()
        file_title = title or path.stem
        
        if extension == ".pdf":
            content = await self._read_pdf(path)
        elif extension in [".docx", ".doc"]:
            content = await self._read_docx(path)
        elif extension == ".txt":
            content = path.read_text(encoding="utf-8", errors="ignore")
        elif extension == ".json":
            content = self._read_json(path)
        elif extension == ".csv":
            content = self._read_csv(path)
        else:
            # Try reading as text
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                logger.error(f"Cannot read file: {file_path}")
                return self
        
        # Add as chunks
        chunks = self._split_text(content)
        for i, chunk in enumerate(chunks):
            self._chunks.append(KnowledgeChunk(
                content=chunk,
                source=str(path),
                source_type=SourceType.FILE,
                title=f"{file_title} (Part {i+1})" if len(chunks) > 1 else file_title,
                metadata={"file_type": extension},
            ))
        
        self._raw_sources.append({
            "type": "file",
            "path": str(path),
            "extension": extension,
            "added_at": datetime.now().isoformat(),
        })
        
        logger.info(f"Added file: {path.name} -> {len(chunks)} chunks")
        return self
    
    async def add_pdf(
        self,
        pdf_content: bytes,
        title: str = "PDF Document",
    ) -> "UniversalKnowledgeBuilder":
        """
        Add PDF from bytes (for uploaded files).
        
        Args:
            pdf_content: PDF file bytes
            title: Document title
        """
        content = await self._extract_pdf_text(pdf_content)
        return self.add_text(content, title)
    
    def add_faq(
        self,
        questions_answers: List[Dict[str, str]],
    ) -> "UniversalKnowledgeBuilder":
        """
        Add FAQ items directly.
        
        Args:
            questions_answers: List of {"question": "...", "answer": "..."}
        """
        for qa in questions_answers:
            q = qa.get("question", "")
            a = qa.get("answer", "")
            
            self._chunks.append(KnowledgeChunk(
                content=f"Q: {q}\nA: {a}",
                source="faq",
                source_type=SourceType.TEXT,
                title="FAQ",
                metadata={"is_faq": True},
            ))
        
        logger.info(f"Added FAQ: {len(questions_answers)} items")
        return self
    
    def add_product_info(
        self,
        products: List[Dict[str, Any]],
    ) -> "UniversalKnowledgeBuilder":
        """
        Add product/service information.
        
        Args:
            products: List of {"name": "...", "description": "...", "price": "..."}
        """
        for product in products:
            name = product.get("name", "Product")
            desc = product.get("description", "")
            price = product.get("price", "")
            
            content = f"Product: {name}\nDescription: {desc}"
            if price:
                content += f"\nPrice: {price}"
            
            self._chunks.append(KnowledgeChunk(
                content=content,
                source="products",
                source_type=SourceType.TEXT,
                title=f"Product: {name}",
                metadata={"is_product": True, **product},
            ))
        
        logger.info(f"Added products: {len(products)} items")
        return self
    
    # ==================== File Readers ====================
    
    async def _read_pdf(self, path: Path) -> str:
        """Read PDF file and extract text."""
        try:
            import PyPDF2
            
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts)
        except ImportError:
            logger.warning("PyPDF2 not available, install with: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"PDF read error: {e}")
            return ""
    
    async def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            import PyPDF2
            
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
        except ImportError:
            logger.warning("PyPDF2 not available")
            return ""
        except Exception as e:
            logger.error(f"PDF extract error: {e}")
            return ""
    
    async def _read_docx(self, path: Path) -> str:
        """Read Word document."""
        try:
            from docx import Document
            
            doc = Document(path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except ImportError:
            logger.warning("python-docx not available, install with: pip install python-docx")
            return ""
        except Exception as e:
            logger.error(f"DOCX read error: {e}")
            return ""
    
    def _read_json(self, path: Path) -> str:
        """Read JSON file and convert to text."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return self._json_to_text(data)
        except Exception as e:
            logger.error(f"JSON read error: {e}")
            return ""
    
    def _json_to_text(self, data: Any, prefix: str = "") -> str:
        """Convert JSON to readable text."""
        lines = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._json_to_text(value, prefix + "  "))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    lines.append(f"{prefix}Item {i+1}:")
                    lines.append(self._json_to_text(item, prefix + "  "))
                else:
                    lines.append(f"{prefix}- {item}")
        else:
            lines.append(f"{prefix}{data}")
        
        return "\n".join(lines)
    
    def _read_csv(self, path: Path) -> str:
        """Read CSV file and convert to text."""
        try:
            import csv
            
            lines = []
            with open(path, encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_text = ", ".join(f"{k}: {v}" for k, v in row.items() if v)
                    lines.append(row_text)
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"CSV read error: {e}")
            return ""
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.CHUNK_SIZE - self.CHUNK_OVERLAP):
            chunk_words = words[i:i + self.CHUNK_SIZE]
            chunks.append(" ".join(chunk_words))
        
        return chunks if chunks else [text]
    
    # ==================== Build Knowledge Base ====================
    
    def build(self) -> BusinessKnowledge:
        """
        Build the complete knowledge base from all sources.
        
        Returns:
            BusinessKnowledge with all information
        """
        knowledge = BusinessKnowledge(
            name=self.business_name,
            chunks=self._chunks,
        )
        
        # Combine all content
        all_content = "\n\n".join(c.content for c in self._chunks)
        knowledge.full_text = all_content
        
        # Extract contact info
        self._extract_contact_info(knowledge, all_content)
        
        # Extract FAQ
        self._extract_faq(knowledge)
        
        # Extract products
        self._extract_products(knowledge)
        
        # Extract keywords
        knowledge.keywords = self._extract_keywords(all_content)
        
        # Generate description
        if not knowledge.description:
            knowledge.description = self._generate_description(all_content)
        
        knowledge.updated_at = datetime.now()
        
        logger.info(f"Built knowledge base: {knowledge.total_chunks} chunks, {knowledge.total_words} words")
        
        return knowledge
    
    def _extract_contact_info(self, knowledge: BusinessKnowledge, content: str):
        """Extract contact information from content."""
        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
        if email_match:
            knowledge.email = email_match.group()
        
        # Phone
        phone_match = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}', content)
        if phone_match:
            knowledge.phone = phone_match.group()
        
        # Website
        web_match = re.search(r'https?://[\w\.-]+\.\w+[/\w]*', content)
        if web_match:
            knowledge.website = web_match.group()
    
    def _extract_faq(self, knowledge: BusinessKnowledge):
        """Extract FAQ from chunks."""
        for chunk in self._chunks:
            if chunk.metadata.get("is_faq"):
                # Parse Q&A
                match = re.match(r'Q:\s*(.+?)\s*A:\s*(.+)', chunk.content, re.DOTALL)
                if match:
                    knowledge.faq.append({
                        "question": match.group(1).strip(),
                        "answer": match.group(2).strip(),
                    })
    
    def _extract_products(self, knowledge: BusinessKnowledge):
        """Extract products from chunks."""
        for chunk in self._chunks:
            if chunk.metadata.get("is_product"):
                name = chunk.metadata.get("name", "")
                if name:
                    knowledge.products.append(name)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        stopwords = {
            "that", "this", "with", "from", "have", "will", "your",
            "about", "which", "their", "would", "there", "been",
        }
        word_freq = {}
        for word in words:
            if word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:30]]
    
    def _generate_description(self, content: str) -> str:
        """Generate a short description from content."""
        # First 200 chars
        clean = re.sub(r'\s+', ' ', content).strip()
        if len(clean) > 200:
            clean = clean[:200] + "..."
        return clean
    
    # ==================== Generate Agent ====================
    
    def generate_agent(
        self,
        knowledge: BusinessKnowledge,
        agent_name: str = "Assistant",
        personality: str = "friendly and professional",
    ) -> Dict[str, Any]:
        """
        Auto-generate an AI agent configuration based on knowledge base.
        
        The agent is optimized to:
        - Answer questions accurately using the knowledge
        - Handle FAQ naturally
        - Know products/services
        - Provide contact info when needed
        - Transfer to human for unknown questions
        
        Args:
            knowledge: Built knowledge base
            agent_name: Name for the agent
            personality: Personality description
            
        Returns:
            Agent configuration dict
        """
        system_prompt = self._generate_system_prompt(knowledge, agent_name, personality)
        
        agent_config = {
            "name": agent_name,
            "description": f"AI assistant for {knowledge.name}",
            "system_prompt": system_prompt,
            "knowledge_base_id": f"kb_{hash(knowledge.name) % 100000}",
            
            # Capabilities
            "capabilities": {
                "can_answer_questions": True,
                "knows_products": len(knowledge.products) > 0,
                "knows_faq": len(knowledge.faq) > 0,
                "has_contact_info": bool(knowledge.email or knowledge.phone),
                "can_transfer_call": True,
            },
            
            # Quick responses for common questions
            "quick_responses": self._generate_quick_responses(knowledge),
            
            # Topics this agent knows about
            "known_topics": knowledge.keywords[:20],
            
            # Transfer settings
            "transfer_if_unknown": True,
            "max_unknown_before_transfer": 2,
        }
        
        logger.info(f"Generated agent: {agent_name} for {knowledge.name}")
        
        return agent_config
    
    def _generate_system_prompt(
        self,
        knowledge: BusinessKnowledge,
        agent_name: str,
        personality: str,
    ) -> str:
        """Generate optimized system prompt from knowledge."""
        
        # Build FAQ section
        faq_section = ""
        if knowledge.faq:
            faq_items = []
            for qa in knowledge.faq[:10]:  # Top 10 FAQ
                faq_items.append(f"Q: {qa['question']}\nA: {qa['answer']}")
            faq_section = "FREQUENTLY ASKED QUESTIONS:\n" + "\n\n".join(faq_items)
        
        # Build products section
        products_section = ""
        if knowledge.products or knowledge.services:
            all_items = knowledge.products + knowledge.services
            products_section = "PRODUCTS/SERVICES:\n" + "\n".join(f"- {p}" for p in all_items[:15])
        
        # Build contact section
        contact_section = ""
        contact_items = []
        if knowledge.email:
            contact_items.append(f"Email: {knowledge.email}")
        if knowledge.phone:
            contact_items.append(f"Phone: {knowledge.phone}")
        if knowledge.website:
            contact_items.append(f"Website: {knowledge.website}")
        if contact_items:
            contact_section = "CONTACT INFORMATION:\n" + "\n".join(contact_items)
        
        prompt = f"""You are {agent_name}, a {personality} AI voice assistant for {knowledge.name}.

YOUR ROLE:
- Answer customer questions accurately based on the business information below
- Be conversational and natural since this is a phone call
- Keep responses concise (1-3 sentences when possible)
- If you don't know something, honestly say so and offer to connect with a team member

ABOUT {knowledge.name.upper()}:
{knowledge.description or 'A professional business dedicated to serving our customers.'}

{contact_section}

{products_section}

{faq_section}

BUSINESS KNOWLEDGE:
{knowledge.full_text[:3000]}

IMPORTANT INSTRUCTIONS:
1. Answer questions using ONLY the information provided above
2. If a question is outside your knowledge, say "Let me connect you with someone who can help with that"
3. Be {personality} in your tone
4. For pricing questions without specific info, say "I'd be happy to get you detailed pricing - let me connect you with our team"
5. Keep responses brief and conversational for phone calls
6. If asked for an opinion, stick to facts from the knowledge base
"""
        
        return prompt.strip()
    
    def _generate_quick_responses(
        self,
        knowledge: BusinessKnowledge,
    ) -> Dict[str, str]:
        """Generate quick responses for common questions."""
        responses = {}
        
        # Hours
        if knowledge.hours:
            responses["hours"] = f"Our business hours are {knowledge.hours}."
        
        # Contact
        if knowledge.phone:
            responses["phone"] = f"You can reach us at {knowledge.phone}."
        if knowledge.email:
            responses["email"] = f"Our email is {knowledge.email}."
        
        # Location
        if knowledge.address:
            responses["address"] = f"We're located at {knowledge.address}."
        
        # Website
        if knowledge.website:
            responses["website"] = f"You can visit our website at {knowledge.website}."
        
        return responses


# ==================== API Endpoint Helper ====================

async def create_agent_from_sources(
    business_name: str,
    sources: List[Dict[str, Any]],
    agent_name: str = "Assistant",
) -> Dict[str, Any]:
    """
    Create an AI agent from multiple sources.
    
    Args:
        business_name: Name of the business
        sources: List of sources, each with:
            - type: "text", "website", "file", "faq", "products"
            - content: The content (text, URL, file path, etc.)
        agent_name: Name for the agent
        
    Returns:
        Complete agent configuration
        
    Example:
        agent = await create_agent_from_sources(
            business_name="Acme Corp",
            sources=[
                {"type": "website", "content": "https://acme.com"},
                {"type": "text", "content": "Our hours are 9-5..."},
                {"type": "file", "content": "products.pdf"},
            ]
        )
    """
    builder = UniversalKnowledgeBuilder(business_name)
    
    for source in sources:
        source_type = source.get("type", "text")
        content = source.get("content", "")
        
        if source_type == "text":
            builder.add_text(content, source.get("title", "Information"))
        elif source_type == "website":
            await builder.add_website(content)
        elif source_type == "file":
            await builder.add_file(content)
        elif source_type == "faq":
            builder.add_faq(content)
        elif source_type == "products":
            builder.add_product_info(content)
    
    knowledge = builder.build()
    agent = builder.generate_agent(knowledge, agent_name)
    
    return {
        "agent": agent,
        "knowledge": {
            "name": knowledge.name,
            "chunks": knowledge.total_chunks,
            "words": knowledge.total_words,
            "faq_count": len(knowledge.faq),
            "products_count": len(knowledge.products),
        },
    }
