"""
Auth Service & RBAC Authorization Manager

Handles:
- User registration & password hashing
- JWT access token minting & validation
- Role-based Access Control (PUBLIC, ANALYST, OPERATOR, ADMIN)
- Session authentication dependencies
"""

from __future__ import annotations

import hmac
import hashlib
import base64
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from backend.config import settings
from backend.models import UserRole

# Secret key for JWT signing
JWT_SECRET = getattr(settings, "app_secret_key", "default-dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 24

security_bearer = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Simple, Robust Cryptographic Hashing & JWT Implementation
# ---------------------------------------------------------------------------

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """PBKDF2-HMAC-SHA256 password hashing."""
    if salt is None:
        salt = base64.b64encode(hashlib.sha256(str(time.time()).encode()).digest()[:16]).decode()
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${base64.b64encode(key).decode()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored salt$hash."""
    try:
        salt, stored_hash = hashed_password.split("$")
        computed = hash_password(plain_password, salt=salt)
        return hmac.compare_digest(computed, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: str, username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=TOKEN_EXPIRATION_HOURS))
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }

    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    signature = hmac.new(
        JWT_SECRET.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")

        header_b64, payload_b64, sig_b64 = parts
        # Verify signature
        expected_sig = hmac.new(
            JWT_SECRET.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256,
        ).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "==")

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise HTTPException(status_code=401, detail="Invalid token signature")

        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode()
        payload = json.loads(payload_json)

        # Check expiration
        if payload.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


# ---------------------------------------------------------------------------
# In-Memory Seed Users Repository (Synced with DB in Production)
# ---------------------------------------------------------------------------

class UserRecord(BaseModel):
    user_id: str
    username: str
    email: str
    hashed_password: str
    role: str
    organization: str
    is_active: bool = True


class AuthService:
    def __init__(self):
        self.users: Dict[str, UserRecord] = {}
        self._seed_default_users()

    def _seed_default_users(self):
        # Admin User
        admin_pass = hash_password("AdminSecure2024!")
        self.users["admin"] = UserRecord(
            user_id="usr-admin-01",
            username="admin",
            email="admin@usdma.uk.gov.in",
            hashed_password=admin_pass,
            role="ADMIN",
            organization="Uttarakhand State Disaster Management Authority (USDMA)",
        )

        # Operator User
        operator_pass = hash_password("Operator2024!")
        self.users["operator_chamoli"] = UserRecord(
            user_id="usr-op-02",
            username="operator_chamoli",
            email="operator.chamoli@ddma.uk.gov.in",
            hashed_password=operator_pass,
            role="OPERATOR",
            organization="DDMA Chamoli Emergency Operation Center",
        )

        # Analyst User
        analyst_pass = hash_password("Analyst2024!")
        self.users["analyst_hydrology"] = UserRecord(
            user_id="usr-an-03",
            username="analyst_hydrology",
            email="glaciology@wihg.res.in",
            hashed_password=analyst_pass,
            role="ANALYST",
            organization="Wadia Institute of Himalayan Geology (WIHG)",
        )

    def authenticate_user(self, username: str, password: str) -> Optional[UserRecord]:
        user = self.users.get(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def register_user(self, username: str, email: str, password: str, role: str = "PUBLIC", org: str = "General Public") -> UserRecord:
        if username in self.users:
            raise HTTPException(status_code=400, detail="Username already registered")
        hashed = hash_password(password)
        user = UserRecord(
            user_id=f"usr-{int(time.time())}",
            username=username,
            email=email,
            hashed_password=hashed,
            role=role,
            organization=org,
        )
        self.users[username] = user
        return user

    def get_user_by_id(self, user_id: str) -> Optional[UserRecord]:
        for u in self.users.values():
            if u.user_id == user_id:
                return u
        return None


auth_service = AuthService()


# ---------------------------------------------------------------------------
# FastAPI Dependency Injections for Protected Routes
# ---------------------------------------------------------------------------

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Optional[Dict[str, Any]]:
    """Extracts and validates user from Bearer JWT token."""
    if not credentials:
        return None
    return decode_access_token(credentials.credentials)


def require_role(allowed_roles: list[str]):
    """Enforces role-based access control on routes."""
    def role_checker(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        user_role = current_user.get("role", "PUBLIC")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access forbidden. Requires one of roles: {allowed_roles}, your role: {user_role}",
            )
        return current_user
    return role_checker
