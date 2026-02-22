import { useEffect, useState } from "react";
import { getTickets, semanticSearch, updateTicket, deleteTicket } from "@/api";
import type { Ticket } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Search, Trash2 } from "lucide-react";

const priorityColor: Record<string, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-green-100 text-green-700 border-green-200",
};

const statusColor: Record<string, string> = {
  open: "bg-blue-100 text-blue-700 border-blue-200",
  in_progress: "bg-purple-100 text-purple-700 border-purple-200",
  resolved: "bg-gray-100 text-gray-600 border-gray-200",
};

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

  const fetchTickets = () => {
    setLoading(true);
    getTickets({
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
      category: categoryFilter || undefined,
    }).then((data) => {
      setTickets(data);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchTickets();
  }, [statusFilter, priorityFilter, categoryFilter]);

  const handleSemanticSearch = async () => {
    if (!searchQuery.trim()) return fetchTickets();
    setLoading(true);
    const results = await semanticSearch(searchQuery);
    setTickets(results);
    setLoading(false);
  };

  const handleStatusChange = async (ticketId: number, status: string) => {
    await updateTicket(ticketId, { status });
    fetchTickets();
  };

  const handleDelete = async (ticketId: number) => {
    if (!confirm("Delete this ticket?")) return;
    await deleteTicket(ticketId);
    fetchTickets();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Tickets</h1>

      {/* Search + Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="flex gap-2 flex-1 min-w-[200px]">
          <Input
            placeholder="Semantic search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSemanticSearch()}
          />
          <Button variant="outline" onClick={handleSemanticSearch}>
            <Search className="h-4 w-4" />
          </Button>
        </div>

        <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="w-36">
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
        </Select>

        <Select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)} className="w-36">
          <option value="">All Priority</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </Select>

        <Select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="w-36">
          <option value="">All Categories</option>
          <option value="billing">Billing</option>
          <option value="technical">Technical</option>
          <option value="hr">HR</option>
          <option value="account">Account</option>
          <option value="general">General</option>
        </Select>

        {(statusFilter || priorityFilter || categoryFilter || searchQuery) && (
          <Button variant="ghost" onClick={() => {
            setStatusFilter("");
            setPriorityFilter("");
            setCategoryFilter("");
            setSearchQuery("");
            fetchTickets();
          }}>
            Clear
          </Button>
        )}
      </div>

      {/* Ticket list */}
      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : tickets.length === 0 ? (
        <p className="text-muted-foreground">No tickets found.</p>
      ) : (
        <div className="space-y-3">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="border rounded-lg p-4 space-y-2 bg-card">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <p className="font-medium">{ticket.title}</p>
                  <p className="text-sm text-muted-foreground">{ticket.ai_summary}</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(ticket.id)}
                  className="shrink-0 text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <Badge className={priorityColor[ticket.priority ?? "low"]}>
                  {ticket.priority}
                </Badge>
                <Badge className={statusColor[ticket.status]}>
                  {ticket.status.replace("_", " ")}
                </Badge>
                <Badge variant="outline" className="capitalize">
                  {ticket.category}
                </Badge>
                {ticket.agent && (
                  <span className="text-xs text-muted-foreground">
                    → {ticket.agent.name}
                  </span>
                )}
              </div>

              {/* Quick status update */}
              <div className="flex gap-2 pt-1">
                {["open", "in_progress", "resolved"].map((s) => (
                  <Button
                    key={s}
                    variant={ticket.status === s ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleStatusChange(ticket.id, s)}
                  >
                    {s.replace("_", " ")}
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}