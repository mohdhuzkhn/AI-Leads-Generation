"use client";
import { useEffect, useState, useCallback } from "react";
import {
  Search, Users, BarChart2, Send,
  CheckCircle2, Circle, Loader2, XCircle
} from "lucide-react";
import clsx from "clsx";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface NodeProgress {
  node: number;
  name: string;
  status: "pending" | "active" | "done" | "error";
  message: string;
}

interface AgentProgressProps {
  jobId: string;
  onComplete?: () => void;
}

const NODE_ICONS = [Search, Users, BarChart2, Send];
const NODE_COLORS = {
  pending: "text-gray-600",
  active:  "text-indigo-400",
  done:    "text-emerald-400",
  error:   "text-red-400",
};

export default function AgentProgress({ jobId, onComplete }: AgentProgressProps) {
  const [nodes, setNodes] = useState<NodeProgress[]>([]);
  const [jobStatus, setJobStatus] = useState<string>("queued");
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    const es = new EventSource(`${API_BASE}/api/status/${jobId}`);

    es.addEventListener("progress", (e) => {
      try {
        const data = JSON.parse(e.data);
        setNodes(data.nodes ?? []);
        setJobStatus(data.status);
        if (data.error) setError(data.error);
      } catch {}
    });

    es.addEventListener("done", (e) => {
      try {
        const data = JSON.parse(e.data);
        setJobStatus(data.status);
        es.close();
        if (data.status === "completed" && onComplete) {
          setTimeout(onComplete, 800);
        }
      } catch {}
    });

    es.addEventListener("error", () => {
      es.close();
      setJobStatus("failed");
    });

    return es;
  }, [jobId, onComplete]);

  useEffect(() => {
    const es = connect();
    return () => es.close();
  }, [connect]);

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Status header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-xl font-bold text-white">Agent Running</h2>
          <p className="text-sm text-gray-400 mt-0.5">
            {jobStatus === "completed"
              ? "All nodes completed successfully"
              : jobStatus === "failed"
              ? "Pipeline encountered an error"
              : "Processing your lead generation request..."}
          </p>
        </div>
        <div className={clsx(
          "px-3 py-1.5 rounded-full text-xs font-semibold border",
          jobStatus === "completed" && "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
          jobStatus === "running"   && "bg-indigo-500/10  text-indigo-400  border-indigo-500/20",
          jobStatus === "failed"    && "bg-red-500/10     text-red-400     border-red-500/20",
          jobStatus === "queued"    && "bg-gray-500/10    text-gray-400    border-gray-500/20",
        )}>
          {jobStatus.toUpperCase()}
        </div>
      </div>

      {/* Node steps */}
      <div className="space-y-3">
        {(nodes.length ? nodes : Array(4).fill(null)).map((node, i) => {
          const Icon = NODE_ICONS[i];
          const status = node?.status ?? "pending";
          const name   = node?.name    ?? ["Company Discovery","Contact Enrichment","Lead Scoring","Output & Outreach"][i];
          const msg    = node?.message ?? "Waiting...";

          return (
            <div
              key={i}
              className={clsx(
                "flex items-start gap-4 p-4 rounded-xl border transition-all duration-500",
                status === "active"  && "glass border-indigo-500/30 glow-indigo",
                status === "done"    && "glass border-emerald-500/10 bg-emerald-500/5",
                status === "error"   && "glass border-red-500/30",
                status === "pending" && "border-white/5 bg-white/[0.01]",
              )}
            >
              {/* Icon */}
              <div className={clsx(
                "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5",
                status === "active"  && "bg-indigo-500/20",
                status === "done"    && "bg-emerald-500/15",
                status === "error"   && "bg-red-500/20",
                status === "pending" && "bg-gray-800",
              )}>
                <Icon size={18} className={NODE_COLORS[status]} />
              </div>

              {/* Text */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={clsx(
                    "text-sm font-semibold",
                    status === "pending" ? "text-gray-500" : "text-white"
                  )}>
                    Node {i + 1} — {name}
                  </span>
                  {status === "active" && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-medium animate-pulse">
                      LIVE
                    </span>
                  )}
                </div>
                <p className={clsx(
                  "text-xs mt-1",
                  status === "active"  && "text-indigo-300",
                  status === "done"    && "text-emerald-400",
                  status === "error"   && "text-red-400",
                  status === "pending" && "text-gray-600",
                )}>
                  {msg}
                </p>
              </div>

              {/* Status icon */}
              <div className="flex-shrink-0 mt-0.5">
                {status === "done"    && <CheckCircle2 size={18} className="text-emerald-400" />}
                {status === "active"  && <Loader2 size={18} className="text-indigo-400 animate-spin" />}
                {status === "error"   && <XCircle size={18} className="text-red-400" />}
                {status === "pending" && <Circle size={18} className="text-gray-700" />}
              </div>
            </div>
          );
        })}
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}
