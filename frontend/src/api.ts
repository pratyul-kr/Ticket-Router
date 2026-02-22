import axios from "axios";
import type { Ticket, TicketCreate, Agent, AgentCreate, TokenResponse } from "./types";

const api = axios.create({
  baseURL: "/api",
});

// Attach token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If token expires, redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── Auth ───────────────────────────────────────────────────────────────────────

export const registerUser = (data: { email: string; password: string }) =>
  api.post("/auth/register", data).then((r) => r.data);

export const loginUser = (data: { email: string; password: string }): Promise<TokenResponse> =>
  api.post("/auth/login", data).then((r) => r.data);

// ── Tickets ────────────────────────────────────────────────────────────────────

export const getTickets = (params?: {
  status?: string;
  priority?: string;
  category?: string;
}) => api.get<Ticket[]>("/tickets", { params }).then((r) => r.data);

export const getTicket = (id: number) =>
  api.get<Ticket>(`/tickets/${id}`).then((r) => r.data);

export const createTicket = (data: TicketCreate) =>
  api.post<Ticket>("/tickets", data).then((r) => r.data);

export const updateTicket = (id: number, data: Partial<Ticket>) =>
  api.patch<Ticket>(`/tickets/${id}`, data).then((r) => r.data);

export const deleteTicket = (id: number) =>
  api.delete(`/tickets/${id}`);

export const assignTicket = (ticketId: number, agentId: number) =>
  api.post<Ticket>(`/tickets/${ticketId}/assign?agent_id=${agentId}`).then((r) => r.data);

export const semanticSearch = (q: string, limit = 5) =>
  api.get<Ticket[]>("/tickets/search/semantic", { params: { q, limit } }).then((r) => r.data);

// ── Agents ─────────────────────────────────────────────────────────────────────

export const getAgents = () =>
  api.get<Agent[]>("/agents").then((r) => r.data);

export const createAgent = (data: AgentCreate) =>
  api.post<Agent>("/agents", data).then((r) => r.data);

export const deleteAgent = (id: number) =>
  api.delete(`/agents/${id}`);