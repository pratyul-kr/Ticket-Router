from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from pgvector.sqlalchemy import Vector

from app.database import Base


# ── Shared constants ───────────────────────────────────────────────────────────

VALID_DEPARTMENTS = {"billing", "technical", "hr", "account", "general"}
VALID_PRIORITIES  = {"low", "medium", "high"}
VALID_STATUSES    = {"open", "in_progress", "resolved"}
VALID_ROLES       = {"admin", "agent"}


# ── SQLAlchemy Models ──────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role          = Column(String(20), default="agent")  # admin or agent
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


class Agent(Base):
    __tablename__ = "agents"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    department = Column(String(100))

    tickets = relationship("Ticket", back_populates="agent")


class Ticket(Base):
    __tablename__ = "tickets"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    category    = Column(String(100))
    priority    = Column(String(20))
    ai_summary  = Column(Text)
    status      = Column(String(20), default="open")
    embedding   = Column(Vector(384), nullable=True)

    assigned_to_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    agent = relationship("Agent", back_populates="tickets")

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())


# ── Pydantic Schemas ───────────────────────────────────────────────────────────

# -- User schemas --

class UserRegister(BaseModel):
    email: str
    password: str
    role: str = "agent"

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"role must be one of: {', '.join(VALID_ROLES)}")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# -- Agent schemas --

class AgentCreate(BaseModel):
    name: str
    email: str
    department: str

    @field_validator("department")
    @classmethod
    def department_must_be_valid(cls, v):
        if v not in VALID_DEPARTMENTS:
            raise ValueError(f"department must be one of: {', '.join(sorted(VALID_DEPARTMENTS))}")
        return v

class AgentResponse(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str]

    class Config:
        from_attributes = True


# -- Ticket schemas --

class TicketCreate(BaseModel):
    title: str
    description: str

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        if v and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        return v

    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v):
        if v and v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}")
        return v

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v):
        if v and v not in VALID_DEPARTMENTS:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_DEPARTMENTS))}")
        return v

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: Optional[str]
    priority: Optional[str]
    ai_summary: Optional[str]
    status: str
    assigned_to_id: Optional[int]
    agent: Optional[AgentResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from pydantic import BaseModel, field_validator
# from typing import Optional
# from datetime import datetime
# from pgvector.sqlalchemy import Vector

# from app.database import Base


# # ── Shared constants ───────────────────────────────────────────────────────────

# VALID_DEPARTMENTS = {"billing", "technical", "hr", "account", "general"}
# VALID_PRIORITIES  = {"low", "medium", "high"}
# VALID_STATUSES    = {"open", "in_progress", "resolved"}


# # ── SQLAlchemy Models ──────────────────────────────────────────────────────────

# class Agent(Base):
#     __tablename__ = "agents"

#     id         = Column(Integer, primary_key=True, index=True)
#     name       = Column(String(100), nullable=False)
#     email      = Column(String(100), unique=True, nullable=False)
#     department = Column(String(100))

#     tickets = relationship("Ticket", back_populates="agent")


# class Ticket(Base):
#     __tablename__ = "tickets"

#     id          = Column(Integer, primary_key=True, index=True)
#     title       = Column(String(255), nullable=False)
#     description = Column(Text, nullable=False)

#     category    = Column(String(100))
#     priority    = Column(String(20))
#     ai_summary  = Column(Text)
#     status      = Column(String(20), default="open")

#     # 384 dimensions — matches all-MiniLM-L6-v2 output size
#     embedding   = Column(Vector(384), nullable=True)

#     assigned_to_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
#     agent = relationship("Agent", back_populates="tickets")

#     created_at  = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at  = Column(DateTime(timezone=True), onupdate=func.now())


# # ── Pydantic Schemas ───────────────────────────────────────────────────────────

# class AgentCreate(BaseModel):
#     name: str
#     email: str
#     department: str

#     @field_validator("department")
#     @classmethod
#     def department_must_be_valid(cls, v):
#         if v not in VALID_DEPARTMENTS:
#             raise ValueError(f"department must be one of: {', '.join(sorted(VALID_DEPARTMENTS))}")
#         return v

# class AgentResponse(BaseModel):
#     id: int
#     name: str
#     email: str
#     department: Optional[str]

#     class Config:
#         from_attributes = True


# class TicketCreate(BaseModel):
#     title: str
#     description: str

# class TicketUpdate(BaseModel):
#     status: Optional[str] = None
#     priority: Optional[str] = None
#     category: Optional[str] = None

#     @field_validator("status")
#     @classmethod
#     def status_must_be_valid(cls, v):
#         if v and v not in VALID_STATUSES:
#             raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
#         return v

#     @field_validator("priority")
#     @classmethod
#     def priority_must_be_valid(cls, v):
#         if v and v not in VALID_PRIORITIES:
#             raise ValueError(f"priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}")
#         return v

#     @field_validator("category")
#     @classmethod
#     def category_must_be_valid(cls, v):
#         if v and v not in VALID_DEPARTMENTS:
#             raise ValueError(f"category must be one of: {', '.join(sorted(VALID_DEPARTMENTS))}")
#         return v

# class TicketResponse(BaseModel):
#     id: int
#     title: str
#     description: str
#     category: Optional[str]
#     priority: Optional[str]
#     ai_summary: Optional[str]
#     status: str
#     assigned_to_id: Optional[int]
#     agent: Optional[AgentResponse]
#     created_at: datetime
#     updated_at: Optional[datetime]

#     # We don't expose the raw embedding in API responses — it's 384 numbers,
#     # not useful to the user and would clutter every response
#     class Config:
#         from_attributes = True