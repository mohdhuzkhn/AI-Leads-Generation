from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum


class Priority(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class OutreachReadiness(str, Enum):
    ready = "ready"
    needs_validation = "needs_validation"
    incomplete_data = "incomplete_data"


class RunRequest(BaseModel):
    location: str = Field(..., description="Target geography, e.g. 'Dubai, UAE'")
    industry: str = Field(..., description="Target sector, e.g. 'SaaS'")
    company_size: str = Field(..., description="Size filter, e.g. '11-50 employees'")
    limit: int = Field(default=5, ge=1, le=50, description="Max companies to find")
    target_persona: List[str] = Field(
        default=["CEO", "Founder"],
        description="Decision-maker titles to target"
    )


class JobStatusEnum(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class NodeStatus(str, Enum):
    pending = "pending"
    active = "active"
    done = "done"
    error = "error"


class NodeProgress(BaseModel):
    node: int
    name: str
    status: NodeStatus
    message: str = ""


class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum
    nodes: List[NodeProgress]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class ValidationScores(BaseModel):
    phone_validation_score: Optional[int] = None
    email_validation_score: Optional[int] = None
    linkedin_validation_score: Optional[int] = None
    overall_contact_score: Optional[int] = None


class ContactResult(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    contact_confidence: Optional[str] = None
    verification_status: Optional[str] = None
    validation_scores: Optional[ValidationScores] = None


class CompanyScores(BaseModel):
    company_fit_score: Optional[int] = None
    data_completeness_score: Optional[int] = None
    verification_confidence_score: Optional[int] = None
    overall_company_score: Optional[int] = None


class LeadResult(BaseModel):
    company_name: Optional[str] = None
    website_url: Optional[str] = None
    company_description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    contacts: List[ContactResult] = []
    company_scores: Optional[CompanyScores] = None
    lead_priority: Optional[str] = None
    priority_reasoning: Optional[str] = None
    outreach_readiness: Optional[str] = None
    quality_flags: List[str] = []
    recommended_contact_method: Optional[str] = None


class EmailDraft(BaseModel):
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    lead_name: Optional[str] = None
    company_name: Optional[str] = None


class GoogleSheetsOutput(BaseModel):
    spreadsheet_id: Optional[str] = None
    spreadsheet_url: Optional[str] = None
    total_rows_added: Optional[int] = None


class RunResult(BaseModel):
    job_id: str
    leads: List[LeadResult] = []
    email_drafts: List[EmailDraft] = []
    google_sheets: Optional[GoogleSheetsOutput] = None
    summary: Optional[dict] = None
    raw_output: Optional[str] = None


class RunResponse(BaseModel):
    job_id: str
    message: str


class JobListItem(BaseModel):
    job_id: str
    status: JobStatusEnum
    location: str
    industry: str
    limit: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    leads_found: int = 0
