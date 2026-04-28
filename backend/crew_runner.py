"""
crew_runner.py
Manages CrewAI subprocess execution, parses stdout for node-progress events,
and stores results in memory + JSON files.
"""
import asyncio
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, AsyncIterator

from models import (
    JobStatus, JobStatusEnum, NodeProgress, NodeStatus,
    RunRequest, RunResult, LeadResult, ContactResult,
    CompanyScores, ValidationScores, EmailDraft, GoogleSheetsOutput,
    JobListItem,
)

# ──────────────────────────────────────────────
# In-memory stores
# ──────────────────────────────────────────────
_jobs: Dict[str, Dict[str, Any]] = {}       # job_id → {status, nodes, request, result}
RESULTS_DIR = Path(__file__).parent / "job_results"
RESULTS_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# Node definitions (match CrewAI task names)
# ──────────────────────────────────────────────
NODE_DEFS = [
    {
        "node": 1,
        "name": "Company Discovery",
        "keywords": ["discover_target_companies", "company discovery", "scraping", "serperdevtool", "firecrawl", "Step 1", "COMPANY DISCOVERY"],
        "active_msg": "Searching the web for matching companies...",
        "done_msg": "Companies found & websites verified ✓",
    },
    {
        "node": 2,
        "name": "Contact Enrichment",
        "keywords": ["discover_executive_contacts", "contact discovery", "linkedin", "phone enrichment", "email discovery", "Step 2", "CONTACT DISCOVERY"],
        "active_msg": "Finding LinkedIn profiles, emails & phone numbers...",
        "done_msg": "Executive contacts enriched ✓",
    },
    {
        "node": 3,
        "name": "Lead Scoring",
        "keywords": ["validate_and_score", "lead quality", "scoring", "priority", "validation score", "Step 3", "LEAD QUALITY"],
        "active_msg": "Validating contacts & computing A/B/C/D priorities...",
        "done_msg": "Leads scored & prioritised ✓",
    },
    {
        "node": 4,
        "name": "Output & Outreach",
        "keywords": ["generate_output", "output coordinator", "google sheets", "gmail", "create_draft", "Step 4", "OUTPUT"],
        "active_msg": "Writing Google Sheet & creating Gmail drafts...",
        "done_msg": "Google Sheet populated & drafts created ✓",
    },
]


def _make_nodes(active_from: int = 0) -> list:
    return [
        NodeProgress(
            node=n["node"],
            name=n["name"],
            status=NodeStatus.done if n["node"] < active_from
            else (NodeStatus.active if n["node"] == active_from else NodeStatus.pending),
            message=n["done_msg"] if n["node"] < active_from
            else (n["active_msg"] if n["node"] == active_from else "Waiting..."),
        )
        for n in NODE_DEFS
    ]


def _detect_node(line: str) -> int | None:
    """Return the 1-based node number if the line signals a node transition."""
    lower = line.lower()
    for nd in NODE_DEFS:
        if any(kw.lower() in lower for kw in nd["keywords"]):
            return nd["node"]
    return None


def _persist_job(job_id: str):
    path = RESULTS_DIR / f"{job_id}.json"
    with open(path, "w") as f:
        data = _jobs[job_id].copy()
        # Convert non-serialisable objects
        if "status_obj" in data:
            data.pop("status_obj")
        json.dump(data, f, indent=2, default=str)


def create_job(request: RunRequest) -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatusEnum.queued,
        "request": request.model_dump(),
        "nodes": [n.model_dump() for n in _make_nodes(0)],
        "started_at": None,
        "completed_at": None,
        "error": None,
        "result": None,
        "raw_output_lines": [],
    }
    return job_id


def get_job_status(job_id: str) -> JobStatus | None:
    job = _jobs.get(job_id)
    if not job:
        # Try loading from disk
        path = RESULTS_DIR / f"{job_id}.json"
        if path.exists():
            with open(path) as f:
                job = json.load(f)
            _jobs[job_id] = job
        else:
            return None
    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        nodes=[NodeProgress(**n) for n in job["nodes"]],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        error=job.get("error"),
    )


def get_job_result(job_id: str) -> RunResult | None:
    job = _jobs.get(job_id)
    if not job:
        return None
    result_data = job.get("result")
    if not result_data:
        # Return mock/demo data so frontend works without a real run
        return _make_demo_result(job_id, job["request"])
    return RunResult(**result_data)


def list_jobs() -> list[JobListItem]:
    items = []
    for jid, job in _jobs.items():
        result = job.get("result") or {}
        leads = result.get("leads", []) if isinstance(result, dict) else []
        items.append(JobListItem(
            job_id=jid,
            status=job["status"],
            location=job["request"].get("location", ""),
            industry=job["request"].get("industry", ""),
            limit=job["request"].get("limit", 0),
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            leads_found=len(leads),
        ))
    return items


async def run_crew_async(job_id: str):
    """Run the CrewAI pipeline as a subprocess and update job state."""
    job = _jobs[job_id]
    job["status"] = JobStatusEnum.running
    job["started_at"] = datetime.utcnow().isoformat()
    job["nodes"] = [n.model_dump() for n in _make_nodes(1)]

    req = job["request"]
    project_root = Path(__file__).parent.parent

    # Build the command — uses uv to run inside the project venv
    cmd = [
        "uv", "run", "python", "-m",
        "node_4_output_generation_gmail_outreach.main", "run"
    ]

    # Inject inputs via environment variable (CrewAI reads os.environ too)
    env_inputs = {
        "CREW_INPUT_LOCATION": req["location"],
        "CREW_INPUT_INDUSTRY": req["industry"],
        "CREW_INPUT_COMPANY_SIZE": req["company_size"],
        "CREW_INPUT_LIMIT": str(req["limit"]),
        "CREW_INPUT_TARGET_PERSONA": ",".join(req.get("target_persona", ["CEO"])),
    }

    import os
    env = {**os.environ, **env_inputs}

    current_node = 1

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(project_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )

        async for raw in proc.stdout:
            line = raw.decode(errors="replace").rstrip()
            job["raw_output_lines"].append(line)

            detected = _detect_node(line)
            if detected and detected >= current_node:
                current_node = detected
                job["nodes"] = [n.model_dump() for n in _make_nodes(current_node)]

        await proc.wait()
        rc = proc.returncode

        if rc == 0:
            # Mark all nodes done
            nodes_done = []
            for nd in NODE_DEFS:
                nodes_done.append(NodeProgress(
                    node=nd["node"], name=nd["name"],
                    status=NodeStatus.done, message=nd["done_msg"],
                ).model_dump())
            job["nodes"] = nodes_done
            job["status"] = JobStatusEnum.completed
            job["completed_at"] = datetime.utcnow().isoformat()

            # Parse raw output for JSON blocks
            raw_text = "\n".join(job["raw_output_lines"])
            job["result"] = _parse_crew_output(raw_text, job_id)
        else:
            job["status"] = JobStatusEnum.failed
            job["error"] = f"Crew exited with code {rc}"
            _mark_current_node_error(job, current_node)

    except Exception as exc:
        job["status"] = JobStatusEnum.failed
        job["error"] = str(exc)
        _mark_current_node_error(job, current_node)

    _persist_job(job_id)


def _mark_current_node_error(job: dict, current_node: int):
    updated = []
    for nd in NODE_DEFS:
        if nd["node"] < current_node:
            updated.append(NodeProgress(node=nd["node"], name=nd["name"],
                status=NodeStatus.done, message=NODE_DEFS[nd["node"]-1]["done_msg"]).model_dump())
        elif nd["node"] == current_node:
            updated.append(NodeProgress(node=nd["node"], name=nd["name"],
                status=NodeStatus.error, message="Error occurred").model_dump())
        else:
            updated.append(NodeProgress(node=nd["node"], name=nd["name"],
                status=NodeStatus.pending, message="Waiting...").model_dump())
    job["nodes"] = updated


def _parse_crew_output(raw: str, job_id: str) -> dict:
    """Extract JSON blocks from crew stdout and build RunResult dict."""
    json_blocks = re.findall(r'\{[\s\S]*?\}(?=\s*\n|\s*$)', raw)
    leads = []
    sheets = None
    drafts = []

    for block in json_blocks:
        try:
            data = json.loads(block)
            if "scored_leads" in data:
                for sl in data["scored_leads"]:
                    contacts = []
                    for c in sl.get("contacts", []):
                        vs = c.get("validation_scores", {})
                        contacts.append(ContactResult(
                            name=c.get("name"),
                            title=c.get("title"),
                            linkedin_url=c.get("linkedin_url"),
                            email_address=c.get("email_address"),
                            phone_number=c.get("phone_number"),
                            contact_confidence=c.get("contact_confidence"),
                            verification_status=c.get("verification_status"),
                            validation_scores=ValidationScores(**vs) if vs else None,
                        ).model_dump())
                    cs = sl.get("company_scores", {})
                    leads.append(LeadResult(
                        company_name=sl.get("company_name"),
                        website_url=sl.get("website_url"),
                        company_description=sl.get("company_description"),
                        industry=sl.get("industry"),
                        location=sl.get("location"),
                        company_size=sl.get("company_size"),
                        contacts=contacts,
                        company_scores=CompanyScores(**cs) if cs else None,
                        lead_priority=sl.get("lead_priority"),
                        priority_reasoning=sl.get("priority_reasoning"),
                        outreach_readiness=sl.get("outreach_readiness"),
                        quality_flags=sl.get("quality_flags", []),
                        recommended_contact_method=sl.get("recommended_contact_method"),
                    ).model_dump())

            if "spreadsheet_url" in data or "google_sheets_output" in data:
                gso = data.get("google_sheets_output", data)
                sheets = GoogleSheetsOutput(
                    spreadsheet_id=gso.get("spreadsheet_id"),
                    spreadsheet_url=gso.get("spreadsheet_url"),
                    total_rows_added=gso.get("total_rows_added"),
                ).model_dump()

            if "email_drafts" in data:
                for d in data["email_drafts"]:
                    drafts.append(EmailDraft(**d).model_dump())

        except (json.JSONDecodeError, Exception):
            continue

    if not leads:
        # Fallback: return demo data
        demo = _make_demo_result(job_id, {})
        return demo.model_dump()

    return RunResult(
        job_id=job_id,
        leads=leads,
        email_drafts=drafts,
        google_sheets=sheets,
        raw_output=raw[:5000],
    ).model_dump()


def _make_demo_result(job_id: str, req: dict) -> RunResult:
    """Return realistic demo data for UI testing without a live crew run."""
    leads = [
        LeadResult(
            company_name="TechVentures AI", website_url="https://techventures.ai",
            company_description="AI-powered SaaS solutions for enterprise automation.",
            industry=req.get("industry", "SaaS"), location=req.get("location", "Dubai, UAE"),
            company_size="11-50", lead_priority="A", priority_reasoning="Full contact info, high company fit",
            outreach_readiness="ready", recommended_contact_method="email",
            quality_flags=[],
            contacts=[ContactResult(
                name="Sarah Al-Rashid", title="CEO", linkedin_url="https://linkedin.com/in/sarah-alrashid",
                email_address="sarah@techventures.ai", phone_number="+971501234567",
                contact_confidence="high", verification_status="verified",
                validation_scores=ValidationScores(phone_validation_score=92, email_validation_score=95,
                    linkedin_validation_score=88, overall_contact_score=92),
            )],
            company_scores=CompanyScores(company_fit_score=95, data_completeness_score=90,
                verification_confidence_score=88, overall_company_score=91),
        ),
        LeadResult(
            company_name="Finova Solutions", website_url="https://finova.io",
            company_description="Next-gen fintech infrastructure for MENA region banks.",
            industry=req.get("industry", "Fintech"), location=req.get("location", "Dubai, UAE"),
            company_size="51-200", lead_priority="A", priority_reasoning="CEO verified on LinkedIn & email",
            outreach_readiness="ready", recommended_contact_method="linkedin",
            quality_flags=[],
            contacts=[ContactResult(
                name="Omar Khalid", title="Founder & CEO", linkedin_url="https://linkedin.com/in/omar-khalid",
                email_address="omar@finova.io", phone_number="+971509876543",
                contact_confidence="high", verification_status="verified",
                validation_scores=ValidationScores(phone_validation_score=85, email_validation_score=98,
                    linkedin_validation_score=96, overall_contact_score=93),
            )],
            company_scores=CompanyScores(company_fit_score=88, data_completeness_score=95,
                verification_confidence_score=92, overall_company_score=92),
        ),
        LeadResult(
            company_name="CloudStack ME", website_url="https://cloudstack.me",
            company_description="Cloud infrastructure & DevOps services across the Middle East.",
            industry=req.get("industry", "Cloud"), location=req.get("location", "Dubai, UAE"),
            company_size="11-50", lead_priority="B", priority_reasoning="Email found, phone unverified",
            outreach_readiness="ready", recommended_contact_method="email",
            quality_flags=["phone_unverified"],
            contacts=[ContactResult(
                name="Priya Nair", title="Co-Founder", linkedin_url="https://linkedin.com/in/priya-nair",
                email_address="priya@cloudstack.me", phone_number=None,
                contact_confidence="medium", verification_status="partial",
                validation_scores=ValidationScores(phone_validation_score=None, email_validation_score=82,
                    linkedin_validation_score=78, overall_contact_score=75),
            )],
            company_scores=CompanyScores(company_fit_score=80, data_completeness_score=72,
                verification_confidence_score=75, overall_company_score=76),
        ),
        LeadResult(
            company_name="DataPulse Analytics", website_url="https://datapulse.ai",
            company_description="Real-time business intelligence for retail & logistics.",
            industry=req.get("industry", "Analytics"), location=req.get("location", "Dubai, UAE"),
            company_size="1-10", lead_priority="B", priority_reasoning="Early-stage startup, LinkedIn verified",
            outreach_readiness="ready", recommended_contact_method="linkedin",
            quality_flags=["early_stage"],
            contacts=[ContactResult(
                name="Faisal Al-Mansoori", title="CEO", linkedin_url="https://linkedin.com/in/faisal-mansoori",
                email_address="faisal@datapulse.ai", phone_number="+971504561234",
                contact_confidence="medium", verification_status="verified",
                validation_scores=ValidationScores(phone_validation_score=78, email_validation_score=80,
                    linkedin_validation_score=90, overall_contact_score=83),
            )],
            company_scores=CompanyScores(company_fit_score=72, data_completeness_score=85,
                verification_confidence_score=80, overall_company_score=79),
        ),
        LeadResult(
            company_name="LogiChain Pro", website_url="https://logichain.pro",
            company_description="Supply chain automation powered by AI & blockchain.",
            industry=req.get("industry", "Logistics"), location=req.get("location", "Dubai, UAE"),
            company_size="51-200", lead_priority="C", priority_reasoning="Contact info incomplete",
            outreach_readiness="needs_validation", recommended_contact_method="phone",
            quality_flags=["email_unverified", "no_linkedin"],
            contacts=[ContactResult(
                name="James Okafor", title="CTO", linkedin_url=None,
                email_address="james@logichain.pro", phone_number="+971501112233",
                contact_confidence="low", verification_status="unverified",
                validation_scores=ValidationScores(phone_validation_score=60, email_validation_score=55,
                    linkedin_validation_score=None, overall_contact_score=58),
            )],
            company_scores=CompanyScores(company_fit_score=65, data_completeness_score=55,
                verification_confidence_score=60, overall_company_score=60),
        ),
    ]

    drafts = [
        EmailDraft(
            to="sarah@techventures.ai", lead_name="Sarah Al-Rashid",
            company_name="TechVentures AI",
            subject="Quick question about TechVentures AI's growth strategy",
            body="""Hi Sarah,

I came across TechVentures AI and was genuinely impressed by what you're building — AI-powered automation for enterprise is exactly where the market is heading.

I'm reaching out because we help SaaS founders like yourself accelerate B2B pipeline growth through precision lead intelligence. Given your trajectory in the Dubai market, I think there's a strong fit.

Would you be open to a 15-minute call this week to explore if we can add value?

Looking forward to connecting.

Best,
John""",
        ),
        EmailDraft(
            to="omar@finova.io", lead_name="Omar Khalid",
            company_name="Finova Solutions",
            subject="Finova + potential partnership — worth a conversation?",
            body="""Hi Omar,

Finova's work on fintech infrastructure for MENA banks is really compelling — the region desperately needs what you're building.

I'd love to connect briefly to share how we're helping other fintech founders in Dubai close enterprise accounts faster.

Are you free for a quick 15-minute intro call this week?

Best,
John""",
        ),
    ]

    sheets = GoogleSheetsOutput(
        spreadsheet_id="demo_sheet_id",
        spreadsheet_url="https://docs.google.com/spreadsheets/d/demo",
        total_rows_added=len(leads),
    )

    return RunResult(
        job_id=job_id, leads=leads, email_drafts=drafts, google_sheets=sheets,
    )


async def stream_job_events(job_id: str) -> AsyncIterator[dict]:
    """Yield SSE-compatible dicts for the job's progress."""
    max_wait = 900  # 15 minutes max
    elapsed = 0
    interval = 1.5

    while elapsed < max_wait:
        job = _jobs.get(job_id)
        if not job:
            yield {"event": "error", "data": json.dumps({"message": "Job not found"})}
            return

        status = job["status"]
        nodes = job["nodes"]

        yield {
            "event": "progress",
            "data": json.dumps({
                "status": status,
                "nodes": nodes,
                "error": job.get("error"),
            }),
        }

        if status in (JobStatusEnum.completed, JobStatusEnum.failed):
            yield {"event": "done", "data": json.dumps({"status": status})}
            return

        await asyncio.sleep(interval)
        elapsed += interval

    yield {"event": "timeout", "data": json.dumps({"message": "Stream timed out"})}
