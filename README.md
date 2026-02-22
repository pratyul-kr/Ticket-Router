# 🎫 Ticket Router

An AI-powered helpdesk ticket routing system built with FastAPI, React, PostgreSQL, and LLaMA 3 via Groq. Tickets are automatically classified, prioritized, and assigned to agents using a full RAG pipeline.

---

## ✨ Features

- **AI Classification** — Every ticket is automatically categorized (billing, technical, HR, account, general) and prioritized (low, medium, high) using LLaMA 3.1 via Groq
- **RAG Pipeline** — New tickets are classified using similar past tickets as context, making routing smarter over time
- **Semantic Search** — Search tickets by meaning using HuggingFace embeddings + pgvector, not just keywords
- **Auto Assignment** — Tickets are automatically assigned to the agent with the fewest active tickets in the matching department (round-robin by workload)
- **JWT Authentication** — Secure login with role-based access control (admin / agent)
- **Full CRUD** — Create, view, update, delete tickets and agents
- **React Dashboard** — Clean UI with filters, semantic search, and real-time status updates

---

## 🧠 AI Pipeline

```
User submits ticket
       ↓
HuggingFace generates embedding (384 dimensions)
       ↓
pgvector finds top 3 similar past tickets
       ↓
Groq (LLaMA 3.1) classifies using those as RAG context
       ↓
Ticket saved with category + priority + AI summary
       ↓
Auto-assigned to agent with fewest active tickets
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL + pgvector |
| AI Classification | Groq (LLaMA 3.1 8B) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Frontend | React, TypeScript, Tailwind CSS, shadcn/ui |
| Auth | JWT + bcrypt |
| Infrastructure | Docker, Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Groq API key ([console.groq.com](https://console.groq.com))
- HuggingFace API key ([huggingface.co](https://huggingface.co/settings/tokens))

### Setup

**1. Clone the repo**
```bash
git clone https://github.com/pratyul-kr/Ticket-Router.git
cd Ticket-Router
```

**2. Create your `.env` file**
```bash
cp .env.example .env
```
Fill in your API keys and generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**3. Start everything**
```bash
docker-compose up --build
```

**4. Open the app**
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

### First time setup
1. Register an account at http://localhost:5173
2. Promote yourself to admin in the database:
```bash
docker exec -it ticket_db psql -U ticketuser -d ticketdb \
  -c "UPDATE users SET role='admin' WHERE email='your@email.com';"
```
3. Sign back in and start adding agents and tickets

---

## 📁 Project Structure

```
ticket-router/
├── app/
│   ├── main.py          # API routes
│   ├── models.py        # Database models + Pydantic schemas
│   ├── database.py      # PostgreSQL connection
│   ├── auth.py          # JWT authentication
│   ├── ai_router.py     # Groq classification + RAG
│   └── embeddings.py    # HuggingFace embeddings
├── frontend/
│   └── src/
│       ├── pages/       # Dashboard, Tickets, NewTicket, Agents, Login
│       ├── components/  # shadcn/ui components
│       ├── context/     # Auth context
│       └── api.ts       # All API calls
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🔐 Role Permissions

| Action | Agent | Admin |
|---|---|---|
| View tickets | ✅ | ✅ |
| Create tickets | ✅ | ✅ |
| Update ticket status | ✅ | ✅ |
| Delete tickets | ❌ | ✅ |
| View agents | ✅ | ✅ |
| Create/delete agents | ❌ | ✅ |
| Assign tickets | ❌ | ✅ |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Public |
| POST | `/auth/login` | Login and get JWT token | Public |
| GET | `/tickets` | List tickets (filterable) | Any |
| POST | `/tickets` | Create ticket (AI classified) | Any |
| PATCH | `/tickets/{id}` | Update ticket | Any |
| DELETE | `/tickets/{id}` | Delete ticket | Admin |
| POST | `/tickets/{id}/assign` | Assign to agent | Admin |
| GET | `/tickets/search/semantic` | Semantic search | Any |
| GET | `/agents` | List agents | Any |
| POST | `/agents` | Create agent | Admin |
| DELETE | `/agents/{id}` | Delete agent | Admin |

---

## 🧪 Testing the API

The full Swagger UI is available at **http://localhost:8000/docs** when running locally.

---

## 📄 License

MIT
