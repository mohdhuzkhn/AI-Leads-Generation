"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import {
  MapPin, Building2, Users, Hash, Target,
  Zap, ArrowRight, Loader2
} from "lucide-react";
import clsx from "clsx";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const INDUSTRIES = [
  "SaaS", "Fintech", "Healthcare", "E-commerce", "Logistics",
  "EdTech", "PropTech", "Cybersecurity", "AI / ML", "Consulting",
  "Marketing Agency", "Retail", "Manufacturing", "Legal Tech",
];

const COMPANY_SIZES = [
  "1-10 employees", "11-50 employees", "51-200 employees", "201-500 employees", "500+ employees",
];

const PERSONAS = ["CEO", "Founder", "Co-Founder", "CTO", "CMO", "COO", "VP Sales", "Head of Growth"];

export default function SearchPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [useDemo, setUseDemo] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    location: "",
    industry: "SaaS",
    company_size: "11-50 employees",
    limit: 5,
    target_persona: ["CEO", "Founder"] as string[],
  });

  const togglePersona = (p: string) => {
    setForm((prev) => ({
      ...prev,
      target_persona: prev.target_persona.includes(p)
        ? prev.target_persona.filter((x) => x !== p)
        : [...prev.target_persona, p],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.location.trim()) { setError("Please enter a location."); return; }
    if (form.target_persona.length === 0) { setError("Select at least one persona."); return; }
    setError(null);
    setLoading(true);

    try {
      const endpoint = useDemo ? "/api/demo" : "/api/run";
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      router.push(`/agent/${data.job_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to start job");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen pt-20">
      <Navbar />

      <div className="max-w-2xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/5 text-xs text-indigo-400 font-medium mb-4">
            <Zap size={11} />
            4-Agent Pipeline
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">
            Configure your <span className="gradient-text">Lead Search</span>
          </h1>
          <p className="text-gray-400 text-sm">
            Define your target market and let the agent do the heavy lifting.
          </p>
        </div>

        {/* Form card */}
        <form onSubmit={handleSubmit} className="glass rounded-2xl p-6 space-y-6">

          {/* Demo toggle */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-amber-500/5 border border-amber-500/15">
            <div>
              <p className="text-xs font-semibold text-amber-400">Demo Mode</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {useDemo ? "Uses simulated pipeline (~20s). No API keys needed." : "Runs the real CrewAI pipeline (requires API keys, ~10min)."}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setUseDemo(!useDemo)}
              className={clsx(
                "relative w-11 h-6 rounded-full transition-colors",
                useDemo ? "bg-amber-500" : "bg-gray-700"
              )}
            >
              <span className={clsx(
                "absolute top-1 w-4 h-4 rounded-full bg-white shadow transition-transform",
                useDemo ? "translate-x-6" : "translate-x-1"
              )} />
            </button>
          </div>

          {/* Location */}
          <div>
            <label className="flex items-center gap-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              <MapPin size={12} /> Location *
            </label>
            <input
              id="input-location"
              type="text"
              placeholder="e.g. Dubai, UAE · London, UK · San Francisco, CA"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              className="w-full px-4 py-3 rounded-xl bg-gray-900 border border-white/8 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-indigo-500/50 transition-colors"
            />
          </div>

          {/* Industry */}
          <div>
            <label className="flex items-center gap-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              <Building2 size={12} /> Industry
            </label>
            <div className="flex flex-wrap gap-2">
              {INDUSTRIES.map((ind) => (
                <button
                  key={ind}
                  type="button"
                  id={`industry-${ind.toLowerCase().replace(/\W/g, "-")}`}
                  onClick={() => setForm({ ...form, industry: ind })}
                  className={clsx(
                    "px-3 py-1.5 rounded-lg text-xs font-medium border transition-all",
                    form.industry === ind
                      ? "bg-indigo-500/15 border-indigo-500/40 text-indigo-300"
                      : "border-white/8 text-gray-500 hover:border-white/20 hover:text-gray-300"
                  )}
                >
                  {ind}
                </button>
              ))}
            </div>
          </div>

          {/* Company size */}
          <div>
            <label className="flex items-center gap-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              <Users size={12} /> Company Size
            </label>
            <div className="flex flex-wrap gap-2">
              {COMPANY_SIZES.map((sz) => (
                <button
                  key={sz}
                  type="button"
                  id={`size-${sz.replace(/\s/g, "-")}`}
                  onClick={() => setForm({ ...form, company_size: sz })}
                  className={clsx(
                    "px-3 py-1.5 rounded-lg text-xs font-medium border transition-all",
                    form.company_size === sz
                      ? "bg-purple-500/15 border-purple-500/40 text-purple-300"
                      : "border-white/8 text-gray-500 hover:border-white/20 hover:text-gray-300"
                  )}
                >
                  {sz}
                </button>
              ))}
            </div>
          </div>

          {/* Limit slider */}
          <div>
            <label className="flex items-center justify-between text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              <span className="flex items-center gap-2"><Hash size={12} /> Lead Limit</span>
              <span className="text-indigo-400 font-bold text-sm normal-case">{form.limit} companies</span>
            </label>
            <input
              id="input-limit"
              type="range" min={1} max={50} step={1}
              value={form.limit}
              onChange={(e) => setForm({ ...form, limit: Number(e.target.value) })}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>1</span><span>25</span><span>50</span>
            </div>
          </div>

          {/* Target Persona */}
          <div>
            <label className="flex items-center gap-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              <Target size={12} /> Target Persona (select all that apply)
            </label>
            <div className="flex flex-wrap gap-2">
              {PERSONAS.map((p) => (
                <button
                  key={p}
                  type="button"
                  id={`persona-${p.toLowerCase().replace(/\s/g, "-")}`}
                  onClick={() => togglePersona(p)}
                  className={clsx(
                    "px-3 py-1.5 rounded-lg text-xs font-medium border transition-all",
                    form.target_persona.includes(p)
                      ? "bg-cyan-500/15 border-cyan-500/40 text-cyan-300"
                      : "border-white/8 text-gray-500 hover:border-white/20 hover:text-gray-300"
                  )}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            id="btn-generate-leads"
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-base disabled:opacity-60 hover:opacity-90 transition-all shadow-lg shadow-indigo-500/25"
          >
            {loading ? (
              <><Loader2 size={18} className="animate-spin" /> Starting pipeline...</>
            ) : (
              <>Generate Leads <ArrowRight size={18} /></>
            )}
          </button>
        </form>

        {/* Summary */}
        <div className="mt-6 grid grid-cols-3 gap-3">
          {[
            { label: "Company Discovery", detail: "Boolean + Scrape" },
            { label: "Contact Enrichment", detail: "LinkedIn · Email · Phone" },
            { label: "Lead Scoring + Outreach", detail: "A/B/C/D · Gmail Drafts" },
          ].map((item) => (
            <div key={item.label} className="glass rounded-xl p-3 text-center">
              <p className="text-[10px] font-bold text-indigo-400 uppercase">{item.label}</p>
              <p className="text-[10px] text-gray-500 mt-0.5">{item.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
