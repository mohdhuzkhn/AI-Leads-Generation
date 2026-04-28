"""
main.py — FastAPI backend for the Lead Generation platform
Run: uvicorn main:app --reload --port 8000
"""
import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from models import RunRequest, RunResponse, JobListItem
from crew_runner import (
    create_job, get_job_status, get_job_result,
    list_jobs, run_crew_async, stream_job_events,
    _make_demo_result,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lead Gen API is running on http://localhost:8000")
    yield


app = FastAPI(
    title="Lead Generation Agent API",
    description="FastAPI backend powering the CrewAI lead generation pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "Lead Gen API"}


# ─────────────────────────────────────────────────────────────
# Run a new job
# ─────────────────────────────────────────────────────────────
@app.post("/api/run", response_model=RunResponse, tags=["Jobs"])
async def run_crew(request: RunRequest, background_tasks: BackgroundTasks):
    """
    Start a CrewAI lead generation run.
    Returns a job_id immediately; use /api/status/{job_id} for live updates.
    """
    job_id = create_job(request)
    background_tasks.add_task(run_crew_async, job_id)
    return RunResponse(job_id=job_id, message="Job started. Track progress via /api/status/" + job_id)


# ─────────────────────────────────────────────────────────────
# Live SSE status stream
# ─────────────────────────────────────────────────────────────
@app.get("/api/status/{job_id}", tags=["Jobs"])
async def job_status_stream(job_id: str):
    """
    Server-Sent Events stream of node progress for a running job.
    Events: progress | done | error | timeout
    """
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def generator():
        async for event in stream_job_events(job_id):
            yield event

    return EventSourceResponse(generator())


# ─────────────────────────────────────────────────────────────
# Get final results
# ─────────────────────────────────────────────────────────────
@app.get("/api/results/{job_id}", tags=["Jobs"])
def job_results(job_id: str):
    """Return the full structured results for a completed job."""
    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")

    result = get_job_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Results not available yet")

    return result


# ─────────────────────────────────────────────────────────────
# Demo endpoint — returns fake data without running the crew
# ─────────────────────────────────────────────────────────────
@app.post("/api/demo", tags=["Demo"])
async def demo_run(request: RunRequest, background_tasks: BackgroundTasks):
    """
    Same as /api/run but simulates 4 node transitions with delays (no real crew).
    Useful for UI testing without API keys.
    """
    from crew_runner import _jobs, JobStatusEnum, NodeStatus, NodeProgress, NODE_DEFS, _persist_job
    import uuid
    from datetime import datetime

    job_id = str(uuid.uuid4())

    nodes_init = [
        NodeProgress(node=n["node"], name=n["name"],
                     status=NodeStatus.pending, message="Waiting...").model_dump()
        for n in NODE_DEFS
    ]

    _jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatusEnum.queued,
        "request": request.model_dump(),
        "nodes": nodes_init,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "error": None,
        "result": None,
        "raw_output_lines": [],
    }

    async def _simulate(jid: str):
        job = _jobs[jid]
        node_delays = [4, 6, 5, 4]  # seconds per node
        for i, nd in enumerate(NODE_DEFS):
            job["status"] = JobStatusEnum.running
            updated = []
            for j, n2 in enumerate(NODE_DEFS):
                if j < i:
                    updated.append(NodeProgress(node=n2["node"], name=n2["name"],
                        status=NodeStatus.done, message=n2["done_msg"]).model_dump())
                elif j == i:
                    updated.append(NodeProgress(node=n2["node"], name=n2["name"],
                        status=NodeStatus.active, message=n2["active_msg"]).model_dump())
                else:
                    updated.append(NodeProgress(node=n2["node"], name=n2["name"],
                        status=NodeStatus.pending, message="Waiting...").model_dump())
            job["nodes"] = updated
            await asyncio.sleep(node_delays[i])

        # All done
        job["nodes"] = [
            NodeProgress(node=n["node"], name=n["name"],
                         status=NodeStatus.done, message=n["done_msg"]).model_dump()
            for n in NODE_DEFS
        ]
        job["status"] = JobStatusEnum.completed
        job["completed_at"] = datetime.utcnow().isoformat()
        demo_result = _make_demo_result(jid, request.model_dump())
        job["result"] = demo_result.model_dump()
        _persist_job(jid)

    background_tasks.add_task(_simulate, job_id)
    return RunResponse(job_id=job_id, message="Demo job started. Track via /api/status/" + job_id)


# ─────────────────────────────────────────────────────────────
# List all jobs
# ─────────────────────────────────────────────────────────────
@app.get("/api/jobs", response_model=list[JobListItem], tags=["Jobs"])
def get_jobs():
    return list_jobs()
