import { useEffect, useState } from "react";
import { getAgents, createAgent, deleteAgent } from "@/api";
import type { Agent } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trash2, UserPlus } from "lucide-react";

const DEPARTMENTS = ["billing", "technical", "hr", "account", "general"];

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("technical");
  const [error, setError] = useState("");

  const fetchAgents = () => getAgents().then(setAgents);

  useEffect(() => { fetchAgents(); }, []);

  const handleCreate = async () => {
    if (!name.trim() || !email.trim()) {
      setError("Name and email are required.");
      return;
    }
    setError("");
    try {
      await createAgent({ name, email, department });
      setName("");
      setEmail("");
      setDepartment("technical");
      fetchAgents();
    } catch {
      setError("Failed to create agent. Email may already exist.");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this agent?")) return;
    await deleteAgent(id);
    fetchAgents();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Agents</h1>

      {/* Add agent form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <UserPlus className="h-4 w-4" /> Add Agent
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-3">
            <Input
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex-1 min-w-[160px]"
            />
            <Input
              placeholder="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 min-w-[160px]"
            />
            <Select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-40"
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d} className="capitalize">{d}</option>
              ))}
            </Select>
            <Button onClick={handleCreate}>Add</Button>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      {/* Agent list */}
      {agents.length === 0 ? (
        <p className="text-muted-foreground text-sm">No agents yet.</p>
      ) : (
        <div className="space-y-3">
          {agents.map((agent) => (
            <div key={agent.id} className="border rounded-lg p-4 flex items-center justify-between bg-card">
              <div className="space-y-1">
                <p className="font-medium">{agent.name}</p>
                <p className="text-sm text-muted-foreground">{agent.email}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="capitalize">{agent.department}</Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(agent.id)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}