"use client";
import { useEffect, useState, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import DraftModal, { Draft } from "@/components/DraftModal";
import PriorityBadge from "@/components/PriorityBadge";
import {
  Clock, CheckCircle2, AlertCircle, Loader2, ArrowRight,
  Users, Star, TrendingUp, Zap, Search, Filter, Mail, ExternalLink, Phone
} from "lucide-react";
import clsx from "clsx";

interface JobItem {
  job_id: string;
  status: string;
  started_at: string;
  completed_at: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function DashboardContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get('jobId');

  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Table state
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [draftModal, setDraftModal] = useState<Draft | null>(null);

  useEffect(() => {
    setLoading(true);
    if (jobId) {
      // Fetch specific result
      fetch(`${API_BASE}/api/results/${jobId}`)
        .then(r => {
          if (!r.ok) throw new Error("Failed to fetch results");
          return r.json();
        })
        .then(data => {
          setResult(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setError(err.message);
          setLoading(false);
        });
    } else {
      // Fetch jobs list
      fetch(`${API_BASE}/api/jobs`)
        .then(r => r.json())
        .then(data => {
          setJobs(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setError("Failed to fetch runs.");
          setLoading(false);
        });
    }
  }, [jobId]);

  // Derived state for the table
  const leads = result?.leads || [];
  const filteredLeads = useMemo(() => {
    return leads.filter((l: any) => {
      const pMatch = priorityFilter === "ALL" || l.lead_priority === priorityFilter;
      const q = searchQuery.toLowerCase();
      const qMatch =
        l.company_name?.toLowerCase().includes(q) ||
        l.industry?.toLowerCase().includes(q) ||
        l.contacts?.[0]?.name?.toLowerCase().includes(q) ||
        l.contacts?.[0]?.title?.toLowerCase().includes(q);
      return pMatch && (qMatch || !searchQuery);
    });
  }, [leads, priorityFilter, searchQuery]);

  const stats = useMemo(() => {
    if (!result) return null;
    let aCount = 0;
    let bCount = 0;
    let sumScore = 0;
    let validScores = 0;

    leads.forEach((l: any) => {
      if (l.lead_priority === "A") aCount++;
      if (l.lead_priority === "B") bCount++;
      const s = l.company_scores?.overall_company_score;
      if (typeof s === "number") {
        sumScore += s;
        validScores++;
      }
    });

    return {
      total: leads.length,
      aPriority: aCount,
      bPriority: bCount,
      avgScore: validScores ? Math.round(sumScore / validScores) : 0,
    };
  }, [result, leads]);

  if (loading) {
    return (
      <main className="min-h-screen pt-20">
        <Navbar />
        <div className="flex flex-col items-center justify-center py-32 text-indigo-400">
          <Loader2 className="animate-spin mb-4" size={40} />
          <p>Loading {jobId ? "results..." : "runs..."}</p>
        </div>
      </main>
    );
  }

  // --- RENDERING JOBS LIST ---
  if (!jobId) {
    return (
      <main className="min-h-screen pt-20">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-12">
          <div className="mb-10 flex justify-between items-end">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Lead Generation Runs</h1>
              <p className="text-gray-400 text-sm">View and manage your recent pipeline executions.</p>
            </div>
            <Link
              href="/search"
              className="px-4 py-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-sm font-medium hover:bg-indigo-500/20 transition-colors"
            >
              + New Run
            </Link>
          </div>
          
          {error ? (
             <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400">{error}</div>
          ) : jobs.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center">
              <h2 className="text-xl font-semibold text-white mb-2">No runs yet</h2>
              <p className="text-gray-400 text-sm mb-6">Start your first lead generation pipeline to see results here.</p>
              <Link
                href="/search"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium hover:opacity-90 transition-all"
              >
                Start Search <ArrowRight size={16} />
              </Link>
            </div>
          ) : (
            <div className="grid gap-4">
              {jobs.map((job) => (
                <Link key={job.job_id} href={`/dashboard?jobId=${job.job_id}`} className="block">
                  <div className="glass rounded-xl p-5 hover:bg-white/5 transition-colors border border-transparent hover:border-indigo-500/30 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-mono text-indigo-400 mb-1">{job.job_id.split("-")[0]}</p>
                      <p className="text-xs text-gray-400">
                        Started: {new Date(job.started_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      {job.status === "completed" ? (
                        <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium border border-emerald-500/20">
                          <CheckCircle2 size={14} /> Completed
                        </span>
                      ) : job.status === "running" ? (
                        <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-medium border border-indigo-500/20">
                          <Loader2 size={14} className="animate-spin" /> Running
                        </span>
                      ) : job.status === "error" ? (
                        <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-medium border border-red-500/20">
                          <AlertCircle size={14} /> Error
                        </span>
                      ) : (
                        <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-gray-500/10 text-gray-400 text-xs font-medium border border-gray-500/20">
                          <Clock size={14} /> Queued
                        </span>
                      )}
                      <ArrowRight size={18} className="text-gray-500" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    );
  }

  // --- RENDERING SPECIFIC RUN RESULTS (THE TABLE) ---
  if (error || !result) {
    return (
      <main className="min-h-screen pt-20">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-12 text-center">
          <AlertCircle size={40} className="mx-auto text-red-400 mb-4" />
          <h1 className="text-xl text-white">Result not found or error</h1>
          <p className="text-gray-400 mt-2">{error || "The requested job could not be loaded."}</p>
          <Link href="/dashboard" className="mt-6 inline-block text-indigo-400 hover:underline">
            &larr; Back to Dashboard
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen pt-20 pb-20">
      <Navbar />

      {/* Draft Modal */}
      <DraftModal draft={draftModal} onClose={() => setDraftModal(null)} />

      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/dashboard" className="text-xs text-indigo-400 hover:underline mb-2 inline-block">
              &larr; Back to Runs
            </Link>
            <h1 className="text-2xl font-bold text-white">Job Results</h1>
            <p className="text-xs text-gray-400 mt-1 font-mono">{jobId}</p>
          </div>
          {result.google_sheets?.spreadsheet_url && (
            <a
              href={result.google_sheets.spreadsheet_url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-sm font-medium hover:bg-emerald-500/20 transition-colors"
            >
              <ExternalLink size={14} /> View in Google Sheets
            </a>
          )}
        </div>

        {/* Top Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="glass rounded-xl p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Users size={48} className="text-indigo-400" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <Users size={14} className="text-indigo-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Leads</p>
            </div>
            <p className="text-3xl font-extrabold text-white">{stats?.total || 0}</p>
          </div>

          <div className="glass rounded-xl p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Star size={48} className="text-emerald-400" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <Star size={14} className="text-emerald-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">A-Priority</p>
            </div>
            <p className="text-3xl font-extrabold text-white">{stats?.aPriority || 0}</p>
          </div>

          <div className="glass rounded-xl p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <TrendingUp size={48} className="text-blue-400" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp size={14} className="text-blue-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">B-Priority</p>
            </div>
            <p className="text-3xl font-extrabold text-white">{stats?.bPriority || 0}</p>
          </div>

          <div className="glass rounded-xl p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Zap size={48} className="text-amber-400" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <Zap size={14} className="text-amber-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Avg Score</p>
            </div>
            <div className="flex items-baseline gap-1">
              <p className="text-3xl font-extrabold text-white">{stats?.avgScore || 0}</p>
              <p className="text-sm font-medium text-gray-500">/100</p>
            </div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between gap-4 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search company, contact, industry..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900 border border-white/10 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-indigo-500/50 transition-colors"
            />
          </div>

          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-gray-900 border border-white/5">
            <div className="px-2 border-r border-white/10">
              <Filter size={14} className="text-gray-500" />
            </div>
            {["ALL", "A", "B", "C", "D"].map((p) => {
              const active = priorityFilter === p;
              const count = p === "ALL" 
                ? leads.length 
                : leads.filter((l: any) => l.lead_priority === p).length;
                
              return (
                <button
                  key={p}
                  onClick={() => setPriorityFilter(p)}
                  className={clsx(
                    "px-3 py-1 rounded-lg text-xs font-semibold transition-all",
                    active
                      ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/20"
                      : "text-gray-400 hover:text-white hover:bg-white/5"
                  )}
                >
                  {p} {count > 0 && <span className="opacity-60 ml-1">({count})</span>}
                </button>
              );
            })}
          </div>
        </div>

        {/* Table */}
        <div className="glass rounded-2xl overflow-hidden border border-white/10">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/5 bg-white/[0.02]">
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Priority</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Company</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Contact & Channels</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Score</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Readiness</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredLeads.map((lead: any, i: number) => {
                const contact = lead.contacts?.[0] || {};
                const draft = result.email_drafts?.find((d: any) => d.company_name === lead.company_name);
                const score = lead.company_scores?.overall_company_score || 0;
                
                return (
                  <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <PriorityBadge priority={lead.lead_priority} />
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white mb-1 flex items-center gap-1.5">
                        {lead.company_name}
                        {lead.website_url && (
                          <a href={lead.website_url} target="_blank" rel="noreferrer" className="text-gray-500 hover:text-indigo-400 transition-colors">
                            <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                      <div className="text-xs text-gray-400">{lead.industry} • {lead.location}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{lead.company_size}</div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="font-medium text-white mb-0.5">{contact.name || "Unknown"}</div>
                      <div className="text-xs text-gray-400 mb-2">{contact.title || "—"}</div>
                      
                      {contact.verification_status === "verified" && (
                         <span className="inline-block mb-2 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                           verified
                         </span>
                      )}

                      <div className="space-y-1">
                        {contact.email_address && (
                          <div className="flex items-center gap-2 text-xs text-gray-300">
                            <Mail size={12} className="text-indigo-400" />
                            {contact.email_address}
                          </div>
                        )}
                        {contact.phone_number && (
                          <div className="flex items-center gap-2 text-xs text-gray-300">
                            <Phone size={12} className="text-emerald-400" />
                            {contact.phone_number}
                          </div>
                        )}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="flex-1 h-1.5 rounded-full bg-gray-800 overflow-hidden w-24">
                          <div 
                            className={clsx("h-full rounded-full", score > 80 ? "bg-emerald-500" : score > 60 ? "bg-amber-500" : "bg-red-500")} 
                            style={{ width: `${score}%` }} 
                          />
                        </div>
                        <span className="text-sm font-bold text-white">{score}</span>
                      </div>
                      <div className="text-xs text-gray-500">
                        Contact: {contact.validation_scores?.overall_contact_score || 0}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="mb-1">
                         {lead.outreach_readiness === "ready" ? (
                           <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400">ready</span>
                         ) : (
                           <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-400">{lead.outreach_readiness}</span>
                         )}
                      </div>
                      <div className="text-[10px] text-gray-500 uppercase tracking-wider">
                         via {lead.recommended_contact_method || "email"}
                      </div>
                    </td>

                    <td className="px-6 py-4 text-right space-y-2">
                      <button
                        onClick={() => setDraftModal(draft || null)}
                        disabled={!draft}
                        className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-medium hover:bg-indigo-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Mail size={13} /> View Draft
                      </button>
                      
                      {contact.linkedin_url ? (
                        <a 
                          href={contact.linkedin_url}
                          target="_blank" 
                          rel="noreferrer"
                          className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 text-gray-300 border border-white/10 text-xs font-medium hover:bg-white/10 transition-colors"
                        >
                          <ExternalLink size={13} /> LinkedIn
                        </a>
                      ) : (
                        <button disabled className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 text-gray-600 border border-white/5 text-xs font-medium cursor-not-allowed">
                          No LinkedIn
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
              {filteredLeads.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No leads match your current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
