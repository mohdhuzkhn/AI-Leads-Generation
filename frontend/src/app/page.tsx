import Link from "next/link";
import Navbar from "@/components/Navbar";
import {
  Search, Users, BarChart2, Send, Zap,
  CheckCircle, Star, ArrowRight, Globe,
  Phone, Link2, Mail, Shield
} from "lucide-react";

// ─── Feature cards ────────────────────────────────────────────
const features = [
  {
    icon: Search,
    title: "Advanced Boolean Search",
    desc: "LinkedIn + web boolean queries built by AI to find exactly the companies you want — no false positives.",
    color: "from-indigo-500 to-blue-500",
  },
  {
    icon: Phone,
    title: "Phone Number Enrichment",
    desc: "Multi-source phone validation gives you direct lines to CEOs, not call centers.",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: BarChart2,
    title: "A/B/C/D Lead Scoring",
    desc: "5-dimensional scoring engine evaluates every lead instantly — so your sales team focuses on what converts.",
    color: "from-cyan-500 to-teal-500",
  },
  {
    icon: Mail,
    title: "Gmail Outreach Automation",
    desc: "Personalised email drafts created for every A/B priority lead and pushed directly to your Gmail.",
    color: "from-emerald-500 to-green-500",
  },
  {
    icon: Link2,
    title: "LinkedIn Profile Discovery",
    desc: "Automated LinkedIn boolean generation finds verified executive profiles across every company.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Globe,
    title: "Google Sheets Export",
    desc: "All 14 lead data-points written to a dated Google Sheet for seamless team collaboration.",
    color: "from-amber-500 to-orange-500",
  },
];

// ─── Pricing ──────────────────────────────────────────────────
const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    desc: "Perfect for testing the pipeline",
    features: ["3 leads per run", "Company Discovery", "Basic email enrichment", "CSV export"],
    cta: "Get Started",
    href: "/search",
    highlight: false,
  },
  {
    name: "Basic",
    price: "$29",
    period: "/month",
    desc: "For solo founders & SDRs",
    features: [
      "50 leads per run",
      "Phone enrichment",
      "LinkedIn discovery",
      "Lead scoring (A/B/C/D)",
      "Google Sheets export",
      "5 Gmail drafts per run",
    ],
    cta: "Start Basic",
    href: "/search",
    highlight: true,
  },
  {
    name: "Pro",
    price: "$99",
    period: "/month",
    desc: "For sales teams & agencies",
    features: [
      "Unlimited leads",
      "Multi-source phone validation",
      "Full Gmail outreach suite",
      "Priority queue",
      "API access",
      "Custom personas",
      "Priority support",
    ],
    cta: "Go Pro",
    href: "/search",
    highlight: false,
  },
];

// ─── Testimonials ─────────────────────────────────────────────
const testimonials = [
  {
    name: "Sarah Al-Rashid",
    role: "Founder, TechVentures AI",
    avatar: "SA",
    quote:
      "LeadForge cut our prospecting time from 3 hours to 8 minutes per campaign. The phone validation alone is worth every penny.",
    stars: 5,
  },
  {
    name: "Omar Khalid",
    role: "CEO, Finova Solutions",
    avatar: "OK",
    quote:
      "The Gmail drafts are shockingly good — personalised enough that our reply rate went from 3% to 18% in the first week.",
    stars: 5,
  },
  {
    name: "Priya Nair",
    role: "Head of Growth, CloudStack ME",
    avatar: "PN",
    quote:
      "I gave it 'SaaS, Dubai, 11-50 employees' and got 10 scored, verified leads with email drafts in under 12 minutes. Insane.",
    stars: 5,
  },
];

// ─── Stat bar ─────────────────────────────────────────────────
const stats = [
  { value: "10x", label: "Faster than manual research" },
  { value: "94%", label: "Contact find rate" },
  { value: "18%", label: "Avg reply rate on AI drafts" },
  { value: "< 12m", label: "End-to-end for 10 leads" },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Navbar />

      {/* ── Hero ────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-24 px-4 overflow-hidden">
        {/* Background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[500px] bg-indigo-500/8 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-20 left-1/4 w-[400px] h-[300px] bg-purple-500/6 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/5 text-xs text-indigo-400 font-medium mb-6">
            <Zap size={11} />
            Powered by CrewAI + GPT-4o-mini
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-white leading-tight mb-6">
            Find, Score &amp; Reach{" "}
            <span className="gradient-text">B2B Leads</span>
            <br />in Minutes, Not Days
          </h1>

          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            A 4-agent AI pipeline that discovers companies, enriches executive
            contacts, scores every lead A→D, and drafts personalised Gmail
            outreach — fully automated.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/search"
              id="hero-cta-start"
              className="flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-base hover:opacity-90 transition-all shadow-2xl shadow-indigo-500/30 hover:shadow-indigo-500/50"
            >
              Generate Leads Now
              <ArrowRight size={18} />
            </Link>
            <Link
              href="/dashboard"
              id="hero-cta-demo"
              className="flex items-center gap-2 px-8 py-4 rounded-xl glass border border-white/10 text-white font-semibold text-base hover:border-indigo-500/30 transition-all"
            >
              View Live Demo
            </Link>
          </div>

          {/* Social proof */}
          <p className="mt-6 text-xs text-gray-500">
            ✓ No credit card &nbsp;·&nbsp; ✓ 3 free leads &nbsp;·&nbsp; ✓ Works in &lt;12 minutes
          </p>
        </div>
      </section>

      {/* ── Stats bar ───────────────────────────────────────── */}
      <section className="py-12 border-y border-white/5">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <p className="text-3xl font-extrabold gradient-text">{s.value}</p>
              <p className="text-xs text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────── */}
      <section id="features" className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Everything your pipeline needs
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Six specialised AI capabilities, working in concert across 4 sequential nodes.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => (
              <div
                key={f.title}
                className="glass rounded-2xl p-6 hover:border-indigo-500/20 transition-all group"
              >
                <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 shadow-lg`}>
                  <f.icon size={20} className="text-white" />
                </div>
                <h3 className="text-base font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────── */}
      <section className="py-20 px-4 border-y border-white/5">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">4 Nodes. One result.</h2>
          <p className="text-gray-400">Each agent hands off to the next — zero human effort required.</p>
        </div>
        <div className="max-w-3xl mx-auto relative">
          {/* Vertical line */}
          <div className="absolute left-5 top-6 bottom-6 w-px bg-gradient-to-b from-indigo-500/50 via-purple-500/30 to-transparent hidden sm:block" />

          {[
            { n: 1, icon: Search,    title: "Company Discovery",   desc: "Boolean search + website scraping for verified companies" },
            { n: 2, icon: Users,     title: "Contact Enrichment",  desc: "CEO / Founder contacts: LinkedIn, email, phone" },
            { n: 3, icon: BarChart2, title: "Lead Scoring",        desc: "5-metric scoring → A/B/C/D priority grade" },
            { n: 4, icon: Send,      title: "Output & Outreach",   desc: "Google Sheet + personalised Gmail drafts" },
          ].map((step) => (
            <div key={step.n} className="flex items-start gap-5 mb-8 relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-500/30 z-10">
                <step.icon size={17} className="text-white" />
              </div>
              <div className="glass rounded-xl p-4 flex-1">
                <p className="text-xs text-indigo-400 font-semibold mb-0.5">NODE {step.n}</p>
                <h3 className="text-sm font-bold text-white">{step.title}</h3>
                <p className="text-xs text-gray-400 mt-1">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pricing ─────────────────────────────────────────── */}
      <section id="pricing" className="py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-bold text-white mb-4">Simple, transparent pricing</h2>
            <p className="text-gray-400">Start free. Scale when you need more leads.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative rounded-2xl p-6 flex flex-col ${
                  plan.highlight
                    ? "gradient-border bg-gray-900"
                    : "glass"
                }`}
              >
                {plan.highlight && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold shadow-lg">
                    MOST POPULAR
                  </div>
                )}
                <div className="mb-6">
                  <p className="text-gray-400 text-sm font-medium">{plan.name}</p>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-4xl font-extrabold text-white">{plan.price}</span>
                    <span className="text-gray-500 text-sm">{plan.period}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{plan.desc}</p>
                </div>

                <ul className="space-y-2.5 flex-1 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle size={14} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.href}
                  className={`block text-center py-2.5 rounded-xl font-semibold text-sm transition-all ${
                    plan.highlight
                      ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:opacity-90 shadow-lg shadow-indigo-500/25"
                      : "border border-white/10 text-white hover:border-indigo-500/30 hover:bg-white/5"
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Testimonials ────────────────────────────────────── */}
      <section id="testimonials" className="py-20 px-4 border-t border-white/5">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-bold text-white mb-4">Trusted by growth teams</h2>
            <p className="text-gray-400">What our users say after their first run.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {testimonials.map((t) => (
              <div key={t.name} className="glass rounded-2xl p-6">
                {/* Stars */}
                <div className="flex gap-0.5 mb-4">
                  {Array(t.stars).fill(0).map((_, i) => (
                    <Star key={i} size={14} className="text-amber-400 fill-amber-400" />
                  ))}
                </div>

                <p className="text-sm text-gray-300 leading-relaxed mb-5 italic">
                  &ldquo;{t.quote}&rdquo;
                </p>

                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                    {t.avatar}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">{t.name}</p>
                    <p className="text-xs text-gray-500">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ──────────────────────────────────────── */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto text-center glass rounded-3xl p-12 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/5 rounded-3xl pointer-events-none" />
          <Shield size={32} className="text-indigo-400 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-3">
            Start your first free run
          </h2>
          <p className="text-gray-400 mb-8">
            3 leads, fully enriched, scored and drafted — no credit card required.
          </p>
          <Link
            href="/search"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-base hover:opacity-90 transition-all shadow-2xl shadow-indigo-500/30"
          >
            Generate Leads Free <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────── */}
      <footer className="border-t border-white/5 py-8 px-4">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Zap size={12} className="text-white" />
            </div>
            <span className="text-sm text-gray-500">LeadForge AI © 2026</span>
          </div>
          <p className="text-xs text-gray-600">
            Built on CrewAI · GPT-4o-mini · Google Workspace APIs
          </p>
        </div>
      </footer>
    </main>
  );
}
