"use client";
import { useRouter } from "next/navigation";
import { use } from "react";
import Navbar from "@/components/Navbar";
import AgentProgress from "@/components/AgentProgress";
import { Zap } from "lucide-react";

interface PageProps {
  params: Promise<{ jobId: string }>;
}

export default function AgentPage({ params }: PageProps) {
  const { jobId } = use(params);
  const router = useRouter();

  const handleComplete = () => {
    router.push(`/dashboard?jobId=${jobId}`);
  };

  return (
    <main className="min-h-screen pt-20">
      <Navbar />

      <div className="max-w-2xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/5 text-xs text-indigo-400 font-medium mb-4">
            <Zap size={11} className="animate-pulse" />
            Agent Running — Live Status
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Pipeline in Progress
          </h1>
          <p className="text-sm text-gray-400">
            Job ID:{" "}
            <code className="text-indigo-400 font-mono text-xs bg-indigo-500/10 px-2 py-0.5 rounded">
              {jobId}
            </code>
          </p>
        </div>

        {/* Progress component (SSE-driven) */}
        <AgentProgress jobId={jobId} onComplete={handleComplete} />

        {/* Info footer */}
        <div className="mt-10 p-4 rounded-xl bg-white/[0.02] border border-white/5 text-center">
          <p className="text-xs text-gray-500">
            This page updates in real-time via Server-Sent Events.
            Results will appear automatically when the pipeline completes.
          </p>
        </div>
      </div>
    </main>
  );
}
