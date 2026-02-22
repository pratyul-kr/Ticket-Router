import { useState } from "react";
import { createTicket } from "@/api";
import type { Ticket } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Loader2 } from "lucide-react";

const priorityColor: Record<string, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-green-100 text-green-700 border-green-200",
};

export default function NewTicket() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Ticket | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!title.trim() || !description.trim()) {
      setError("Please fill in both fields.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const ticket = await createTicket({ title, description });
      setResult(ticket);
      setTitle("");
      setDescription("");
    } catch {
      setError("Failed to submit ticket. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-2xl font-semibold">New Ticket</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Submit a support ticket</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Title</label>
            <Input
              placeholder="Brief description of the issue"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Description</label>
            <textarea
              className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Describe the issue in detail..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button onClick={handleSubmit} disabled={loading} className="w-full">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                AI is classifying...
              </>
            ) : (
              "Submit Ticket"
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Show AI result after submission */}
      {result && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2 text-green-700">
              <CheckCircle2 className="h-4 w-4" />
              Ticket #{result.id} created
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm font-medium">{result.title}</p>
            <p className="text-sm text-muted-foreground">{result.ai_summary}</p>

            <div className="flex flex-wrap gap-2">
              <Badge className={priorityColor[result.priority ?? "low"]}>
                {result.priority} priority
              </Badge>
              <Badge variant="outline" className="capitalize">
                {result.category}
              </Badge>
            </div>

            {result.agent ? (
              <p className="text-sm">
                Assigned to <span className="font-medium">{result.agent.name}</span>
              </p>
            ) : (
              <p className="text-sm text-muted-foreground">
                No agent available for this category yet.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}