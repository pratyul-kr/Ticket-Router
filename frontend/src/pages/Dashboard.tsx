import { useEffect, useState } from "react";
import { getTickets } from "@/api";
import type { Ticket } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TicketCheck, Clock, AlertCircle, CheckCircle2 } from "lucide-react";

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTickets().then((data) => {
      setTickets(data);
      setLoading(false);
    });
  }, []);

  const count = (status: string) => tickets.filter((t) => t.status === status).length;
  const byCategory = tickets.reduce<Record<string, number>>((acc, t) => {
    if (t.category) acc[t.category] = (acc[t.category] || 0) + 1;
    return acc;
  }, {});
  const byPriority = tickets.reduce<Record<string, number>>((acc, t) => {
    if (t.priority) acc[t.priority] = (acc[t.priority] || 0) + 1;
    return acc;
  }, {});

  if (loading) return <p className="text-muted-foreground p-8">Loading...</p>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      {/* Status cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Open</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{count("open")}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{count("in_progress")}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Resolved</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{count("resolved")}</p>
          </CardContent>
        </Card>
      </div>

      {/* Category + Priority breakdown */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">By Category</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(byCategory).length === 0 && (
              <p className="text-sm text-muted-foreground">No data yet</p>
            )}
            {Object.entries(byCategory).map(([cat, cnt]) => (
              <div key={cat} className="flex items-center justify-between">
                <span className="text-sm capitalize">{cat}</span>
                <span className="text-sm font-semibold">{cnt}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">By Priority</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(byPriority).length === 0 && (
              <p className="text-sm text-muted-foreground">No data yet</p>
            )}
            {Object.entries(byPriority).map(([pri, cnt]) => (
              <div key={pri} className="flex items-center justify-between">
                <span className="text-sm capitalize">{pri}</span>
                <span className="text-sm font-semibold">{cnt}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Recent tickets */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <TicketCheck className="h-4 w-4" /> Recent Tickets
          </CardTitle>
        </CardHeader>
        <CardContent>
          {tickets.length === 0 && (
            <p className="text-sm text-muted-foreground">No tickets yet</p>
          )}
          <div className="space-y-3">
            {tickets.slice(0, 5).map((t) => (
              <div key={t.id} className="flex items-center justify-between border-b pb-2 last:border-0">
                <div>
                  <p className="text-sm font-medium">{t.title}</p>
                  <p className="text-xs text-muted-foreground capitalize">{t.category} · {t.priority}</p>
                </div>
                <span className="text-xs capitalize text-muted-foreground">{t.status.replace("_", " ")}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}