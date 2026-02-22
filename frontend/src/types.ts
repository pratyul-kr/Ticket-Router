export interface Agent {
  id: number;
  name: string;
  email: string;
  department: string;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  category: string | null;
  priority: string | null;
  ai_summary: string | null;
  status: string;
  assigned_to_id: number | null;
  agent: Agent | null;
  created_at: string;
  updated_at: string | null;
}

export interface TicketCreate {
  title: string;
  description: string;
}

export interface AgentCreate {
  name: string;
  email: string;
  department: string;
}

export interface UserResponse {
  id: number;
  email: string;
  role: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}