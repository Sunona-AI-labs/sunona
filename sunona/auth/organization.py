"""
Sunona Voice AI - Organization Model

Multi-tenant organization with users and teams.
"""

import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """User roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OrgStatus(str, Enum):
    """Organization status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


@dataclass
class User:
    """User within an organization."""
    user_id: str
    email: str
    name: str
    role: UserRole = UserRole.MEMBER
    
    # Auth
    auth_provider: str = "email"  # email, google, sso
    external_id: Optional[str] = None
    
    # Status
    is_active: bool = True
    email_verified: bool = False
    mfa_enabled: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "is_active": self.is_active,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Team:
    """Team within organization."""
    team_id: str
    name: str
    description: str = ""
    members: List[str] = field(default_factory=list)  # User IDs
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "member_count": len(self.members),
        }


@dataclass
class Organization:
    """
    Multi-tenant organization.
    
    Represents a company/organization with users, teams, and billing.
    """
    org_id: str
    name: str
    slug: str  # URL-friendly name
    
    # Contact
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address: Dict[str, str] = field(default_factory=dict)
    
    # Status
    status: OrgStatus = OrgStatus.TRIAL
    
    # Users and teams
    users: List[User] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # External IDs
    billing_account_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_user(
        self,
        email: str,
        name: str,
        role: UserRole = UserRole.MEMBER,
    ) -> User:
        """Add user to organization."""
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email,
            name=name,
            role=role,
        )
        self.users.append(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users:
            if user.email.lower() == email.lower():
                return user
        return None
    
    def create_team(self, name: str, description: str = "") -> Team:
        """Create a team."""
        team = Team(
            team_id=f"team_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
        )
        self.teams.append(team)
        return team
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "org_id": self.org_id,
            "name": self.name,
            "slug": self.slug,
            "email": self.email,
            "status": self.status.value,
            "user_count": len(self.users),
            "team_count": len(self.teams),
            "created_at": self.created_at.isoformat(),
        }
    
    def to_profile_dict(self) -> Dict[str, Any]:
        """Full profile for dashboard."""
        return {
            **self.to_dict(),
            "phone": self.phone,
            "website": self.website,
            "address": self.address,
            "users": [u.to_dict() for u in self.users],
            "teams": [t.to_dict() for t in self.teams],
            "settings": self.settings,
        }


class OrganizationManager:
    """
    Manage organizations and users.
    
    Example:
        ```python
        manager = OrganizationManager()
        
        # Create org
        org = manager.create_org(
            name="Acme Corp",
            email="admin@acme.com"
        )
        
        # Add user
        user = manager.add_user(
            org_id=org.org_id,
            email="john@acme.com",
            name="John Doe"
        )
        ```
    """
    
    def __init__(self):
        self._orgs: Dict[str, Organization] = {}
        logger.info("Organization manager initialized")
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug."""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug[:50]
    
    def create_org(
        self,
        name: str,
        email: str,
        owner_name: str = "Admin",
    ) -> Organization:
        """Create organization with owner."""
        org_id = f"org_{uuid.uuid4().hex[:12]}"
        slug = self._generate_slug(name)
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while any(o.slug == slug for o in self._orgs.values()):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        org = Organization(
            org_id=org_id,
            name=name,
            slug=slug,
            email=email,
        )
        
        # Add owner user
        org.add_user(email, owner_name, UserRole.OWNER)
        
        self._orgs[org_id] = org
        
        logger.info(f"Created organization: {org_id} - {name}")
        
        return org
    
    def get_org(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return self._orgs.get(org_id)
    
    def get_org_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        for org in self._orgs.values():
            if org.slug == slug:
                return org
        return None
    
    def add_user(
        self,
        org_id: str,
        email: str,
        name: str,
        role: UserRole = UserRole.MEMBER,
    ) -> Optional[User]:
        """Add user to organization."""
        org = self._orgs.get(org_id)
        if not org:
            return None
        
        # Check if user already exists
        if org.get_user_by_email(email):
            return None
        
        return org.add_user(email, name, role)
    
    def remove_user(self, org_id: str, user_id: str) -> bool:
        """Remove user from organization."""
        org = self._orgs.get(org_id)
        if not org:
            return False
        
        org.users = [u for u in org.users if u.user_id != user_id]
        return True
    
    def update_user_role(
        self,
        org_id: str,
        user_id: str,
        new_role: UserRole,
    ) -> bool:
        """Update user role."""
        org = self._orgs.get(org_id)
        if not org:
            return False
        
        user = org.get_user(user_id)
        if not user:
            return False
        
        user.role = new_role
        return True
    
    def list_orgs(self, status: Optional[OrgStatus] = None) -> List[Organization]:
        """List organizations."""
        orgs = list(self._orgs.values())
        
        if status:
            orgs = [o for o in orgs if o.status == status]
        
        return orgs
