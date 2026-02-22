from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import Base, engine, get_db
from app.models import (
    Ticket, Agent, User,
    TicketCreate, TicketUpdate, TicketResponse,
    AgentCreate, AgentResponse,
    UserRegister, UserLogin, UserResponse, TokenResponse,
)
from app.ai_router import classify_ticket
from app.embeddings import get_embedding
from app.auth import (
    hash_password, verify_password,
    create_access_token,
    get_current_user, require_admin,
)

with engine.connect() as conn:
    conn.execute(__import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ticket Routing System",
    description="AI-powered helpdesk ticket router",
    version="1.0.0",
)


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok"}


# ── Auth endpoints ─────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new user. Role defaults to agent."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT token."""
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id, "role": user.role})

    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently logged in user."""
    return current_user


# ── Agent endpoints (admin only) ───────────────────────────────────────────────

@app.post("/agents", response_model=AgentResponse, status_code=201)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),   # only admins can create agents
):
    existing = db.query(Agent).filter(Agent.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An agent with this email already exists")

    agent = Agent(name=payload.name, email=payload.email, department=payload.department)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@app.get("/agents", response_model=list[AgentResponse])
def list_agents(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),   # any logged in user can view agents
):
    return db.query(Agent).all()


@app.delete("/agents/{agent_id}", status_code=204)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()


# ── Ticket endpoints ───────────────────────────────────────────────────────────

@app.post("/tickets", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    text = f"{payload.title}. {payload.description}"
    embedding = get_embedding(text)

    similar_tickets = (
        db.query(Ticket)
        .filter(Ticket.embedding.isnot(None))
        .filter(Ticket.category.isnot(None))
        .order_by(Ticket.embedding.op("<=>")(embedding))
        .limit(3)
        .all()
    )

    ai_result = classify_ticket(payload.title, payload.description, similar_tickets)

    agent = (
        db.query(Agent)
        .filter(Agent.department == ai_result["category"])
        .outerjoin(Ticket, (Ticket.assigned_to_id == Agent.id) & (Ticket.status != "resolved"))
        .group_by(Agent.id)
        .order_by(func.count(Ticket.id).asc())
        .first()
    )

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        category=ai_result["category"],
        priority=ai_result["priority"],
        ai_summary=ai_result["ai_summary"],
        embedding=embedding,
        status="in_progress" if agent else "open",
        assigned_to_id=agent.id if agent else None,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    return query.order_by(Ticket.created_at.desc()).all()


@app.get("/tickets/search/semantic", response_model=list[TicketResponse])
def semantic_search(
    q: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query_embedding = get_embedding(q)
    results = (
        db.query(Ticket)
        .filter(Ticket.embedding.isnot(None))
        .order_by(Ticket.embedding.op("<=>")(query_embedding))
        .limit(limit)
        .all()
    )
    return results


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if payload.status is not None:
        ticket.status = payload.status
    if payload.priority is not None:
        ticket.priority = payload.priority
    if payload.category is not None:
        ticket.category = payload.category

    db.commit()
    db.refresh(ticket)
    return ticket


@app.post("/tickets/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    ticket.assigned_to_id = agent.id
    ticket.status = "in_progress"
    db.commit()
    db.refresh(ticket)
    return ticket


@app.delete("/tickets/{ticket_id}/assign", response_model=TicketResponse)
def unassign_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.assigned_to_id = None
    ticket.status = "open"
    db.commit()
    db.refresh(ticket)
    return ticket


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),   # only admins can delete
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()